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
import enum

from webtraversallibrary.driver_check import OS, get_current_os, get_os_function_class
from webtraversallibrary.driver_check.os_functions import (
    OsFunctionsLinux,
    OsFunctionsMacOs,
    OsFunctionsWindows,
    get_cmd_output,
)


class MockDrivers(enum.Enum):
    PYTHON = "python"


def test_get_current_os():
    os = get_current_os()
    assert os is not None


def test_get_cmd_output():
    result = get_cmd_output("ls")
    assert result is not None


def test_get_os_system_function_class():
    assert isinstance(get_os_function_class(OS.LINUX), OsFunctionsLinux)
    assert isinstance(get_os_function_class(OS.MACOS), OsFunctionsMacOs)
    assert isinstance(get_os_function_class(OS.WINDOWS), OsFunctionsWindows)


def test_function_class_get_is_driver_installed():
    fc = get_os_function_class(get_current_os())
    # noinspection PyTypeChecker
    assert fc.is_driver_installed(MockDrivers.PYTHON) is True


def test_function_class_get_driver_version():
    fc = get_os_function_class(get_current_os())
    # noinspection PyTypeChecker
    assert "Python" in fc.get_driver_version(MockDrivers.PYTHON)


def test_function_class_get_driver_location():
    fc = get_os_function_class(get_current_os())
    # noinspection PyTypeChecker
    assert fc.get_driver_location(MockDrivers.PYTHON) is not None
