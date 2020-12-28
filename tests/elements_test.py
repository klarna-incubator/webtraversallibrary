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

import bs4
import pytest

import webtraversallibrary as wtl


def test_by_score_and_uid():
    elements = wtl.snapshot.Elements(
        [
            wtl.PageElement(page=None, metadata={"wtl_uid": 1, "x": 0.5}),
            wtl.PageElement(page=None, metadata={"wtl_uid": 2, "x": 0.5, "y": 0.5}),
            wtl.PageElement(page=None, metadata={"y": 0.75, "raw_scores": {"y": 2.5}}),
            wtl.PageElement(page=None, metadata={"x": 1.5, "y": 1.5, "raw_scores": {"y": 1.5}}),
        ]
    )

    x_elements = elements.by_score("x")
    assert len(x_elements) == 3

    a_elements = elements.by_score("a")
    assert not a_elements

    y_elements = elements.by_score("y", limit=1.0)
    assert len(y_elements) == 1

    y_raw_elements = elements.by_raw_score("y", limit=1.0)
    assert len(y_raw_elements) == 2

    y_raw_elements_sorted = elements.by_raw_score("y").sort_by("y")
    assert len(y_raw_elements) == 2
    assert y_raw_elements[0] == y_raw_elements_sorted[1]
    assert y_raw_elements[1] == y_raw_elements_sorted[0]

    xy_element = elements.by_uid(2)
    assert xy_element.metadata["x"] == xy_element.metadata["y"]


def test_by_selector():
    class MockSource:
        @property
        def page(self):
            return self

        @property
        def page_source(self):
            return bs4.BeautifulSoup(
                """
                <body wtl-uid="5"><div wtl-uid="1" class="hey"><a wtl-uid="2"></a><a wtl-uid="6"></a></div>
                <div wtl-uid="3"><span wtl-uid="4"></span></div></body>""",
                "html5lib",
            )

    elements = wtl.snapshot.Elements(
        [
            wtl.PageElement(page=MockSource(), metadata={"wtl_uid": 1}),
            wtl.PageElement(page=MockSource(), metadata={"wtl_uid": 2}),
            wtl.PageElement(page=MockSource(), metadata={"wtl_uid": 3}),
            wtl.PageElement(page=MockSource(), metadata={"wtl_uid": 4}),
            wtl.PageElement(page=MockSource(), metadata={"wtl_uid": 6}),
        ]
    )

    divs = elements.by_selector(wtl.Selector("div"))
    assert len(divs) == 2

    divs = elements.by_selector(wtl.Selector(".hey"))
    assert len(divs) == 1

    links = elements.by_subtree(divs[0], include_root=False)
    assert len(links) == 2

    links = elements.by_subtree(wtl.Selector(".hey"), include_root=True)
    assert len(links) == 3

    with pytest.raises(AssertionError):
        elements.by_subtree(wtl.Selector("does-not-exist"))
