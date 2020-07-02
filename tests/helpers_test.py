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
from webtraversallibrary.helpers import ClassifierCollection, FrameSwitcher, MonkeyPatches


class MockJavascriptWrapper:
    def __init__(self):
        self.s = None

    def find_iframe_name(self, s):
        self.s = s
        return s + "iframe"


class MockWebDriver:
    def __init__(self):
        self.f = None

    @property
    def switch_to(self):
        return self

    def frame(self, f):
        self.f = f

    def default_content(self):
        self.f = "default"


class MockSnapshot:
    def __init__(self, elements):
        self._elements = elements

    @property
    def elements(self):
        return self

    def by_selector(self, s):
        return self._elements[s.css]


def test_classifier_collection():
    collection = ClassifierCollection(
        [
            wtl.classifiers.Classifier(name="aaa", enabled=True),
            wtl.classifiers.Classifier(name="bbb", enabled=False),
            wtl.classifiers.Classifier(name="ccc", enabled=True),
        ]
    )

    assert len(collection) == 3

    ddd = wtl.classifiers.Classifier(name="ddd", enabled=False)
    collection.add(ddd)

    assert len(collection) == 4
    assert len([c for c in collection if c]) == 4
    assert ddd in collection
    assert "ddd" in collection
    assert wtl.classifiers.Classifier(name="eee") not in collection
    assert len([c for c in collection if c.enabled]) == 2

    collection.start("bbb")

    assert len([c for c in collection if c.enabled]) == 3

    collection.start(ddd)

    assert len([c for c in collection if c.enabled]) == 4

    collection.stop(ddd)

    assert len([c for c in collection if c.enabled]) == 3


def test_monkeypatches():
    patches = MonkeyPatches({wtl.Selector("aaa"): "AAA"})

    assert len(patches) == 1

    patches.add(wtl.Selector("bbb"), "BBB")

    assert len(patches) == 2
    assert wtl.Selector("aaa") in patches
    assert wtl.Selector("bbb") in patches

    e1 = wtl.snapshot.PageElement(None, {"x": 1})
    e2 = wtl.snapshot.PageElement(None, {"x": 2})
    e3 = wtl.snapshot.PageElement(None, {"x": 3})
    e4 = wtl.snapshot.PageElement(None, {"x": 4})

    snapshot = MockSnapshot({"aaa": [e1, e3], "bbb": [e2]})

    assert patches.check(snapshot, e1) == "AAA"
    assert patches.check(snapshot, e2) == "BBB"
    assert patches.check(snapshot, e3) == "AAA"
    assert not patches.check(snapshot, e4)

    patches.set_default("CCC")

    assert patches.check(snapshot, e4) == "CCC"
    assert patches.check(snapshot, e1) == "AAA"


def test_frame_switcher():
    js = MockJavascriptWrapper()
    driver = MockWebDriver()
    fs = FrameSwitcher("abc", js, driver)

    with fs:
        assert driver.f == "abciframe"

    assert fs.name == "abciframe"
    assert driver.f == "default"
