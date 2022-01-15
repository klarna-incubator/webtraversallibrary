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

import io
from pathlib import Path

from PIL import Image

import webtraversallibrary as wtl
from tests.graphics_test import equal_images
from webtraversallibrary.screenshot import Screenshot

ORIGINAL_DIR = Path("tests/data/")


class MockWebDriver:
    def __init__(self, filename: str):
        self.filename = filename

    def get_screenshot_as_png(self) -> Image.Image:
        img = Image.open(ORIGINAL_DIR / self.filename)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format="PNG")
        return img_byte_arr.getvalue()

    def get_log(self, _):
        return []

    def execute_script(self, *_, **__):
        return None


def test_capture_viewport():
    driver = MockWebDriver("crop.png")
    result = Screenshot.capture_viewport("testing", driver)
    reference = Image.open(ORIGINAL_DIR / "crop.png")

    assert result.name == "testing"
    assert equal_images(result.image, reference)

    result_scaled = Screenshot.capture_viewport("testing", driver, scale=3.0)
    reference_scaled = Image.open(ORIGINAL_DIR / "crop_3.png")

    assert result_scaled.name == "testing"
    assert equal_images(result_scaled.image, reference_scaled)


def test_save_load_copy(tmpdir):
    driver = MockWebDriver("crop.png")
    result = Screenshot.capture_viewport("testing", driver)
    result.save(tmpdir, "mytest")
    result2 = Screenshot.load("testing", tmpdir / "testing_mytest.png")

    assert equal_images(result.image, result2.image)

    result3 = result.copy("testing3")

    assert result3.name == "testing3"
    assert equal_images(result.image, result3.image)


def test_capture(mocker):
    driver = MockWebDriver("cat.png")

    mocker.patch("webtraversallibrary.javascript.JavascriptWrapper.get_full_height", return_value=2048)
    mocker.patch(
        "webtraversallibrary.javascript.JavascriptWrapper.find_viewport",
        return_value=wtl.Rectangle(wtl.Point(0, 0), wtl.Point(256, 256)),
    )
    mocker.patch("webtraversallibrary.javascript.JavascriptWrapper.hide_position_fixed_elements", return_value={})

    result = Screenshot.capture("testing", driver, max_page_height=900)
    reference = Image.open(ORIGINAL_DIR / "page.png")

    assert result.name == "testing"
    assert equal_images(result.image, reference)
