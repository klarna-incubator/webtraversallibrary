# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
The Workflow is the main entry point for using the Web Traversal Library.
"""
from __future__ import annotations

import contextlib
import itertools
import logging
import os
from dataclasses import replace
from pathlib import Path
from time import sleep
from typing import Any, Callable, Dict, List, Union

from selenium import webdriver

from .actions import Abort, Action, Actions, ElementAction, Navigate, Refresh, Revert, Wait
from .classifiers import Classifier
from .color import Color
from .config import Config
from .error import Error
from .geometry import Point, Rectangle
from .goals import FOREVER
from .helpers import ClassifierCollection, FrameSwitcher, MonkeyPatches
from .javascript import JavascriptWrapper
from .logging import setup_logging
from .processtools import TimeoutContext
from .scraper import Scraper
from .selector import Selector
from .snapshot import PageElement, PageSnapshot
from .view import View
from .window import Window

logger = logging.getLogger("wtl")


class Workflow:
    """
    The Workflow is the main entry point for using the Web Traversal Library.
    It will handle setup and teardown of all helper classes and appropriate use of the configuration object.
    Note that you can "run a workflow" manually by creating Window and Scraper objects manually,
    however this is not recommended for general use.
    """

    SINGLE_TAB: str = "tab"

    def __init__(
        self,
        url: Union[str, Dict[str, str], Dict[str, Dict[str, str]]],
        policy: Callable,
        output: Path = None,
        config: Config = None,
        goal: Callable = FOREVER,
        classifiers: List[Classifier] = None,
        patches: Dict[Selector, str] = None,
    ):
        """
        Create a Workflow and reset it.
        :param url: Single string, dict mapping tab name to URL, or dict mapping window name to tab: url dict. Each
        tab name must be unique, even among different windows!
        :param policy: Function taking workflow and views, returning an action or a list of actions per tab/view.
        :param output: Path for storing local data (if needed).
        :param config: Configuration object for this instance.
        :param goal: Called before each policy call, will halt the workflow if it returns True.
        :param classifiers: List of classifiers to run on every snapshots.
        :param patches: A dictionary of selectors to monkeypatch to other destinations.
        """
        setup_logging(log_dir=output if config.debug.save else None)
        config = config or Config.default()
        config.validate()

        self.loop_idx = -1
        self.output = output
        self.config = config
        self._windows: Dict[str, Window] = {}
        self.policy = policy() if policy.__name__ == "__wtl_wrapped" else policy
        self.goal = goal if goal else FOREVER
        self.preload_callbacks: List[Path] = []
        self.postload_callbacks: List[Callable] = []
        self._history: Dict[str, List[View]] = {}
        self._current_tab: str = None
        self._current_window: Window = None
        self._has_quit = False
        self._tabs_cache: List[str] = None
        self.metadata: Dict[Any, Any] = {}
        self.monkeypatches = MonkeyPatches(patches)
        self.classifiers = ClassifierCollection(classifiers)
        self.previous_policy_result = None

        # Basic error handling
        assert self.policy, "Workflow created without a policy!"
        if self.config.debug.save:
            assert self.output, "Saving debug output requires specifying an output path!"

        # Setup starting points
        if isinstance(url, str):
            # Convert url type from str to Dict[str, str]
            url = {Workflow.SINGLE_TAB: url}
        if isinstance(list(url.values())[0], str):
            # Convert url type from Dict[str, str] to Dict[str, Dict[str, str]]]
            url = {Workflow.SINGLE_TAB: url}  # type: ignore
        self._starting_url: Dict[str, Dict[str, str]] = url  # type: ignore

        self.reset()

    def __enter__(self):
        return self

    def __exit__(self, *_, **__):
        """Calls :func:`quit` unless debug.preserve_window in config is True."""
        if not self.config.debug.preserve_window:
            self.quit()

    @Error.wrapped
    def run(self):
        """
        Runs the workflow loop!
        Intializes the tabs to the starting URLs and then
        calls :func:`run_once` in a loop until the goal function returns True
        or all tabs have stopped.
        """
        assert not self._has_quit
        if self.classifiers:
            self.preload_callbacks.append(Path("js/intercept_event_listeners.js"))

        try:
            ctx = TimeoutContext(n_seconds=self.config.timeout) if self.config.timeout else contextlib.nullcontext()
            with ctx:
                while self.success:
                    if self.run_once():
                        break

        except TimeoutError:
            logger.error("Workflow.run() timed out!")

        logger.debug("Workflow.run() completed!")

    @Error.wrapped
    def run_once(self):
        """
        Runs a single iteration of the WTL flow, i.e. snapshots, runs classifiers,
        checks goal, computes actions, calls policy, executes actions.
        Check `loop_idx` member attribute for number of iterations.

        .. note::
            This does not initialize the tabs to their starting URLs. Normally, use :func:`run` instead.

        :return: The boolean output from the goal function.
        """
        self._populate_tabs_cache()

        # Perform required snapshotting
        self.loop_idx += 1
        all_views = self._get_new_views()

        # Stop iterating if we've reached our goal
        goal_result = self.goal(self, all_views)
        if isinstance(goal_result, dict):
            goal_result = goal_result and all(goal_result.values())

        if not goal_result:
            # Query the policy
            try:
                policy_result = self.policy(self, all_views)
                self.previous_policy_result = policy_result
                policy_stopped = False
            except StopIteration:
                logger.info("Received StopIteration from policy, will not continue.")
                policy_stopped = True

            # Execute actions
            if not policy_stopped:
                self._execute_policy_result(policy_result)

        # Save snapshot to disk
        if self.config.debug.save:
            for tab in self.tabs:
                self.tab(tab)
                try:
                    if self.latest_view.snapshot:
                        self.latest_view.snapshot.save(self.output_path)
                except IndexError:
                    pass

        # Stop iterating if goal returned True
        if goal_result:
            return True

        # Abort all remaining tabs if policy is finished
        if policy_stopped:
            self._execute_policy_result({tab: Abort() for tab in self.open_tabs})

        # Reduce memory usage if keeping a lot of views
        if self.config.scraping.history and not self.config.scraping.full_history:
            for tab in self.open_tabs:
                self.tab(tab)
                self.history[-1] = self.history[-1].copy(no_snapshot=True)

        # Continue if there is still something in the policy
        return policy_stopped

    def _get_new_views(self) -> Dict[str, View]:
        all_views: Dict[str, View] = {tab: None for tab in self.tabs}

        for tab in self.open_tabs:
            self.tab(tab)

            # Navigate if neccessary
            initial_url = self.current_window.navigation
            initial_action = None
            if initial_url:
                initial_action = Navigate(initial_url)
                self._perform_action(initial_action)

            # Optimization: Only scrape tab if enforced, action taken, or never scraped before
            sh = self.history
            if (
                not self.config.scraping.all
                and self.previous_policy_result
                and tab not in self.previous_policy_result
                and sh[-1]
                and sh[-1].snapshot
            ):
                self.history.append(sh)
                all_views[tab] = sh[-1]
                continue

            # Store View
            all_views[tab] = self._get_new_view(tab, initial_action)

        return all_views

    def _get_new_view(self, name: str, initial_action: Action) -> View:
        # Run postload callbacks
        for cb in self.current_window.scraper.postload_callbacks:
            cb()

        # Scrape the page
        snapshot = self.current_window.scraper.scrape_current_page()

        # Assemble basic list of actions
        action_list: List[Action] = [Abort(), Refresh(), Navigate(), Wait()]
        action_list += [Revert(step) for step in range(len(self.history))]
        actions = Actions(action_list)

        # Setup metadata
        metadata: Dict[str, Any] = {}
        if self.config.scraping.history:
            if self.history and "next_action" in self.history[self.loop_idx - 1].metadata:
                metadata = self.history[self.loop_idx - 1].metadata.copy()
                metadata["previous_action"] = metadata["next_action"]
            else:
                metadata["previous_action"] = [initial_action]
        metadata["next_action"] = None

        # Create view
        view = View(name=name, snapshot=snapshot, actions=actions, metadata=metadata)

        # Add state to history
        if self.loop_idx < len(self.history):
            self.history[self.loop_idx] = view
        else:
            self.history.append(view)

        # Maintain only one level of history if required
        ct = self.current_tab
        if not self.config.scraping.history:
            for i in range(len(self._history[ct]) - 1):
                self._history[ct][i] = None

        # Run element classifiers
        view.actions.extend(self._run_element_classifiers(snapshot))

        # Run page classifiers
        for classifier in self.classifiers.active_view_classifiers:
            result = classifier.callback(view)
            view.tags.update(result)

        return view

    def _execute_policy_result(self, policy_result: Dict[str, Union[Action, List[Action]]]):
        # If a reset action was given, perform it directly
        revert_actions = [a for a in policy_result.values() if isinstance(a, Revert)]

        revert_actions.sort(key=lambda a: a.view_index)
        if revert_actions:
            self._perform_action(revert_actions[0])
            return

        # Execute other actions in the policy result
        for tab in self.open_tabs:
            # Find corresponding actions
            if tab in policy_result:
                actions = policy_result[tab]
            else:
                keys = [r for r in policy_result if isinstance(r, View) and r.name == tab]
                if not keys:
                    logger.info(f"No action given for {tab}.")
                    actions = []
                else:
                    actions = policy_result[keys[0]]

            # Execute actions
            if not isinstance(actions, list):
                actions = [actions]

            if actions:
                self.tab(tab)

            for i, action in enumerate(actions):
                sleep(self.config.scraping.wait_action)

                if (
                    isinstance(action, ElementAction)
                    and isinstance(action.target, Selector)
                    and not action.target.iframe
                ):
                    action = action.transformed_to_element(self.latest_view.snapshot.elements)
                    actions[i] = action
                self._perform_action(action)

            self.latest_view.metadata["next_action"] = actions

    def create_window(self, name: str) -> Window:
        """Opens a new browser window and adds it to this workflow. Returns the new window."""
        window = Window(
            config=self.config, preload_callbacks=self.preload_callbacks, postload_callbacks=self.postload_callbacks
        )
        self._windows[name] = window
        return window

    @property
    def current_tab(self) -> str:
        """Returns the name of the current tab"""
        return self._current_tab

    @property
    def current_window(self) -> Window:
        """Returns the window object for the current tab."""
        return self._current_window

    @property
    def success(self) -> bool:
        """Returns True if there are any open (i.e. not-cancelled) tabs."""
        return any(window.open_tabs for window in self.windows)

    @property
    def tabs(self) -> List[str]:
        """Returns a list of all tab names."""
        return self._tabs_cache

    @property
    def open_tabs(self):
        """Returns a list of all open tab names."""
        return list(itertools.chain.from_iterable(window.open_tabs for window in self.windows))

    @property
    def windows(self):
        """Returns a list of all window instances."""
        return list(self._windows.values())

    @property
    def history(self) -> List[View]:
        """
        Returns a history of views for the current tab.
        The view stores previous_action and next_action in its metadata for future
        resurrection of the workflow.
        """
        ct = self.current_tab
        if ct not in self._history:
            self._history[ct] = []
            for _ in range(self.loop_idx + 1):
                self._history[ct].append(View(name=ct, snapshot=None))
        return self._history[ct]

    @property
    def aborted(self) -> bool:
        """Returns True if the current tab has been closed."""
        return self.current_window.is_closed(self.current_tab)

    @property
    def js(self) -> JavascriptWrapper:
        """Returns a :class:`JavascriptWrapper` associated to the current window."""
        return self.current_window.js

    @property
    def driver(self) -> webdriver:
        """Returns the WebDriver instance associated to the current window."""
        return self.current_window.driver

    @property
    def scraper(self) -> Scraper:
        """Provides a :class:`Scraper` instance associated to the current window."""
        return self.current_window.scraper

    @property
    def latest_view(self) -> View:
        """Returns the latest :class:`View` taken from the current tab."""
        return self.history[self.loop_idx]

    @property
    def output_path(self) -> Path:
        """Returns path to output directory for current tab and iteration"""
        assert self.output, "No output path was specified!"
        output_path = self.output / str(self.loop_idx)
        if len(self.tabs) > 1:
            output_path = output_path / self.current_tab
        return output_path

    @property
    def post_processing_output_path(self) -> Path:
        """
        Returns path to output directory for post processing output.
        The Workflow does not put anything here itself by default, but this is provided as
        convenience to the user.
        """
        assert self.output, "No output path was specified!"
        output_path = self.output / "post"
        os.makedirs(output_path, exist_ok=True)
        return output_path

    def tab(self, name: str) -> Workflow:
        """Sets the current tab to the given name."""
        if len(self.tabs) > 1 and self._current_tab != name:
            logger.info(f"> Setting tab: {name}...")
        self._current_tab = name
        for window in self.windows:
            if self._current_tab in window.tabs:
                self._current_window = window
                break
        self._current_window.set_tab(name)
        return self

    def window(self, name: str):
        """Returns the window instance with the name provided when created with :func:`create_window`."""
        return self._windows[name]

    def view(self, view: View) -> Workflow:
        """Sets the current tab to the one where given view was taken from."""
        return self.tab(view.name)

    def quit(self):
        """Cleans up all windows. Call this after you are done! Do not use again after this."""
        self._has_quit = True
        for window in self.windows:
            window.quit()

    def frame(self, identifier: str) -> FrameSwitcher:
        """
        Returns a context manager for entering and exiting iframes.
        See `FrameSwitcher` for more details.
        """
        return FrameSwitcher(identifier, self.js, self.driver)

    def _perform_action(self, action: Action):
        if not action:
            logger.warning("None given as action")
            return

        logger.debug(f"Next action: {action}")

        try:
            if isinstance(action, ElementAction):
                has_element_handle = isinstance(action.target, PageElement)
                if (
                    self.config.debug.autoscroll
                    and has_element_handle
                    and (self.config.debug.screenshots or not self.config.browser.headless)
                ):
                    self.smart_scroll_to(action.target.bounds)  # type: ignore

                if self.config.debug.save and self.config.debug.screenshots and has_element_handle:
                    index = 1 + len([s for s in self.latest_view.snapshot.screenshots if s.startswith("action")])
                    name = f"action{index}"
                    assert name not in self.latest_view.snapshot.screenshots

                    scr = self.scraper.capture_screenshot("action")
                    viewport = self.js.find_viewport()
                    scr.highlight(
                        action.target.bounds - viewport.minima,  # type: ignore
                        Color(255, 0, 0),
                        f"Action: {action.__class__.__name__}",
                    )
                    self.latest_view.snapshot.screenshots[name] = scr

                if self.config.debug.live:
                    self.js.highlight(action.selector, Color.from_str(self.config.debug.action_highlight_color))
                    if not self.config.browser.headless:
                        sleep(self.config.debug.live_delay)

                if has_element_handle:
                    patch = self.monkeypatches.check(action.target.page, action.target)  # type: ignore
                    if patch:
                        action = Navigate(patch)
                        logger.info(f"Action monkeypatched: {action}")

            action.execute(self)
        except NotImplementedError as e:
            logger.error(e)

    def smart_scroll_to(self, element: Rectangle):
        """
        Uses js.scroll_to in a slightly smarter way to minimize
        required scrolls and vertically center elements of interest.
        """
        viewport = self.js.find_viewport()
        y = None

        if element in viewport:
            # Element is completely visible already, do nothing
            pass

        elif element.height > viewport.height:
            # Element is larger than viewport, fit as much as possible
            y = element.y

        elif element.y < viewport.y:
            # Element requires scrolling up, make sure it's inside the screen
            y = element.y

        elif element.y + element.height > viewport.y + viewport.height:
            # Element requires scrolling down, try centering it
            y = element.y + element.height / 2 - viewport.height / 2

        if y is not None:
            self.js.scroll_to(viewport.x, y)
            sleep(self.config.scraping.wait_scroll)

    def _run_element_classifiers(self, snapshot: PageSnapshot) -> List[Action]:
        action_list: List[Action] = []

        for classifier in self.classifiers.active_element_classifiers:
            subset = snapshot.elements.by_score(classifier.subset)
            results = classifier.callback(subset, self)

            if not results:
                continue

            if not isinstance(results, dict):
                results = {"": results}

            for cls_name, cls_result in results.items():
                action_list.extend(self._process_class(classifier, cls_name, cls_result, subset, snapshot))

        return action_list

    def _populate_tabs_cache(self):
        """Updates the cache used by self.tabs property"""
        self._tabs_cache = list(itertools.chain.from_iterable(window.tabs for window in self.windows))

    def _process_class(self, classifier, cls_name, cls_result, subset, snapshot) -> List[Action]:
        # Add the classifier name as the prefix on multi-class predictions
        cls_name = f"{classifier.name}__{cls_name}" if cls_name else classifier.name

        binary_filter = isinstance(cls_result[0], PageElement) if cls_result else True

        if binary_filter:
            cls_result = [(e, 1.0 if e in cls_result else 0.0) for e in subset]

        cls_result.sort(key=lambda x: x[1], reverse=True)

        if binary_filter:
            scaled_result = [value[1] for value in cls_result]
        else:
            scaled_result = classifier.mode.scale([r[1] for r in cls_result])

        cls_result = [(e, r, s) for (e, r), s in zip(cls_result, scaled_result)]

        for element, raw_score, score in cls_result:
            element.raw_scores[cls_name] = raw_score
            element.metadata[cls_name] = classifier.result_type(score)

        if classifier.highlight:
            self._highlight_classifier_result(classifier, cls_name, cls_result, snapshot)

        if classifier.action:
            return [classifier.action(element) for element, _, score in cls_result if score]

        return []

    def reset(self):
        """
        Resets the workflow.
        Does not clear any history.
        """
        assert self.config.scraping.history or self.loop_idx == -1, "Cannot reset if config.scraping.history is False!"

        self.loop_idx = -1
        self.previous_policy_result = None

        # Clear any existing windows
        for window in self.windows:
            if window:
                window.quit()
        self._windows.clear()

        # Create all windows and tabs
        for window_name, tab_names in self._starting_url.items():
            window = self.create_window(window_name)
            for tab_name, url in tab_names.items():
                window.create_tab(tab_name, url=url)
        self._populate_tabs_cache()
        self.tab(self.tabs[0])

    def reset_to(self, view_index: int):
        """
        Resets the Workflow and replays the first ``view_index`` actions.
        History in memory will be mutated.
        Because this resets the `loop_idx` variable to match, saved output will override
        previous output.
        """
        assert self.config.scraping.history, "Cannot reset if config.scraping.history set to False!"
        assert 0 <= view_index < self.loop_idx, "Cannot revert into the future or before the beginning of time!"
        self.reset()
        self.loop_idx = view_index

        for tab in self.tabs:
            self._history[tab] = self._history[tab][: view_index + 1]

        for i in range(view_index + 1):
            logger.info(f"Replaying index {i}...")
            policy_result = {tab: self.tab(tab).history[i].metadata["previous_action"] for tab in self.tabs}
            self._execute_policy_result(policy_result)
            self._get_new_views()

    def _highlight_classifier_result(self, classifier, title, result, snapshot):
        # Given a classifier and its output, call highlighting accordingly.
        # Takes a list of tuples (element, raw_score, score).
        # Highlights according to the scaled score.

        do_screenshots = self.config.debug.screenshots
        if do_screenshots:
            scr = snapshot.new_screenshot(name=classifier.name, of="full")

        def _highlight(index):
            element = result[index][0]
            raw_score = result[index][1]
            score = result[index][2]

            if not score:
                return

            color = replace(classifier.highlight_color, a=int(score * 255))
            self.js.highlight(element.selector, color)
            score_str = f"{score:.2f} " + (f"({raw_score:.2f})" if isinstance(raw_score, float) else f"({raw_score})")

            if self.config.debug.live_annotation:
                self.js.annotate(
                    Point(element.bounds.x + 1, element.bounds.y + element.bounds.height + 10),
                    color,
                    10,
                    f"{title}: {score_str}",
                )

            if do_screenshots:
                scr.highlight(element.bounds, color, text=score_str)

        if isinstance(classifier.highlight, bool):
            for index in range(len(result)):
                _highlight(index)
        elif isinstance(classifier.highlight, int):
            for index in range(min(classifier.highlight, len(result))):
                _highlight(index)
        elif isinstance(classifier.highlight, float):
            for index, entry in enumerate(result):
                if entry[2] > classifier.highlight:
                    _highlight(index)
        else:
            logger.error(f"Invalid classifier.highlight value in {classifier}")
