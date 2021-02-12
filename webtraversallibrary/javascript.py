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
Wrapper functions around JavaScript code to be used from Selenium WebDriver. The main reason to store JS code in
files instead of embedding it in Python code is convenience: it is more readable and has better IDE support.
"""

import functools
import logging
import os
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Dict, Iterable, List, Union

from selenium.common.exceptions import (
    JavascriptException,
    NoAlertPresentException,
    UnexpectedAlertPresentException,
    WebDriverException,
)
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.remote.webdriver import WebDriver

from .color import Color
from .config import Config
from .error import WindowClosedError
from .geometry import Point, Rectangle
from .selector import Selector

logger = logging.getLogger("wtl")


def safe_selenium_method(func):
    """
    Handles errors thrown in the browser while executing javascript and outputs information to the log.
    Note: This is a clumsy decorator for instance methods and assumes there is a self.driver member.
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        def to_logger(msg, js_level):
            if js_level == "INFO":
                level = self.config.javascript.info
            elif js_level == "WARNING":
                level = self.config.javascript.warning
            elif js_level == "SEVERE":
                level = self.config.javascript.severe
            else:
                return
            if level == "debug":
                logger.debug(msg)
            elif level == "info":
                logger.info(msg)
            elif level == "warning":
                logger.warning(msg)
            elif level == "error":
                logger.error(msg)
            elif level == "critical":
                logger.critical(msg)

        alert_text = None
        try:
            return func(self, *args, **kwargs)
        except UnexpectedAlertPresentException:
            # Some websites create an alert to communicate an error message instead of throwing the normal exception
            # or instead of things normal people use popups for.
            # However, selenium can be "too quick" to dismiss the alerts and crash.
            alert = Alert(self.driver)
            try:
                alert_text = alert.text
                alert.dismiss()
            except NoAlertPresentException:
                pass
        except JavascriptException as e:
            logger.error("Exception thrown in the browser's Javascript engine.")
            logger.debug(e)
        finally:
            log_records = []
            try:
                log_records = self.driver.get_log("browser")
            except (WebDriverException, WindowClosedError):
                logger.warning("Failed to fetch log records from the driver")

            # Print browser logs
            for record in sorted(log_records, key=lambda x: int(x["timestamp"])):
                record["timestamp"] = datetime.fromtimestamp(record["timestamp"] / 1000).strftime("%H:%M")
                log_line = "[{level}] {message}".format(**record)
                log_level = record["level"]
                to_logger(log_line, log_level)

            # Then alert text, if there was any
            if alert_text is not None:
                logger.error(f"  JS Alert text:  {alert_text}")

    return wrapper


