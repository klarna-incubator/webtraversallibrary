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

"""Abstraction layer for a screenshot of a site"""

from __future__ import annotations

import io
import os
import time
from math import ceil
from pathlib import Path
from typing import Dict, List

from PIL import Image
from selenium.webdriver.remote.webdriver import WebDriver

from .color import Color
from .geometry import Point, Rectangle
from .graphics import draw_rect, draw_text
from .javascript import JavascriptWrapper


class Screenshot:
    """Abstraction layer for a screenshot of a site, allowing for various annotations."""

    def __init__(self, name: str, image: Image.Image):
        self.name = name
        self.image = image

    @classmethod
    def capture_viewport(cls, name: str, driver: WebDriver, scale: float = 1.0) -> Screenshot:
        """
        Creates a screenshot of the current viewport of a given webdriver.
        Scales the image by some pixel ratio, if given.
        Uses PIL as a backend.
        """
        page_screenshot_png_bytes = driver.get_screenshot_as_png()
        image = Image.open(io.BytesIO(page_screenshot_png_bytes)).convert("RGB")
        if scale != 1.0:
            new_size = [int(x * scale) for x in image.size]
            image = image.resize(new_size)
        return Screenshot(name, image)

    @classmethod
    def capture(cls, name: str, driver: WebDriver, scale: float = 1.0, max_page_height: int = 0) -> Screenshot:
        """
        Creates a snapshot on the given webdriver under certain conditions.
        """
        js = JavascriptWrapper(driver)
        viewport = js.find_viewport()
        if max_page_height < viewport.height:
            return cls.capture_viewport(name, driver, scale)

        # Capture at least one viewport's height, at most the page's height
        minimum_length = max(int(viewport.height), js.get_full_height())
        page_height = min(max_page_height, minimum_length)
        num_shots = ceil(page_height / viewport.height)
        viewport_screenshots: List[Image.Image] = []
        hidden_elements: Dict[int, str] = js.hide_position_fixed_elements()

        try:
            # We start from bottom, and go up!
            for shot_idx in range(num_shots, -1, -1):
                # Don't hide elements at the top
                if shot_idx == 0 or viewport.height > page_height:
                    js.show_position_fixed_elements(hidden_elements)

                # Scroll, hide sticky elements, and take viewport screenshot
                hidden = Screenshot._scroll_to(js, shot_idx * int(viewport.height))
                hidden_elements.update(hidden)
                viewport_screenshot = cls.capture_viewport("temp", driver, scale).image

                if shot_idx * viewport.height > page_height - viewport.height:
                    new_viewport_area = (
                        0,
                        0,
                        viewport.width,
                        page_height - shot_idx * viewport.height,
                    )
                    viewport_screenshot = viewport_screenshot.crop(new_viewport_area)

                # Append screenshot of the current viewport at the top of the image
                viewport_screenshots.insert(0, viewport_screenshot)
        finally:
            # Unhide everything and scroll back to the top
            js.show_position_fixed_elements(hidden_elements)

        total_height = sum(image.height for image in viewport_screenshots)
        final_screenshot = Image.new("RGB", (viewport_screenshots[0].width, total_height))

        offset = 0
        for viewport_screenshot in viewport_screenshots:
            final_screenshot.paste(viewport_screenshot, (0, offset))
            offset += viewport_screenshot.height

        return Screenshot(name, final_screenshot)

    @classmethod
    def load(cls, name: str, path: Path) -> Screenshot:
        return cls(name, Image.open(str(path)))

    def save(self, path: Path, suffix: str = ""):
        """Saves screenshot to given path. Filename consists of the screenshot name
        and an optional suffix."""
        os.makedirs(path, exist_ok=True)
        filename = f"{self.name}_{suffix}.png" if suffix else f"{self.name}.png"
        self.image.save(str(path / filename))

    def copy(self, new_name: str) -> Screenshot:
        return Screenshot(new_name, self.image.copy())

    def highlight(self, rect: Rectangle, color: Color, text: str = "", width: int = 1):
        """
        Draws a colored rectangle on the screenshot.
        Can also annotate with a text below the rectangle, if given.
        """
        draw_rect(self.image, rect, color, width)
        if text:
            offset = 1
            self.annotate(Point(rect.x + offset, rect.y + rect.height + offset), color, 12, text)

    def annotate(self, top_left: Point, color: Color, size: int, text: str):
        """
        Writes text with a given color on the screenshot.
        """
        draw_text(self.image, top_left, color, size, text)

    @property
    def size(self) -> Point:
        """Returns a (width, height) Point of the screenshot size in pixels"""
        return Point(self.width, self.height)

    @property
    def height(self) -> int:
        return self.image.height

    @property
    def width(self) -> int:
        return self.image.width

    @staticmethod
    def _scroll_to(js: JavascriptWrapper, y_pos: int, elements: List[str] = None):
        waiting_time = 0.1
        hidden: Dict[int, str] = {}

        js.scroll_to(0, y_pos)
        time.sleep(waiting_time)
        hidden = js.hide_position_fixed_elements(elements=elements if elements else [])
        time.sleep(waiting_time)

        return hidden
