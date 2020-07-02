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

import webtraversallibrary as wtl
from webtraversallibrary.javascript import JavascriptWrapper


class MockWebDriver:
    def __init__(self):
        self.calls = 0
        self.to_return = None

    def execute_script(self, *_, **__):
        self.calls += 1
        return self.to_return if self.to_return else self.calls

    def get_log(self, *_, **__):  # pylint: disable=no-self-use
        return []


def test_javascript_wrapper():
    driver = MockWebDriver()
    js = JavascriptWrapper(driver)

    result = js.get_full_height()
    assert result == 1

    result = js.find_iframe_name("id")
    assert result == 2

    result = js.get_element_metadata()
    assert result == 3

    result = js.hide_position_fixed_elements()
    assert result == 4

    js.show_position_fixed_elements(None)
    assert driver.calls == 5

    js.disable_animations()
    assert driver.calls == 6

    result = js.is_page_loaded()
    assert result == 7

    result = js.find_active_elements()
    assert result == 8

    js.scroll_to(0, 0)
    assert driver.calls == 9

    js.make_canvas()
    assert driver.calls == 10

    js.annotate(wtl.Point(0, 0), wtl.Color.from_str("FFFFFF"), 0, "")
    assert driver.calls == 12

    js.highlight(wtl.Selector(""), wtl.Color.from_str("FFFFFF"))
    assert driver.calls == 14

    js.clear_highlights()
    assert driver.calls == 15

    js.click_element(wtl.Selector(""))
    assert driver.calls == 16

    js.delete_element(wtl.Selector(""))
    assert driver.calls == 17

    js.fill_text(wtl.Selector(""), "")
    assert driver.calls == 18

    js.select(wtl.Selector(""), "")
    assert driver.calls == 19

    driver.to_return = {"x": 1, "y": 2, "w": 3, "h": 4}
    result = js.find_viewport()
    assert result.bounds == (1, 2, 4, 6)
    assert driver.calls == 20
