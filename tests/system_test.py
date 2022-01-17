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

import os
import random
import subprocess

import pytest

import webtraversallibrary as wtl
from webtraversallibrary.actions import Abort, Click, Wait
from webtraversallibrary.config import Config
from webtraversallibrary.error import Error

TESTURL = "http://localhost:5000"


@pytest.fixture(scope="session", autouse=True)
def mock_merchant_website(request):
    my_env = os.environ.copy()
    my_env["FLASK_APP"] = "tests/site/flask_app.py"
    server = subprocess.Popen("python3 -m flask run".split(), env=my_env)
    request.addfinalizer(server.terminate)


browsers = [None, "desktop"] + (["firefox_mobile", "firefox_desktop"] if os.name != "nt" else [])


@pytest.mark.parametrize("browser", browsers)
@pytest.mark.system
def test_simple(browser):
    # Just navigate to a single tab, do nothing.

    config = Config.default(["headless", browser])

    workflow = wtl.Workflow(
        url=TESTURL,
        config=config,
        policy=lambda *_, **__: {wtl.Workflow.SINGLE_TAB: Wait(1)},
        goal=wtl.goals.N_STEPS(3),
    )

    workflow.run()
    assert workflow.success

    workflow.quit()
    with pytest.raises(Error):
        workflow.run()


@pytest.mark.system
def test_abort():
    # Abort a workflow

    config = Config.default(["headless"])

    workflow = wtl.Workflow(
        url=TESTURL,
        config=config,
        policy=lambda *_, **__: {wtl.Workflow.SINGLE_TAB: Abort()},
        goal=wtl.goals.N_STEPS(3),
    )

    workflow.run()
    assert not workflow.success
    workflow.quit()


@pytest.mark.system
def test_multiple():
    config = Config.default(["headless"])

    @wtl.multi_tab_coroutine
    def policy():
        yield
        _, views = yield {}
        urls = set(v.snapshot.page_metadata["url"] for v in views.values())
        print([v.snapshot.page_metadata["url"] for v in views.values()])
        assert len(urls) == 1

        _, views = yield {
            "1": wtl.actions.Click(wtl.Selector(".sidenav a:nth-of-type(2)")),
            "2": None,
            "3": wtl.actions.Click(wtl.Selector(".sidenav a:nth-of-type(3)")),
            "4": None,
        }
        urls = set(v.snapshot.page_metadata["url"] for v in views.values())
        print([v.snapshot.page_metadata["url"] for v in views.values()])
        assert len(urls) == 3

        _, views = yield {"4": wtl.actions.Click(wtl.Selector(".sidenav a:nth-of-type(4)"))}
        urls = set(v.snapshot.page_metadata["url"] for v in views.values())
        assert len(urls) == 4

        yield {}

    workflow = wtl.Workflow(
        url={"A": {"1": TESTURL, "2": TESTURL}, "C": {"3": TESTURL, "4": TESTURL}}, config=config, policy=policy
    )

    workflow.run()
    assert workflow.loop_idx == 4
    workflow.quit()


@pytest.mark.system
def test_complex():
    @wtl.single_tab
    def policy(w, view):
        menu_actions = view.actions.by_type(Click).by_score("menu")
        w.metadata["clicks"] = w.metadata["clicks"] + 1
        return random.choice(menu_actions)

    def menu_classifier_func(elements, _):
        return [
            elem for elem in elements if elem.location.x < 10 and elem.location.y < 200 and elem.metadata["tag"] == "a"
        ]

    config = Config.default(["headless", "desktop"])

    workflow = wtl.Workflow(url=TESTURL, config=config, policy=policy, goal=wtl.goals.N_STEPS(3))
    workflow.metadata["clicks"] = 0
    workflow.classifiers.add(wtl.ActiveElementFilter(action=Click))
    workflow.classifiers.add(
        wtl.ElementClassifier(
            name="menu", action=Click, subset="is_active", highlight=True, callback=menu_classifier_func
        )
    )

    workflow.run()
    assert workflow.success
    assert workflow.metadata["clicks"] == 3
    workflow.quit()
