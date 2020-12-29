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

"""Abstraction layer for interactions with a browser instance."""
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Set

from selenium.common.exceptions import JavascriptException, UnexpectedAlertPresentException, WebDriverException

from .config import Config
from .error import WindowClosedError
from .javascript import JavascriptWrapper
from .logging import logging
from .scraper import Scraper
from .webdrivers import setup_driver

logger = logging.getLogger("wtl")


class Window:
    """
    Owns a webdriver, scraper and javascript wrapper.
    Handles browser instance logic.
    """

    def __init__(
        self, config: Config, preload_callbacks: Iterable[Path] = None, postload_callbacks: List[Callable] = None
    ):
        self._driver = setup_driver(config, preload_callbacks=preload_callbacks)
        self.scraper = Scraper(driver=self.driver, config=config, postload_callbacks=postload_callbacks)
        self.js = JavascriptWrapper(self.driver, config)
        self.name_to_handle: Dict[str, int] = {}
        self.closed: Set[str] = set()
        self.current: str = None
        self.tab_navigation: Dict[str, str] = {}

    def ensure_running(self):
        """
        Tries fetching attached window handles.
        Raises WindowClosedError if this fails.
        """
        try:
            assert self._driver
            _ = self._driver.window_handles
        except (AssertionError, WebDriverException) as e:
            raise WindowClosedError("Could not reach the browser window!") from e

    @property
    def driver(self):
        """Checks if the driver is attached, and if so returns a reference to it."""
        self.ensure_running()
        return self._driver

    def is_closed(self, tab):
        """Returns True if the tab has been closed"""
        return tab in self.closed

    @property
    def tabs(self):
        """Returns a list of all tab names"""
        return list(self.name_to_handle.keys())

    @property
    def open_tabs(self):
        """Returns a list of all open tab names"""
        return [tab for tab in self.tabs if not self.is_closed(tab)]

    @property
    def navigation(self):
        """
        Returns URL to navigate to for the current active tab, if it exists.
        Removes the entry afterwards, to two subsequent calls need not be equal.
        """
        if self.current not in self.tab_navigation:
            return None

        result = self.tab_navigation[self.current]
        del self.tab_navigation[self.current]
        return result

    @property
    def cookies(self) -> List[Any]:
        return self.driver.get_cookies()

    @cookies.setter
    def cookies(self, value: Iterable[Any]):
        """Replaces(!) all existing cookies with the given list."""
        self.driver.delete_all_cookies()
        for cookie in value:
            self.driver.add_cookie(cookie)

    def create_tab(self, name: str, url: str = "about:blank"):
        """
        Open a new tab with a given `name` (must be unique for this Window).
        If `url` argument is given, saves this value that can be retrieved using the
        :func:`navigation` method later. The tab will not automatically navigate
        to the given adress. Use a :class:`Scraper` or interact directly with the driver.
        """
        assert self.driver, "Cannot interact with window after calling quit!"
        assert name not in self.closed, "Cannot reopen a closed tab!"

        # Every window comes with one tab, reuse if possible
        if len(self.name_to_handle) > 0:
            self.js.execute_script("window.open('about:blank');")

        # Get mapping of the new tab and store in the dict
        for _tab in self.driver.window_handles:
            if _tab not in self.name_to_handle.values():
                self.name_to_handle[name] = _tab

        # Remember navigation
        if url != "about:blank":
            self.tab_navigation[name] = url

    def set_tab(self, name: str):
        """
        Sets the current active tab to the one listed under the given `name`.
        Throws AssertionError if no such tab exists.

        .. warning::
            If the tab has been closed, interactions may lead to weird behaviour.
        """
        assert name in self.name_to_handle, f"No such tab exists: {name}"
        self.current = name

        if name in self.closed:
            logger.warning("This tab has been closed. Do not interact with it.")
        else:
            self.driver.switch_to.window(self.name_to_handle[name])

    def close_tab(self):
        """Closes the current active tab."""
        assert self.current not in self.closed, "Closing already closed tab!"
        self.closed.add(self.current)
        try:
            self.driver.close()
        except (UnexpectedAlertPresentException, JavascriptException, WebDriverException, WindowClosedError):
            logger.warning("Attempting to close failed - window probably already closed.")

    def quit(self):
        """
        Terminates the browser and associated driver of this instance.
        Do not use this window afterwards.
        """
        if not self._driver:
            return

        try:
            for tab in self.open_tabs:
                self.set_tab(tab)
                self.close_tab()
            self._driver.quit()
        except WindowClosedError:
            logger.warning("Attempting to close already closed window.")
        finally:
            self._driver = None
