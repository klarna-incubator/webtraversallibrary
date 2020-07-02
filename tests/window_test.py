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

import pytest

import webtraversallibrary as wtl


def test_window():
    config = wtl.Config.default(["headless"])
    window = wtl.Window(config=config)
    assert window.driver is not None

    assert len(window.tabs) == 0

    window.create_tab("tab1")
    assert len(window.tabs) == 1
    assert not window.is_closed("tab1")

    window.create_tab("tab2")
    assert len(window.tabs) == 2
    assert not window.is_closed("tab2")

    window.create_tab("tab3")
    assert len(window.tabs) == 3
    assert not window.is_closed("tab3")

    window.set_tab("tab2")
    window.close_tab()
    assert len(window.tabs) == 3
    assert len(window.open_tabs) == 2
    assert window.is_closed("tab2")

    assert window.open_tabs == ["tab1", "tab3"]

    window.quit()

    with pytest.raises(wtl.Error):
        window.ensure_running()

    with pytest.raises(wtl.Error):
        window.create_tab("tab4")

    window.quit()
