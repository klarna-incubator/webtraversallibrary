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

from dataclasses import dataclass

import bs4
import pytest

import webtraversallibrary as wtl


def test_by_type():
    actions = wtl.actions.Actions(
        [
            wtl.actions.Refresh(),
            wtl.actions.Click(),
            wtl.actions.Click(wtl.Selector("abc")),
            wtl.actions.FillText(wtl.Selector("ghi")),
            wtl.actions.FillText(),
            wtl.actions.Navigate(),
        ]
    )

    assert len(actions) == 6

    click_actions = actions.by_type(wtl.actions.Click)
    assert len(click_actions) == 2

    fill_text_actions = actions.by_type(wtl.actions.FillText)
    assert len(fill_text_actions) == 2

    element_actions = actions.by_type(wtl.actions.ElementAction)
    assert len(element_actions) == 4


def test_by_score():
    actions = wtl.actions.Actions(
        [
            wtl.actions.Refresh(),
            wtl.actions.Click(wtl.PageElement(page=None, metadata={"x": 0.5, "raw_scores": {"x": 2.5}})),
            wtl.actions.Click(wtl.PageElement(page=None, metadata={"x": 0.5, "y": 0.5})),
            wtl.actions.FillText(wtl.PageElement(page=None, metadata={"y": 0.75, "raw_scores": {"y": 2.5}})),
            wtl.actions.FillText(wtl.PageElement(page=None, metadata={"x": 1.5, "y": 1.5, "raw_scores": {"y": 1.5}})),
            wtl.actions.Navigate(),
        ]
    )

    x_actions = actions.by_score("x")
    assert len(x_actions) == 3

    x_actions_sorted = actions.by_score("x").sort_by("x")
    assert len(x_actions_sorted) == 3
    assert x_actions[0] == x_actions_sorted[2]
    assert x_actions[2] != x_actions_sorted[0]

    a_actions = actions.by_score("a")
    assert not a_actions

    y_actions = actions.by_score("y", limit=1.0)
    assert len(y_actions) == 1

    y_raw_actions = actions.by_raw_score("y", limit=1.0)
    assert len(y_raw_actions) == 2

    b_actions = actions.by_raw_score("b")
    assert not b_actions


def test_by_selector():
    class MockSource:
        @property
        def page(self):
            return self

        @property
        def page_source(self):
            return bs4.BeautifulSoup(
                """
<body wtl-uid="5"><div wtl-uid="1" class="hey"><a wtl-uid="2"></a></div>
<div wtl-uid="3"><span wtl-uid="4"></span></div></body>""",
                "html5lib",
            )

    actions = wtl.actions.Actions(
        [
            wtl.actions.Refresh(),
            wtl.actions.Click(wtl.PageElement(page=MockSource(), metadata={"wtl_uid": 1})),
            wtl.actions.FillText(wtl.PageElement(page=MockSource(), metadata={"wtl_uid": 3})),
            wtl.actions.Navigate(),
        ]
    )

    divs = actions.by_selector(wtl.Selector("div"))
    assert len(divs) == 2

    divs = actions.by_selector(wtl.Selector(".hey"))
    assert len(divs) == 1

    divs = actions.by_selector(wtl.Selector("#yo"))
    assert not divs


def test_page_actions():
    navigate = wtl.actions.Navigate()
    navigate_2 = navigate("www.google.com")
    assert navigate.url == ""
    assert navigate_2.url == "www.google.com"

    navigate = wtl.actions.Wait(1)
    navigate_2 = navigate(3)
    assert navigate.seconds == 1
    assert navigate_2.seconds == 3


def test_transformed_to_element():
    @dataclass
    class Temp:
        x: int

    class MockElements:
        def __init__(self, results=3):
            self._results = results

        def by_selector(self, s):
            return [Temp(len(s.css))] * self._results

    element_action = wtl.actions.Click(wtl.Selector("abc"))
    element_action = element_action.transformed_to_element(MockElements())
    assert element_action.target.x == 3

    with pytest.raises(AssertionError):
        element_action = element_action.transformed_to_element(MockElements(0))
