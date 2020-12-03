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


def test_view_copy():
    view = wtl.View(name="abcdef", snapshot=1, actions=2, tags=3, metadata=4)

    view2 = view.copy()

    assert view2.name == view.name
    assert view2.snapshot == view.snapshot
    assert view2.actions == view.actions
    assert view2.tags == view.tags
    assert view2.metadata == view.metadata

    view3 = view.copy(no_snapshot=True)

    assert view3.name == view.name
    assert view3.snapshot is None
    assert view3.actions is None
    assert view3.tags == view.tags
    assert view3.metadata == view.metadata
