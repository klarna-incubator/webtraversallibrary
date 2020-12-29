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
Collection of helper classes used in Workflow.
"""

import logging
from collections.abc import Collection
from typing import Any, Dict, Iterable, Union

from selenium import webdriver

from .classifiers import Classifier, ElementClassifier, ViewClassifier
from .error import ElementNotFoundError
from .javascript import JavascriptWrapper
from .selector import Selector
from .snapshot import PageElement, PageSnapshot

logger = logging.getLogger("wtl")


class ClassifierCollection(Collection):
    """Helper class for predefined classifiers"""

    def __init__(self, classifiers: Iterable[Classifier]):
        self._classifiers: Dict[str, Classifier] = {}
        if classifiers:
            for classifier in classifiers:
                self.add(classifier)

    def add(self, classifier: Classifier):
        self._classifiers[classifier.name] = classifier

    def start(self, classifier: Union[str, Classifier]):
        name = classifier if isinstance(classifier, str) else classifier.name
        self._classifiers[name].enabled = True

    def stop(self, classifier: Union[str, Classifier]):
        name = classifier if isinstance(classifier, str) else classifier.name
        self._classifiers[name].enabled = False

    @property
    def active_element_classifiers(self):
        return ClassifierCollection([c for c in self if c.enabled and c.callback and isinstance(c, ElementClassifier)])

    @property
    def active_view_classifiers(self):
        return ClassifierCollection([c for c in self if c.enabled and c.callback and isinstance(c, ViewClassifier)])

    def __iter__(self):
        yield from self._classifiers.values()

    def __contains__(self, classifier: Any):
        if isinstance(classifier, str):
            return classifier in self._classifiers
        if isinstance(classifier, Classifier):
            return classifier in self._classifiers.values()
        raise TypeError

    def __len__(self):
        return len(self._classifiers)


class MonkeyPatches:
    """Helper class for monkeypatches"""

    def __init__(self, patches: Dict[Selector, str] = None):
        self._data: Dict[Selector, str] = patches or {}
        self._default: str = None

    def add(self, selector: Selector, patch: str):
        self._data[selector] = patch

    def set_default(self, patch: str):
        """Equivalent to ``check(Selector("*"), element)`` but much faster."""
        self._default = patch

    def check(self, snapshot: PageSnapshot, element: PageElement) -> str:
        """If a rule applies for given element for given snapshot, return the most specific value"""
        selector_elements = [(s, snapshot.elements.by_selector(s)) for s in self._data]
        selector_elements.sort(key=lambda item: len(item[1]), reverse=True)
        for selector, elements in selector_elements:
            if element in elements:
                return self._data[selector]
        return self._default

    def __contains__(self, selector: Selector):
        return selector in self._data

    def __len__(self):
        return len(self._data)


class FrameSwitcher:
    """
    Helper class for entering and exiting iframes.
    Raises ElementNotFoundError if an iframe could not be found.
    """

    def __init__(self, identifier: str, js: JavascriptWrapper, driver: webdriver):
        self.name = None
        self.driver = driver

        if identifier:
            self.name = js.find_iframe_name(identifier)
            if not self.name:
                raise ElementNotFoundError(f"Found no iframe with identifier '{identifier}'")

    def __enter__(self):
        """
        Goes into an <iframe> object with given name.
        """
        if self.name:
            logger.debug(f"Entering iframe: '{self.name}'")
            self.driver.switch_to.frame(self.name)

    def __exit__(self, *_):
        """
        Steps out into the parent frame.
        """
        if self.name:
            logger.debug(f"Exiting iframe: '{self.name}'")
            self.driver.switch_to.default_content()
