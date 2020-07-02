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

"""Contains built-in simple, common policies and helper decorators for building custom policies."""


import random
from functools import wraps

from .workflow import Workflow


def DUMMY(_workflow, view):
    """Never takes any action."""
    return {v: None for v in view}


def RANDOM(_workflow, view):
    """Picks a completely random (available) action for every view."""
    return {v: random.choice(v.actions) for v in view}


def single_tab(func):
    """
    Decorator for simplifying policies or goals when just one tab is in use.
    Simplifies the API, the views (dict) argument is replaced by the single (first) view instance.
    Also, the policy can now just return action (or list of actions) without a dict mapping.
    """

    @wraps(func)
    def wrapper(workflow, view):
        assert len(view.keys()) == 1
        tab = list(view.keys())[0]
        result = func(workflow, view[tab])
        return {tab: result}

    return wrapper


class _PolicyCoroutine:
    """
    Wrapper for writing coroutines/generators that work as policy functions.
    Do not use directly, instead refer to `single_tab_coroutine` and `multi_tab_coroutine` decorators.
    """

    def __init__(self, p, single: bool):
        self.p = p()
        self.p.send(None)
        self.single = single

    def __call__(self, workflow, view):
        if self.single:
            result = self.p.send((workflow, view[Workflow.SINGLE_TAB]))
            return {Workflow.SINGLE_TAB: result}

        return self.p.send((workflow, view))


def single_tab_coroutine(policy):
    """
    Decorator for simplifying policies given by a generator/coroutine on a single tab.
    Interface will be the same as when using @single_tab for normal functions.
    Allows you to yield from the policy and pass the reference to the function/coroutine
    as you would for a normal method, without instantiating an object.
    """

    def __wtl_wrapped():
        return _PolicyCoroutine(policy, single=True)

    return __wtl_wrapped


def multi_tab_coroutine(policy):
    """
    Decorator for simplifying policies given by a generator/coroutine on multiple tabs.
    Allows you to yield from the policy and pass the reference to the function/coroutine
    as you would for a normal method, without instantiating an object.
    """

    def __wtl_wrapped():
        return _PolicyCoroutine(policy, single=False)

    return __wtl_wrapped
