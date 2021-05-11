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
Helper functions to check versions and existence of installed dependencies.
"""

import enum
import platform
from subprocess import CalledProcessError, run
from typing import List, Optional, Union

from driver_check.os_functions import get_os_function_class


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


def is_driver_installed(driver: Drivers, os: OS = None) -> bool:
    """
    Checks if a given driver is installed on the OS.
    """
    os = os if os else get_current_os()
    sf = get_os_function_class(os)
    return sf.is_driver_installed(driver)


def get_driver_version(driver: Drivers, os: OS = None) -> str:
    """
    Gets the driver version.
    """
    os = os if os else get_current_os()
    sf = get_os_function_class(os)
    return sf.get_driver_version(driver)


def get_driver_location(driver: Drivers, os: OS = None) -> str:
    """
    Gets the location of the driver.
    """
    os = os if os else get_current_os()
    sf = get_os_function_class(os)
    return sf.get_driver_location(driver)


def get_current_os() -> OS:
    """
    Gets the current OS of the machine running.
    """
    system = platform.system()
    os = {
        "Linux": OS.LINUX,
        "Darwin": OS.MACOS,
        "Windows": OS.WINDOWS,
    }.get(system, None)
    if not os:
        raise SystemError("Could not determine Operating System")
    return os


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
