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

import logging
import platform

from .os_functions import OS, Drivers, get_os_function_class

logger = logging.getLogger("wtl")


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


def log_driver_version(title: str, driver: Drivers, os: OS = None):
    os = os if os else get_current_os()
    version = get_driver_version(driver, os)
    if version:
        logger.info(f"{title}: {version}")
    else:
        logger.info(f"{title}: [FAILED]")


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
