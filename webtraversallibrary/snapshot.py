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
Static snapshot of a web page. Contains source, screenshots, element images, and metadata.
"""
from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Union

import bs4
from PIL import Image

from .config import Config
from .error import ScrapingError
from .geometry import Point, Rectangle
from .graphics import crop_image
from .processtools import cached_property
from .screenshot import Screenshot
from .selector import Selector

logger = logging.getLogger("wtl")


@dataclass(frozen=True)
class PageElement:
    """
    Represents an element with associated and structured `metadata` on a given `page`.
    """

    page: "PageSnapshot" = field(repr=False)
    metadata: dict = field(repr=False)

    @property
    def raw_scores(self) -> Dict[str, float]:
        """Returns all raw classifier scores."""
        if "raw_scores" not in self.metadata:
            self.metadata["raw_scores"] = {}
        return self.metadata["raw_scores"]

    @cached_property
    def tag(self) -> bs4.Tag:
        """Returns the bs4.Tag associated with this PageElement"""
        tag = self.page.page_source.find(attrs={"wtl-uid": self.wtl_uid})
        if not tag:
            logger.warning(f"No bs4.tag with wtl-uid={self.wtl_uid}!")
        return tag

    @cached_property
    def wtl_uid(self) -> int:
        """Returns the wtl-uid associated with this PageElement."""
        return self.metadata["wtl_uid"]

    @cached_property
    def wtl_parent_uid(self) -> int:
        """Returns the wtl-uid associated with the parent of this PageElement."""
        return self.metadata["wtl_parent_uid"]

    @cached_property
    def parent(self) -> PageElement:
        """Returns the parent of this PageElement."""
        return self.page.elements.by_uid(self.wtl_parent_uid)

    @cached_property
    def location(self) -> Point:
        """Returns the top-left position of this PageElement."""
        location = self.metadata["location"]
        return Point(location["x"], location["y"])

    @cached_property
    def size(self) -> Point:
        """Returns the wtl-uid associated with this PageElement."""
        size = self.metadata["size"]
        return Point(size["width"], size["height"])

    @cached_property
    def bounds(self) -> Rectangle:
        """Returns the bounding box of this PageElement."""
        return Rectangle(self.location, self.location + self.size)

    @cached_property
    def selector(self) -> Selector:
        """CSS Selector for the element without attributes."""
        return Selector.build(self.page.page_source, self.wtl_uid)

    @cached_property
    def font_size(self) -> float:
        """Returns resolved font size property in pixels."""
        return PageElement.parse_resolved_size(self.metadata["font_size"])

    @cached_property
    def screenshot(self) -> Image.Image:
        """
        Returns element screenshot for the given element, cropped from the page screenshot.

        .. warning::
            Screenshotting must have been enabled (and run) on the page for this to work!
        """
        fixed_pos = self.metadata["fixed_pos"]
        page_screenshot = self.page.screenshots["first"] if fixed_pos else self.page.screenshots["full"]
        assert page_screenshot, "Page screenshotting must be enabled if requesting element screenshot"

        screenshot_box = Rectangle(Point.zero(), page_screenshot.size)
        element_box = self.bounds
        intersection_box = Rectangle.intersection([screenshot_box, element_box])

        if intersection_box.area == 0:
            return None

        return crop_image(page_screenshot.image, intersection_box)

    @staticmethod
    def parse_resolved_size(value: str) -> float:
        """
        Parse resolved CSS size value
        :raises: ``ValueError`` if format not supported (currently float followed by ``px``)
        """
        pattern = re.compile(r"\d+(.\d*)?px")
        value = value.strip()
        if not pattern.fullmatch(value):
            raise ScrapingError(f"Expected a number followed by px, got '{value}'")
        return float(value[:-2])


class Elements(list):
    """Helper class for a list of elements from the same page"""

    def by_score(self, name: Union[str, Iterable[str]], limit: float = 0.0) -> Elements:
        """Return elements tagged with all given scores over a certain limit"""
        if name == "all":
            return self

        if isinstance(name, str):
            return Elements([e for e in self if name in e.metadata and e.metadata[name] > limit])

        return Elements([e for e in self if set(name) <= set(e.metadata.keys())])

    def by_raw_score(self, name: Union[str, Iterable[str]], limit: float = 0.0) -> Elements:
        """Return elements tagged with all given raw scores over a certain limit"""
        if name == "all":
            return self

        if isinstance(name, str):
            return Elements([e for e in self if name in e.raw_scores and e.raw_scores[name] > limit])

        return Elements([e for e in self if set(name) <= set(e.metadata.keys())])

    def by_selector(self, selector: Selector) -> Elements:
        """Return all elements that match a given selector"""
        if not self:
            return Elements([])

        tags = set(self[0].page.page_source.html.select(selector.css))
        if not tags:
            return Elements([])

        wtl_uids = set(int(x.attrs["wtl-uid"]) for x in tags if "wtl-uid" in x.attrs)
        elements = Elements([e for e in self if e.wtl_uid in wtl_uids])

        # Falls back on BS4 tags if selector matches something that hasn't been snapshotted yet
        if not elements:
            elements = Elements([e for e in self if e.tag in tags])

        return elements

    def by_subtree(self, target: Union[Selector, PageElement], include_root: bool = True) -> Elements:
        """Return all elements belonging to the subtree where given element is the root"""
        if not self:
            return Elements([])

        if isinstance(target, Selector):
            targets = self.by_selector(target)
            assert len(targets) == 1
            target = targets[0]

        assert isinstance(target, PageElement)
        tags = set(target.tag.descendants)
        return Elements([e for e in self if e.tag in tags] + ([target] if include_root else []))

    def by_uid(self, wtl_uid: int) -> PageElement:
        """Returns the element with the given wtl_uid"""
        for e in self:
            if e.wtl_uid == wtl_uid:
                return e
        return None

    def sort_by(self, name: str = None, reverse: bool = False) -> Elements:
        """
        Sorts by a certain (raw) score. If given name does not exist the element gets (raw) score 0.
        """
        self.sort(key=lambda e: e.raw_scores.get(name, 0), reverse=reverse)
        return self

    def unique(self) -> PageElement:
        """Checks if exactly one element exists, if so returns it. Throws AssertionError otherwise"""
        assert len(self) == 1
        return self[0]


@dataclass(repr=False, frozen=True)
class PageSnapshot:
    """
    Static snapshot of a web page.
    Contains source (DOM), screenshots, elements and metadata.

    .. note::
        Not _all_ parts of the website (separate CSS and JS files, for example) are
        represented here. If that's what you need, consider storing MHTML snapshots
        and manipulating them manually.
    """

    page_source: bs4.BeautifulSoup
    page_metadata: Optional[dict]
    elements_metadata: List[dict]
    elements: Elements = field(init=False)
    screenshots: Dict[str, Screenshot] = field(default_factory=dict)
    mhtml_source: bytes = None

    def __post_init__(self):
        page_elements = Elements([PageElement(self, metadata) for metadata in self.elements_metadata])
        object.__setattr__(self, "elements", page_elements)

        if "screenshots" not in self.page_metadata:
            self.page_metadata["screenshots"] = []

    def new_screenshot(self, name: str, of: str) -> Screenshot:
        """
        Creates a new screenshot from a copy of a previous one.
        Saves it to this snapshot and returns the new screenshot object.
        """
        assert of in self.screenshots.keys(), "Creating screenshot from nonexistant original!"
        self.screenshots[name] = self.screenshots[of].copy(name)
        return self.screenshots[name]

    @classmethod
    def load(cls, path: Path, bs4_parser: str = None) -> PageSnapshot:
        """
        Returns a PageSnapshot at given path (directory) in the format
        as stored in :func:`save`.
        """
        assert path.exists()
        screenshots: Dict[str, Screenshot] = {}
        mhtml_source: bytes = None

        if bs4_parser is None:
            bs4_parser = Config.default().bs_html_parser

        with open(path / "source.html", encoding="utf8") as f:
            page_source = bs4.BeautifulSoup(f.read(), bs4_parser)
        with open(path / "page_metadata.json", encoding="utf8") as f:
            page_metadata = json.load(f)
        with open(path / "elements_metadata.json", encoding="utf8") as f:
            elements_metadata = json.load(f)
        for f in page_metadata["screenshots"]:
            screenshots[str(f)] = Screenshot.load(str(f), path / f"{f}.png")
        try:
            with open(path / "page.mhtml", "rb") as f:  # type: ignore
                mhtml_source = f.read()  # type: ignore
        except OSError:
            pass

        snapshot = PageSnapshot(
            page_source=page_source,
            page_metadata=page_metadata,
            elements_metadata=elements_metadata,
            screenshots=screenshots,
            mhtml_source=mhtml_source,
        )

        return snapshot

    def save(self, path: Path):
        """
        Saves the current PageSnapshot instance to a folder.
        The number of files depends on whether screenshots were taken or not.
        """
        os.makedirs(path, exist_ok=True)

        with open(path / "source.html", "w", encoding="utf8") as f:
            f.write(str(self.page_source))
        with open(path / "page_metadata.json", "w", encoding="utf8") as f:
            json.dump(self.page_metadata, f)
        with open(path / "elements_metadata.json", "w", encoding="utf8") as f:
            json.dump(self.elements_metadata, f)
        for scr in self.screenshots.values():
            scr.save(path)
        if self.mhtml_source:
            with open(path / "page.mhtml", "wb") as f:  # type: ignore
                f.write(self.mhtml_source)  # type: ignore
