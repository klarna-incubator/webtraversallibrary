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
An action is an abstraction of some website or browser interaction,
often implemented as a javascript snippet or webdriver API execution applicable for a given view.

Action instances can be incomplete, i.e. they are not initialized with all fields. Call them with
the missing attributes to replace those.
"""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, replace
from time import sleep
from typing import Union

from .color import Color
from .geometry import Point
from .selector import Selector
from .snapshot import Elements, PageElement


@dataclass(frozen=True)
class Action(ABC):
    """
    Base class for all actions. Do not use, refer
    instead to :class:`ElementAction` or :class:`PageAction`.

    Each action must provide an ``execute`` method that performs the required logic.
    """

    def execute(self, workflow):
        pass

    def __call__(self, *args, **kwargs):
        if not args:
            return replace(self, **kwargs)

        # If there is only one non-target element, use the positional argument for that
        assert len(args) == 1
        fields = [x for x in self.__dataclass_fields__ if x != "target"]  # pylint: disable=no-member
        assert len(fields) == 1, "Ambiguous action specialiation, use keyword arguments!"
        return replace(self, **{fields[0]: args[0]})


class Actions(list):
    """Helper class for a list of actions"""

    def by_type(self, tag: type) -> Actions:
        """Returns all actions of the given type."""
        return Actions([action for action in self if isinstance(action, tag)])

    def by_score(self, name: str, limit: float = 0.0) -> Actions:
        """Returns all actions with the given score (metadata entry) greater than the given limit."""
        return Actions(
            [
                action
                for action in self
                if isinstance(action, ElementAction)
                and name in action.target.metadata  # type: ignore
                and action.target.metadata[name] > limit  # type: ignore
            ]
        )

    def by_raw_score(self, name: str, limit: float = 0.0) -> Actions:
        """
        Returns all actions with the given raw score (output from a classifier before scaling)
        greater than the given limit.
        """
        return Actions(
            [
                action
                for action in self
                if isinstance(action, ElementAction)
                and name in action.target.raw_scores  # type: ignore
                and action.target.raw_scores[name] > limit  # type: ignore
            ]
        )

    def by_element(self, element: PageElement) -> Actions:
        """Returns all actions (ElementAction) that act upon the given element."""
        return Actions([action for action in self if isinstance(action, ElementAction) and action.target == element])

    def by_selector(self, selector: Selector) -> Actions:
        """
        Queries the page by the given selector. If at least one element is found,
        return all elements equal to one of those.
        """
        if not self:
            return Actions([])

        element_actions = self.by_type(ElementAction)
        if not element_actions:
            return Actions([])

        tags = set(element_actions[0].target.page.page_source.html.select(selector.css))
        if not tags:
            return Actions([])

        wtl_uids = set(int(x.attrs["wtl-uid"]) for x in tags if "wtl-uid" in x.attrs)
        actions = Actions([action for action in element_actions if action.target.wtl_uid in wtl_uids])

        # Falls back on BS4 tags if selector matches something that hasn't been snapshotted yet
        if not actions:
            actions = Actions([action for action in element_actions if action.target.tag in tags])

        return actions

    def sort_by(self, name: str = None, reverse: bool = False) -> Actions:
        """
        Sorts by a certain action (raw) score. If given name does not exist the element gets (raw) score 0.
        """
        self.sort(key=lambda action: action.target.raw_scores.get(name, 0), reverse=reverse)
        return self

    def unique(self) -> Action:
        """Checks if exactly one element exists, if so returns it. Throws AssertionError otherwise"""
        assert len(self) == 1
        return self[0]


@dataclass(frozen=True)
class ElementAction(Action):
    """
    Base class for all actions that execute on a specific element.
    Can be initialised with a :class:`PageElement` or a css selector string.
    """

    target: Union[PageElement, Selector] = None

    def transformed_to_element(self, elements: Elements) -> ElementAction:
        """Modifies this action with a PageElement corresponding to the stored selector"""
        assert isinstance(self.target, Selector)
        selector = self.target
        tags = elements.by_selector(selector)
        assert tags, f"Failed to perform {self.__class__.__name__}: Selector '{selector.css}' matches no tags"
        page_element = replace(tags[0])
        object.__setattr__(page_element, "selector", selector)
        return replace(self, target=page_element)

    @property
    def selector(self) -> Selector:
        return self.target if isinstance(self.target, Selector) else self.target.selector


@dataclass(frozen=True)
class PageAction(Action):
    """
    Base class for all actions that do not execute on a specific element.
    """


@dataclass(frozen=True)
class Click(ElementAction):
    """
    Simulates a click on the contained element.
    If it isn't clickable, nothing happens.
    """

    def execute(self, workflow):
        with workflow.frame(self.selector.iframe):
            workflow.js.click_element(self.selector)


@dataclass(frozen=True)
class FillText(ElementAction):
    """
    Fills a string by setting the text value in the contained element.
    If it isn't a text field, anything can happen.
    """

    text: str = ""

    def execute(self, workflow):
        with workflow.frame(self.selector.iframe):
            workflow.js.fill_text(self.selector, self.text)


@dataclass(frozen=True)
class Select(ElementAction):
    """
    Selects the given value on a <select> dropdown element.
    If it isn't a select element, anything can happen.
    """

    value: str = ""

    def execute(self, workflow):
        with workflow.frame(self.selector.iframe):
            workflow.js.select(self.selector, self.value)


@dataclass(frozen=True)
class ScrollTo(ElementAction):
    """
    Scrolls the current page to center the given element vertically.
    """

    def execute(self, workflow):
        workflow.smart_scroll_to(self.target.bounds)


@dataclass(frozen=True)
class Highlight(ElementAction):
    """
    Highlights an element by calling workflow.js.highlight(...)
    viewport refers to drawing on a floating viewport-sized canvas. If None, uses default value from config.
    """

    color: Color = Color.from_str("#FFB3C7")
    fill: bool = False
    viewport: bool = None

    def execute(self, workflow):
        viewport = workflow.config.debug.default_canvas_viewport if self.viewport is None else self.viewport
        workflow.js.highlight(selector=self.selector, color=self.color, fill=self.fill, viewport=viewport)


@dataclass(frozen=True)
class Remove(ElementAction):
    """Removes the given element from the DOM."""

    def execute(self, workflow):
        workflow.js.delete_element(self.selector)


@dataclass(frozen=True)
class Annotate(PageAction):
    """
    Writes text on a given page by calling workflow.js.annotate(...).
    viewport refers to drawing on a viewport canvas. If None, uses default value from config.
    """

    location: Point
    color: Color
    size: int
    text: str
    background: Color = Color(0, 0, 0, 0)
    viewport: bool = None

    def execute(self, workflow):
        viewport = workflow.config.debug.default_canvas_viewport if self.viewport is None else self.viewport

        workflow.js.annotate(
            location=self.location,
            color=self.color,
            size=self.size,
            text=self.text,
            background=self.background,
            viewport=viewport,
        )


@dataclass(frozen=True)
class Clear(PageAction):
    """
    Clears all highlights and annotations.
    viewport refers to drawing on a floating viewport-sized canvas. If None, uses default value from config.
    """

    viewport: bool = None

    def execute(self, workflow):
        viewport = workflow.config.debug.default_canvas_viewport if self.viewport is None else self.viewport
        workflow.js.clear_highlights(viewport=viewport)


@dataclass(frozen=True)
class Navigate(PageAction):
    """
    Navigates to a new URL and waits for the page to load.
    If the URL is invalid, you may end up on the browser's error page.
    """

    url: str = ""

    def execute(self, workflow):
        workflow.scraper.navigate(self.url)


@dataclass(frozen=True)
class Revert(PageAction):
    """
    Reverts the state of the Workflow to a previous point in time.
    In effect, resets the underlying web driver and then replays all actions leading up
    to the given view_index. If 0, just perform the initial action of :class:`Navigate`
    to the initial URL.
    """

    view_index: int = 0

    def execute(self, workflow):
        workflow.reset_to(self.view_index)


@dataclass(frozen=True)
class Wait(PageAction):
    """
    Calls :func:`time.sleep` with the given seconds argument.
    """

    seconds: float = 0

    def execute(self, _):
        sleep(self.seconds)


@dataclass(frozen=True)
class WaitForElement(PageAction):
    """
    Checks to see if element at given selector exists on the page.
    Keeps trying indefinitely with a given interval until it succeeds.
    """

    selector: Selector
    seconds: float = 1.0

    def execute(self, workflow):
        while not workflow.js.element_exists(self.selector):
            sleep(self.seconds)


@dataclass(frozen=True)
class WaitForUser(PageAction):
    """
    Waits until the Enter key is pressed in the terminal.
    """

    def execute(self, _):
        _ = input("Click [Enter] to continue...")


@dataclass(frozen=True)
class Refresh(PageAction):
    """
    Triggers a refresh of the current page.
    Note that the following snapshot may not have wtl_uid that
    map equally to the previous state.
    """

    def execute(self, workflow):
        workflow.scraper.refresh()


@dataclass(frozen=True)
class Abort(PageAction):
    """
    Stops any future progress on this tab and will set an aborted flag
    on the given tab. The tab will not be snapshoted in the future.
    If all tabs have received an Abort call, the workflow will stop.
    Note! If you're using multiple tabs, this action has highest priority.
    """

    def execute(self, workflow):
        if workflow.config.actions.abort.close and not workflow.config.debug.preserve_window:
            workflow.current_window.close_tab()
