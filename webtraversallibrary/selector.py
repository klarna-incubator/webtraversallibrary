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
This module contains heuristics for generating selectors.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import total_ordering
from typing import Union

import bs4

logger = logging.getLogger("wtl")


@total_ordering
@dataclass(frozen=True)
class Selector:
    """
    Web element selector based on CSS and XPATH.
    You may also specify an identifier (name or ID) of an iframe in which the given element is located.
    The class itself provides no guarantees on whether the selector is unique or even matches anything.
    The ``iframe`` value can be used if this selector refers to an element inside an iframe. Specify as ID or name.
    """

    css: str = "*"
    xpath: str = "/"
    iframe: str = None

    def __lt__(self, other: Selector) -> bool:
        if len(self.css) == len(other.css):
            return self.xpath < other.xpath
        return len(self.css) < len(other.css)

    @classmethod
    def build(cls, bs4_soup: bs4.BeautifulSoup, target: Union[bs4.Tag, int]) -> Selector:
        """
        Compute xpath and css of a ``target`` in a bs4.BeautifulSoup.
        Will be verbose. Use a separate generalizer if you want reusable selectors.
        """
        # Identify target
        if isinstance(target, bs4.Tag):
            element = target
        else:
            options = bs4_soup.find_all(attrs={"wtl-uid": target})
            if len(options) != 1:
                logger.error("Invalid wtl-uid given to Selector.build, returning blank selector")
                return cls(css="bad_wtl_uid_no_matches", xpath="bad_wtl_uid_no_matches")
            element = options[0]

        names, indices = [], []
        child = element if element.name else element.parent

        for parent in child.parents:
            siblings = parent.find_all(child.name, recursive=False)
            index = 1 + siblings.index(child)
            names.append(cls._safe_tag_name(child.name))
            indices.append(-1 if len(siblings) == 1 else index)
            child = parent

        css_components = [
            name if index == -1 else f"{name}:nth-of-type({index})" for (name, index) in zip(names, indices)
        ]
        xpath_components = [name if index == -1 else f"{name}[{index}]" for (name, index) in zip(names, indices)]

        css = ">".join(reversed(css_components)).strip()
        xpath = "/" + "/".join(reversed(xpath_components)).strip()
        return Selector(css=css, xpath=xpath)

    @classmethod
    def _safe_tag_name(cls, name: str) -> str:
        if ":" in name or "=" in name:
            return "*"
        return name
