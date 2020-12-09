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
Web Traversal Library (WTL)
Provides a bottom abstraction layer for automatic web workflows.
"""

from .actions import Action, Actions, ElementAction
from .classifiers import ActiveElementFilter, ElementClassifier, ScalingMode, ViewClassifier
from .color import Color
from .config import Config
from .error import ElementNotFoundError, Error, ScrapingError, WebDriverSendError, WindowClosedError
from .geometry import Point, Rectangle
from .javascript import JavascriptWrapper
from .policies import multi_tab_coroutine, single_tab, single_tab_coroutine
from .scraper import Scraper
from .selector import Selector
from .snapshot import Elements, PageElement, PageSnapshot
from .version import __version__
from .view import View
from .window import Window
from .workflow import Workflow
