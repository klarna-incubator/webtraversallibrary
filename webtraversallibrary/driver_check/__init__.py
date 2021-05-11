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


class Drivers(enum.Enum):
    CHROME = "google-chrome"
    CHROMIUM = "chromium"
    CHROMEDRIVER = "chromedriver"
    FIREFOX = "firefox"
    GECKODRIVER = "geckodriver"


class OS(enum.Enum):
    LINUX = "linux"
    MACOS = "macos"
    WINDOWS = "windows"


def get_current_os() -> OS:
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
    if isinstance(cmd, str):
        cmd = cmd.split(" ")
    try:
        result = run(cmd, check=True, capture_output=True)
        return result.stdout.decode().strip()
    except (CalledProcessError, FileNotFoundError):
        return None
