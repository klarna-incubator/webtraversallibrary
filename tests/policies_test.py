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

from dataclasses import dataclass, field
from typing import List

import pytest

import webtraversallibrary as wtl

# pylint: disable=not-callable


@dataclass(frozen=True)
class MockView:
    name: str
    actions: List[str] = field(hash=False, default_factory=List)


def test_dummy():
    policy = wtl.policies.DUMMY

    assert policy(None, [1, 2, 3]) == {1: None, 2: None, 3: None}


def test_random():
    policy = wtl.policies.RANDOM

    a = MockView("a", [1])
    b = MockView("b", [2, 3, 4])

    p = policy(None, [a, b])
    assert len(p) == 2
    assert p[a] == 1
    assert 2 <= p[b] <= 4


def test_single_tab():
    @wtl.single_tab
    def policy(_, __):
        return "yo"

    result = policy(None, {"a": "b"})
    assert result == {"a": "yo"}


def test_single_tab_coroutine():
    @wtl.single_tab_coroutine
    def policy():
        yield
        yield 1
        yield 2
        yield 3

    p = policy()
    T = wtl.Workflow.SINGLE_TAB
    assert p(None, {T: "b"}) == {T: 1}
    assert p(None, {T: "b"}) == {T: 2}
    assert p(None, {T: "b"}) == {T: 3}

    with pytest.raises(StopIteration):
        p(None, {T: "b"})


def test_multi_tab_coroutine():
    @wtl.multi_tab_coroutine
    def policy():
        yield
        yield 1
        yield 2
        yield 3

    p = policy()
    assert p(None, {"a": "b"}) == 1
    assert p(None, {"a": "b"}) == 2
    assert p(None, {"a": "b"}) == 3

    with pytest.raises(StopIteration):
        p(None, {"a": "b"})
