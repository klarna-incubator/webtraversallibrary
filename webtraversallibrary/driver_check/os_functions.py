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
Base classes and OS specific classes containing
functions to look up external dependencies.
"""

import abc
import enum
import logging
import sys
from shutil import which
from subprocess import CalledProcessError, run
from typing import List, Optional, Union

logger = logging.getLogger("wtl")


class Drivers(enum.Enum):
    """
    Drivers used for various operations.
    """

    GOOGLE_CHROME = "google-chrome"
    CHROMIUM = "chromium"
    CHROMEDRIVER = "chromedriver"
    FIREFOX = "firefox"
    GECKODRIVER = "geckodriver"


class OS(enum.Enum):
    """
    Various supported operating systems.
    """

    LINUX = "linux"
    MACOS = "macos"
    WINDOWS = "windows"


class OsFunctionsBase(abc.ABC):
    """
    Extendable base class for OS specific classes able to determine existence of external dependencies.
    """

    # Disable static method checks for this class, since it's supposed to be overridden (if necessary)
    # pylint: disable=no-self-use

    def get_driver_location(self, driver: Drivers) -> Optional[str]:
        """
        Tries to find where on the system a driver is located.
        """
        which_location = which(driver.value)
        return which_location

    def is_driver_installed(self, driver: Drivers) -> bool:
        """
        Checks if a driver is installed on the system.
        """
        if driver.name in sys.modules:
            return True

        return self.get_driver_location(driver) is not None

    def get_driver_version(self, driver: Drivers) -> Optional[str]:
        """
        Tries to get the version of a driver.
        """
        return get_cmd_output([f"{driver.value}", "--version"])


class OsFunctionsLinux(OsFunctionsBase):
    """
    Extended class for Linux from OsFunctionsBase.
    """


class OsFunctionsMacOs(OsFunctionsBase):
    """
    Extended class for MacOS from OsFunctionsBase.
    """

    @staticmethod
    def get_driver_name(driver: Drivers):
        """
        Converts the driver instance to its OS specific application name.
        """
        return {
            Drivers.GOOGLE_CHROME: "Google Chrome.app",
            Drivers.CHROMIUM: "Chromium.app",
            Drivers.FIREFOX: "Firefox.app",
        }.get(driver, None)

    def get_driver_location(self, driver: Drivers) -> Optional[str]:
        location = super().get_driver_location(driver)
        if location:
            return location

        driver_name = self.get_driver_name(driver)
        cmd = ["mdfind", f"kMDItemKind == 'Application' && kMDItemDisplayName == '{driver_name}'"]
        result = get_cmd_output(cmd)

        if result is None:
            return None
        locations = result.split("\n")

        if len(locations) > 0:
            return locations[0]

        return None

    def get_driver_version(self, driver: Drivers) -> Optional[str]:
        driver_location = self.get_driver_location(driver)
        if driver_location.endswith(".app"):
            driver_name = driver_location.split("/")[-1]
            driver_name = driver_name.split(".")[0]
            cmd = [f"{driver_location}/Contents/MacOS/{driver_name}", "--version"]
            return get_cmd_output(cmd)

        return super().get_driver_version(driver)


class OsFunctionsWindows(OsFunctionsBase):
    """
    Extended class for Windows from OsFunctionsBase.
    """

    def is_driver_installed(self, driver: Drivers) -> bool:
        if super().is_driver_installed(driver):
            return True
        # TODO: Add driver check for Windows
        logger.info("Driver check on Windows is currently not supported.")
        return True


def get_os_function_class(os: OS) -> OsFunctionsBase:
    """
    Converts an OS parameter into its corresponding SystemFunctions class.
    """
    os_class = {
        OS.LINUX: OsFunctionsLinux(),
        OS.MACOS: OsFunctionsMacOs(),
        OS.WINDOWS: OsFunctionsWindows(),
    }.get(os, None)
    if not os_class:
        raise SystemError("Could not determine Operating System")
    return os_class


def get_cmd_output(cmd: Union[str, List]) -> Optional[str]:
    """
    Executes a command and returns the output.
    """
    if isinstance(cmd, str):
        cmd = cmd.split(" ")
    try:
        result = run(cmd, check=True, capture_output=True)
        return result.stdout.decode().strip()
    except (CalledProcessError, FileNotFoundError):
        return None
