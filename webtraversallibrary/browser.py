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
Module for different webdrivers considered.
"""
from __future__ import annotations

import importlib.resources
import json
import logging
import os.path
from pathlib import Path
from typing import List

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.remote.webdriver import WebDriver

from .config import Config
from .error import WebDriverSendError
from .javascript import JavascriptWrapper
from .version_check import VERSION_CMD, run_cmd

logger = logging.getLogger("wtl")


class Browser:
    """Abstraction class for browser interaction"""

    def __init__(self, config: Config, profile_path: Path = None, preload_callbacks: List[Path] = None):
        """
        Creates a WebDriver object with the given configuration.
        :param: configuration Configuration dictionary
        :return: A WebDriver instance
        """
        self.config = config
        self.profile_path = profile_path

        if config.browser.browser == "chrome":
            self.driver = self._setup_chrome()
        elif config.browser.browser == "firefox":
            self.driver = self._setup_firefox()
        else:
            raise NotImplementedError(f"Uninmplemented browser type given to setup_driver: {config.browser.browser}")

        self.js = JavascriptWrapper(self.driver, self.config)

        preload_callbacks = preload_callbacks or []
        for cb in preload_callbacks:
            self.driver.add_script(str(cb))

    def _setup_chrome(self) -> WebDriver:
        assert run_cmd(VERSION_CMD.CHROME, "Chrome version") or run_cmd(VERSION_CMD.CHROMIUM, "Chromium version")
        assert run_cmd(VERSION_CMD.CHROMEDRIVER, "Chromedriver version")

        chrome_options = webdriver.ChromeOptions()
        browser = self.config.browser

        # Disable security
        # Don't enforce the same-origin policy, see https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
        # Without this the JS code executed with Selenium WebDriver cannot access cross-domain CSS which are popular.
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--no-sandbox")

        # Disable unused/annoying features
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument("--hide-scrollbars")
        chrome_options.add_argument("--disable-dev-shm-usage")

        chrome_options.headless = browser.headless

        if self.profile_path:
            profile_dir = self.profile_path.name
            user_data_dir = str(self.profile_path.parent)
            chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
            chrome_options.add_argument(f"--profile-directory={profile_dir}")

        if browser.proxy:
            chrome_options.add_argument(f"--proxy-server={browser.proxy}")
            chrome_options.add_argument("--disk-cache-dir=chrometemp/")  # Proxy messes up access rights of cache folder

        if browser.enable_mhtml:
            with importlib.resources.path("webtraversallibrary.extension", "wtl_extension.crx") as filepath:
                chrome_options.add_extension(str(filepath))
            chrome_options.add_experimental_option(
                "prefs", {"download.default_directory": os.path.expanduser(self.config.scraping.temp_path)}
            )

        if "pixelRatio" in browser and browser.pixelRatio != 0:
            # Emulating a mobile device - the full set of parameters must be provided
            chrome_options.add_experimental_option(
                "mobileEmulation",
                {
                    "deviceMetrics": {
                        "width": browser.width,
                        "height": browser.height,
                        "pixelRatio": browser.pixelRatio,
                    },
                    "userAgent": browser.useragent,
                },
            )
        else:
            if "useragent" in browser:
                chrome_options.add_argument(f'--user-agent="{browser.useragent}"')

        if "width" in browser and "height" in browser:
            chrome_options.add_argument(f"--window-size={browser.width},{browser.height + 120}")

        capabilities = DesiredCapabilities.CHROME.copy()
        capabilities["goog:loggingPrefs"] = {"browser": "ALL"}

        def _add_script(driver: WebDriver, script_path: str):
            send(driver, "Page.addScriptToEvaluateOnNewDocument", {"source": script_path})

        WebDriver.add_script = _add_script

        # launch Chrome
        driver = webdriver.Chrome(options=chrome_options, desired_capabilities=capabilities)

        return driver

    def _setup_firefox(self) -> WebDriver:
        assert run_cmd(VERSION_CMD.FIREFOX, "Firefox version")
        assert run_cmd(VERSION_CMD.GECKODRIVER, "Geckodriver version")

        firefox_profile = webdriver.FirefoxProfile()
        firefox_options = webdriver.FirefoxOptions()
        browser = self.config.browser

        # Disable security
        firefox_options.add_argument("-safe-mode")
        firefox_profile.set_preference("browser.link.open_newwindow", 3)
        firefox_profile.set_preference("browser.link.open_newwindow.restriction", 0)
        firefox_profile.set_preference("media.volume_scale", "0.0")

        firefox_options.headless = browser.headless

        if browser.proxy:
            address = browser.proxy.split(":")
            firefox_profile.set_preference("network.proxy.http", address[0])
            firefox_profile.set_preference("network.proxy.http_port", address[1])

        if browser.enable_mhtml:
            # TODO
            logger.critical("Firefox does not currently support MHTML")
            assert False

        if "pixelRatio" in browser and browser.pixelRatio != 0:
            # TODO
            logger.error("Firefox does not currently support custom pixelratio")

        if "useragent" in browser:
            firefox_profile.set_preference("general.useragent.override", browser.useragent)

        def _add_script(driver: WebDriver, script_path: str):
            send(driver, "Page.addScriptToEvaluateOnNewDocument", {"source": script_path})

        WebDriver.add_script = _add_script

        # TODO No support to output console logs for geckodriver

        driver = webdriver.Firefox(options=firefox_options, firefox_profile=firefox_profile)

        # Screen size (we can't set viewport size as for Chrome so we adjust screen size)
        if "width" in browser and "height" in browser:
            driver.set_window_size(browser.width, browser.height)

        return driver


def send(driver: WebDriver, cmd: str, params: dict = None) -> int:
    """
    Send command to the webdriver, return resulting status code.
    """
    # pylint: disable=protected-access
    if params is None:
        params = {}
    resource = f"/session/{driver.session_id}/chromium/send_command_and_get_result"
    url = driver.command_executor._url + resource
    body = json.dumps({"cmd": cmd, "params": params})
    response = driver.command_executor._request("POST", url, body)
    value = response.get("value")

    if response.get("status", False):
        raise WebDriverSendError(f"Command '{cmd}' returned status={value}")

    return value
