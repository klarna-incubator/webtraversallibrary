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

from pathlib import Path

import pytest
from PIL import Image, ImageChops, ImageStat

import webtraversallibrary as wtl
from webtraversallibrary.graphics import crop_image, draw_rect, draw_text

ORIGINAL_DIR = Path("tests/data/")


def equal_images(img1, img2):
    """Adapted from Nicolas Hahn:
    https://github.com/nicolashahn/diffimg/blob/master/diffimg/__init__.py
    """
    if img1.mode != img2.mode or img1.size != img2.size or img1.getbands() != img2.getbands():
        return False

    diff_img = ImageChops.difference(img1, img2)
    stat = ImageStat.Stat(diff_img)
    return (100 * sum(stat.mean)) / (len(stat.mean) * 255) < 0.01


def test_crop_image():
    img = Image.open(ORIGINAL_DIR / "cat.png")
    rect = wtl.Rectangle(wtl.Point(50, 70), wtl.Point(130, 170))
    result = crop_image(img, rect)

    reference = Image.open(ORIGINAL_DIR / "crop.png")

    assert equal_images(result, reference)

    with pytest.raises(ValueError):
        rect = wtl.Rectangle.empty()
        crop_image(img, rect)

    with pytest.raises(ValueError):
        rect = wtl.Rectangle(wtl.Point(257, 257), wtl.Point(270, 280))
        crop_image(img, rect)


def test_draw_rect():
    img = Image.open(ORIGINAL_DIR / "cat.png")
    rect_1 = wtl.Rectangle(wtl.Point(40, 50), wtl.Point(70, 80))
    rect_2 = wtl.Rectangle(wtl.Point(200, 210), wtl.Point(220, 230))
    draw_rect(img, rect_1, wtl.Color(50, 150, 250), 5)
    draw_rect(img, rect_2, wtl.Color(250, 30, 30), 5)

    reference = Image.open(ORIGINAL_DIR / "rect.png")

    assert equal_images(img, reference)


@pytest.mark.skip(reason="currently broken, needs new reference image")
def test_draw_text():
    img = Image.open(ORIGINAL_DIR / "cat.png")
    draw_text(img, wtl.Point(10, 10), wtl.Color(50, 150, 250), 20, "This is a cat")
    draw_text(img, wtl.Point(50, 200), wtl.Color(0, 0, 0), 50, "Not a dog")

    reference = Image.open(ORIGINAL_DIR / "text.png")

    assert equal_images(img, reference)
