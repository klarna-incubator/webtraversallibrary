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

"""Contains common library-level errors"""

from __future__ import annotations

import logging
from functools import wraps

logger = logging.getLogger("wtl")


class Error(Exception):
    """Base class for all WTL-specific exceptions."""

    @classmethod
    def wrapped(cls, func):
        """Wraps a function in a try-except block where AssertionErrors are logged and reraised as Error."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except AssertionError as e:
                logger.error(e)
                raise cls(e)
            return result

        return wrapper


class ScrapingError(Error):
    """Any error related to scraping/parsing webpages."""


class ElementNotFoundError(Error):
    """Any error related to finding elements on the page."""


class WindowClosedError(Error):
    """Trying to access a browser instance that was closed by the user"""


class WebDriverSendError(Error):
    """Any error related to custom sending commands to a WebDriver instance"""