class JavascriptWrapper:
    """
    Helper class for executing built-in javascript scripts or custom
    files and snippets.
    """

    def __init__(self, driver: WebDriver, config: Config = None):
        assert driver
        config = config or Config.default()
        self.driver = driver
        self.config = config

    def save_mhtml(self, filename: str):
        """
        Executes the MHTML saving extension. Saves to the path specified in config.scraping.temp_path.
        Note: If the file already exists, it will not be overwritten.
        """
        self.execute_script('window.postMessage({type: "SAVE_MHTML", filename: "' + filename + '"})')

    def get_full_height(self) -> int:
        """
        Get the full page height, i.e. the height of the document.
        :return: document height in pixels
        """
        return self.execute_file(Path("get_full_page_height.js"))

    def find_iframe_name(self, identifier: str) -> str:
        """
        Looks for an iframe where name, ID, or class equals the identifier,
        and returns its name. Returns empty string if no matching object was found.
        :return: iframe name or empty string
        """
        return self.execute_file(Path("find_iframe_name.js"), identifier)

    def find_viewport(self) -> Rectangle:
        """
        Get the width of the web browser window with content.
        :return: viewport height in pixels
        """
        result = self.execute_file(Path("find_viewport.js"))

        if not result:
            logger.error("Failed to compute get viewport size")
            return Rectangle.empty()

        return Rectangle.from_list([result["x"], result["y"], result["x"] + result["w"], result["y"] + result["h"]])

    def get_element_metadata(self) -> List[Dict[str, Any]]:
        """
        Collects metadata about web page DOM elements: their tags, some of the HTML attributes, position and size on the
        page, CSS styles and classes, inner text.

        Each element on the page is assigned a unique within the scope of the page ``wtl_uid`` and
        has a pointer to the parent DOM element in the ``wtl_parent_uid`` field and are not to be confused
        with ``id`` attribute in HTML which is neither unique nor mandatory.

        :return: a list of JSON objects (in their Python dict form) with HTML attributes, additionally calculated
                properties and unique IDs. Refer to the script code for the keys' names.
        """
        return self.execute_file(Path("get_element_metadata.js"))

    def hide_position_fixed_elements(self, elements: List[str] = None) -> dict:
        """
        Hides page elements that are fixed or sticky (the ones that stay on the page when you scroll)
        by setting their visibility to "hidden".

        Returns a map from element ids (wtl-uid) to the old visibility values.

        Mutates the web page.
        """
        elements = elements or []
        return self.execute_file(Path("hide_position_fixed_elements.js"), elements)

    def show_position_fixed_elements(self, id_to_visibility: dict):
        """
        Set the specified visibility to the elements with ids listed in ``id_to_visibility``.

        The 2nd parameter is expected to be the (possibly accumulated) output of hide_position_fixed_elements.

        Mutates the web page (hopefully undoing the changes made by hide_position_fixed_elements)
        """

        self.execute_file(Path("show_position_fixed_elements.js"), id_to_visibility)

    def element_exists(self, selector: Selector) -> bool:
        """
        Returns True if an element exists, otherwise False.
        """

        return self.execute_file(Path("element_exists.js"), selector.css)

    def disable_animations(self):
        """
        Turns off animation on the page. Works for jQuery by setting a certain flag and for CSS animations by injecting
        an additional style into the page code.

        Mutates the web page.
        """
        self.execute_file(Path("disable_animations.js"))

    def is_page_loaded(self, *_) -> bool:
        """
        Applies some heuristics to check if the page is loaded. But since it is in general a hard question to answer,
        is known to be faulty in some cases.
        """
        # Ignores any input arguments given by WebDriverWait.until()
        return self.execute_file(Path("is_page_loaded.js"))

    def find_active_elements(self) -> list:
        """
        Uses a couple of heuristics to try and find all clickable elements in the page.
        """
        return self.execute_file(Path("find_active_elements.js"))

    def scroll_to(self, x: float, y: float):
        """
        Scroll the page to given coordinates.
        """
        self.execute_script(f"scrollTo({int(x)}, {int(y)});")

    def make_canvas(self):
        """
        Create viewport and page canvases and add them to the DOM.
        """
        self.execute_file(Path("make_canvas.js"))

    def annotate(
        self,
        location: Point,
        color: Color,
        size: int,
        text: str,
        background: Color = Color(0, 0, 0, 0),
        viewport: bool = False,
    ):
        """
        Writes text with a given color on the page.
        Shares an HTML canvas with `highlight`.
        """
        self.make_canvas()
        self.execute_file(
            Path("annotate.js"),
            location.x,
            location.y,
            color.to_str(),
            size,
            text,
            background.to_str(),
            background.a / 255,
            viewport,
        )

    def highlight(self, selector: Selector, color: Color, fill: bool = False, viewport: bool = False):
        """
        Highlight an element as found by a given selector with arbitrary
        color and intensity.
        Note: If more elements can be found, only one will be highlighted.
        Shares an HTML canvas with `annotate`.
        """
        self.make_canvas()
        self.execute_file(Path("highlight.js"), selector.css, color.to_str(), color.a / 255, fill, viewport)

    def clear_highlights(self, viewport: bool = False):
        """Removes all highlights created by :func:`highlight`."""
        self.execute_file(Path("clear_highlights.js"), viewport)

    def click_element(self, selector: Selector):
        """
        Clicks an element found by the given selector.
        Note: If more elements can be found, only one will be clicked.
        """
        self.execute_file([Path("dom.js"), Path("click_element.js")], selector.css)

    def delete_element(self, selector: Selector):
        """
        Deletes an element found by the given selector.
        Note: If more elements can be found, only one will be clicked.
        """
        self.execute_file(Path("delete_element.js"), selector.css)

    def fill_text(self, selector: Selector, value: str):
        """
        Fills an element as found by a given selector with given text.
        Note: If more elements can be found, only one will be used.
        """
        self.execute_file([Path("dom.js"), Path("fill_text.js")], selector.css, value)

    def select(self, selector: Selector, value: str):
        """
        Select an element of a dropdown (select) element.
        Note: If more elements can be found, only one will be used.
        """
        self.execute_file([Path("dom.js"), Path("select.js")], selector.css, value)

    @classmethod
    @functools.lru_cache(maxsize=32)
    def assemble_script(cls, filenames: Iterable[Path]) -> str:
        """
        Concatenates the contents of several Javascript files into one, with caching.
        :param filenames: Path to the JS files either in webtraversallibrary/js or an absolute path.
        """
        contents = []

        for filename in filenames:
            if not filename.exists():
                filename = Path(os.path.dirname(__file__)) / "js" / filename

            assert filename.exists() and filename.is_file()

            with open(filename, "rt", encoding="utf8") as f:
                contents.append(f.read())

        return "\n".join(contents)

    def execute_file(self, filename: Union[Path, Iterable[Path]], *args, execute_async: bool = False) -> Any:
        """
        Execute the JavaScript code in given file and return the result
        :param filename: Path to the JS file(s) either in webtraversallibrary/js or an absolute path.
        :param execute_async: if True, will wait until the javascript code has called
        arguments[arguments.length-1] and will return its input arguments.
        """
        if isinstance(filename, Path):
            filename = [filename]

        script = JavascriptWrapper.assemble_script(tuple(filename))

        if execute_async:
            return self.execute_script_async(script, *args)
        return self.execute_script(script, *args)

    @safe_selenium_method
    def execute_script(self, script: str, *args) -> Any:
        """
        Execute the JavaScript code in `script` and return the result
        :param script: path to the JS file relative to this package
        """
        return self.driver.execute_script(script, *args)

    @safe_selenium_method
    def execute_script_async(self, script: str, *args) -> Any:
        """
        Execute the JavaScript code in `script` asynchronously and returns the result
        :param script: path to the JS file relative to this package
        """
        return self.driver.execute_async_script(script, *args)
