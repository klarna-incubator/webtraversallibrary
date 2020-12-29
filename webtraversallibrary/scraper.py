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
Module for scraping a website and saving contents to file.
"""

import logging
import os.path
from datetime import datetime
from pathlib import Path
from time import sleep
from typing import Callable, Dict, List

import bs4
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from urllib3.util import parse_url

from .config import Config
from .javascript import JavascriptWrapper
from .processtools import TimeoutContext
from .screenshot import Screenshot
from .snapshot import PageSnapshot
from .version import __version__

logger = logging.getLogger("wtl")


class Scraper:
    """
    Used to create web page snapshots using a WebDriver instance.
    """

    def __init__(
        self, driver: WebDriver, config: Config, hide_sticky: bool = True, postload_callbacks: List[Callable] = None
    ):
        self.driver = driver
        self.config = config
        self.hide_sticky = hide_sticky
        self.js = JavascriptWrapper(self.driver, config)
        self.postload_callbacks = postload_callbacks
        self.device_pixel_ratio = self.js.execute_script("return window.devicePixelRatio;") or 1.0

    def scrape_current_page(self) -> PageSnapshot:
        """
        Scrape the page currently open in the driver,
        """
        attempts = self.config.scraping.attempts
        if attempts < 1:
            logger.warning("config.scraping.attempts is set to 0, no snapshot will be made!")

        snapshot = None
        while attempts > 0:
            try:
                attempts -= 1
                snapshot = self._create_snapshot()
                break
            except WebDriverException as e:
                logger.error(e)
                if attempts <= 0:
                    raise

            logger.warning("Scraping failed, reloading the page and trying again...")

            while attempts > 0:
                sleep(1.0)

                try:
                    self.refresh()
                    break
                except WebDriverException as e:
                    attempts -= 1
                    logger.error(e)
                    if attempts <= 0:
                        raise

        return snapshot

    def refresh(self):
        """
        Triggers a refresh of the page.
        Blocks until page is loaded.
        """
        self.driver.refresh()
        if self.config.scraping.disable_animations:
            self.js.disable_animations()
        self.wait_until_loaded()

    def navigate(self, url: str):
        """
        Navigate the scraper's internal webdriver to the URL.
        Blocks until page is loaded.
        """
        try:
            if parse_url(url).scheme is None:
                url = "http://" + url
            self.driver.get(url)
        except TimeoutException:
            raise TimeoutError(f"WebDriver page load timed out on url '{url}'")
        except WebDriverException:
            logger.error(f"URL not valid: {url}")

        if self.config.scraping.disable_animations:
            self.js.disable_animations()
        self.wait_until_loaded()

    def wait_until_loaded(self, timeout: int = None):
        """
        Waits on the webdriver instance to finish loading a page before returning.

        .. note::
            Because of the unending imagination of javascript devs, there may be cases where
            this function returns before the timeout although the page hasn't loaded.
        """
        if timeout is None:
            timeout = self.config.scraping.page_load_timeout

        try:
            # Wait until page is loaded from JS and jQuery perspective
            WebDriverWait(self.driver, timeout).until(self.js.is_page_loaded)
        except TimeoutException:
            logger.warning("Timed out waiting for the page to fully load, proceeding anyway")
        except UnexpectedAlertPresentException:
            logger.warning("Javascript alert noted, trying to proceed")

        sleep(self.config.scraping.wait_loading)

        # Some pages change after scrolling, so simulate some movement
        if self.config.scraping.prescroll:
            self.js.scroll_to(0, 100)
            sleep(self.config.scraping.wait_scroll)
            self.js.scroll_to(0, 9999)
            sleep(self.config.scraping.wait_scroll)
            self.js.scroll_to(0, 0)
            sleep(self.config.scraping.wait_scroll)

    def capture_screenshot(self, name: str, max_page_height: int = 0) -> Screenshot:
        """
        Captures the screenshot of the current rendering in the browser window.
        """
        return Screenshot.capture(
            name=name, driver=self.driver, scale=1 / self.device_pixel_ratio, max_page_height=max_page_height
        )

    def get_page_as_mhtml(self) -> bytes:
        """
        Gets an MHTML representation of the current page, returns it as a bytestring.
        MHTML must be enabled in the browser configuration, otherwise returns None.
        """
        if not self.config.browser.enable_mhtml:
            return None

        folder = Path(os.path.expanduser(self.config.scraping.temp_path))
        os.makedirs(folder, exist_ok=True)
        filename = "temp_mhtml_file.txt"

        try:
            os.remove(folder / filename)
        except OSError:
            pass

        self.js.save_mhtml(filename)

        try:
            with TimeoutContext(n_seconds=self.config.scraping.mhtml_timeout):
                while not os.path.exists(folder / filename):
                    sleep(0.25)
        except TimeoutError:
            logger.error("Failed to get MHTML snapshot within desired time limit!")
            return None

        with open(folder / filename, "rb") as f:
            return f.read()

    def _create_snapshot(self) -> PageSnapshot:
        before = datetime.now()

        logger.debug(f"Page title: {self.driver.title}")

        # Create screenshots if required
        screenshots: Dict[str, Screenshot] = {}
        if self.config.debug.screenshots:
            max_page_height = self.config.scrolling.max_page_height
            screenshots["first"] = self.capture_screenshot("first")
            if max_page_height == 0:
                screenshots["full"] = screenshots["first"].copy("full")
            else:
                screenshots["full"] = self.capture_screenshot("full", max_page_height=max_page_height)

        # Gather element metadata
        elements_metadata = self.js.get_element_metadata() or []
        num_elements = len(elements_metadata)

        # Gather page metadata
        inner_html = self.driver.find_element(By.XPATH, "/html").get_attribute("innerHTML")
        page_source = bs4.BeautifulSoup(f"<!DOCTYPE html><html>{inner_html}</html>", self.config.bs_html_parser)
        page_metadata = {
            "timestamp": before.isoformat(),
            "url": self.driver.current_url,
            "title": self.driver.title,
            "driver": self.driver.name,
            "full_page_size": (self.config.browser.width, self.js.get_full_height()),
            "device_pixel_ratio": self.device_pixel_ratio,
            "num_elements": num_elements,
            "screenshots": list(screenshots.keys()),
            "wtl_version": __version__,
        }

        milliseconds_passed = (datetime.now() - before).total_seconds() * 1000
        if num_elements < 2:
            logger.info("No elements detected on the page!")
        else:
            logger.info(f"Found {num_elements} " f"elements in {milliseconds_passed:.2f}ms")

        mhtml_source = self.get_page_as_mhtml() if self.config.scraping.save_mhtml else None

        # Assemble snapshot
        snapshot = PageSnapshot(
            page_source=page_source,
            page_metadata=page_metadata,
            elements_metadata=elements_metadata,
            screenshots=screenshots,
            mhtml_source=mhtml_source,
        )

        return snapshot
