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
import shutil
import subprocess
from pathlib import Path

import pytest
from xvfbwrapper import Xvfb

import webtraversallibrary as wtl

TESTURL = "http://localhost:5000"


@pytest.fixture(scope="session", autouse=True)
def mock_merchant_website(request):
    my_env = os.environ.copy()
    my_env["FLASK_APP"] = "tests/site/flask_app.py"
    server = subprocess.Popen("python3 -m flask run".split(), env=my_env)
    request.addfinalizer(server.terminate)


@wtl.single_tab_coroutine
def test_policy():
    yield
    yield None


@pytest.mark.system
def test_mhtml_export():
    OUTPUT_DIR = Path("./mhtml/")

    with Xvfb():
        workflow = wtl.Workflow(
            url=TESTURL,
            policy=test_policy,
            config=wtl.Config(["default", "browser.enable_mhtml=True", "scraping.save_mhtml=True", "debug.save=True"]),
            output=OUTPUT_DIR,
        )
        workflow.run()

    assert (OUTPUT_DIR / "0" / "page.mhtml").exists()
    assert (OUTPUT_DIR / "1" / "page.mhtml").exists()
    assert os.stat(OUTPUT_DIR / "0" / "page.mhtml").st_size
    assert os.stat(OUTPUT_DIR / "1" / "page.mhtml").st_size

    shutil.rmtree(OUTPUT_DIR)
