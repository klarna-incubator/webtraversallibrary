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
Fallback functionality for the logging module.
Will be removed in future a version.
"""

from importlib import import_module

from .logging_utils import *  # pylint: disable=unused-wildcard-import,wildcard-import

logging = import_module("logging")


def getLogger(name: str):
    """Fallback for the logging.getLogger() function to prevent relative import errors."""
    return logging.getLogger(name)
