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

from webtraversallibrary.snapshot import Elements, PageElement


def test_page_element():
    location = {"x": 12, "y": 13}
    size = {"width": 10, "height": 11}
    element = PageElement(None, {"location": location, "size": size})

    assert element.location.x == 12
    assert element.location.y == 13

    assert element.size.x == 10
    assert element.size.y == 11

    assert element.bounds.area == 110


def test_parse_resolved_size():
    assert PageElement.parse_resolved_size("12px") == 12.0
    assert PageElement.parse_resolved_size(" 9px ") == 9.0
    assert PageElement.parse_resolved_size("1.2px") == 1.2


def test_uid_and_parent():
    class FakePage:
        def __init__(self):
            self.elements = None

    page = FakePage()

    a = PageElement(page, {"wtl_uid": 1, "wtl_parent_uid": 23})
    b = PageElement(page, {"wtl_uid": 23, "wtl_parent_uid": 35})
    c = PageElement(page, {"wtl_uid": 35, "wtl_parent_uid": -1})

    assert b.wtl_uid == 23
    assert b.wtl_parent_uid == 35

    page.elements = Elements([b, c, a])

    assert a.parent == b
    assert b.parent == c
    assert c.parent is None
