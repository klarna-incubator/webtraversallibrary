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

from webtraversallibrary.config import Config
from webtraversallibrary.snapshot import PageSnapshot

# Pylint doesn't understand dataclasses just yet
# pylint: disable=unsubscriptable-object


def test_page_snapshot():
    source = """
<body>
    <div wtl-uid=12>
        <p wtl-uid=15></p>
        <p wtl-uid=19></p>
        <p wtl-uid=7></p>
    </div>
</body>
"""

    metadata = [
        {"wtl_uid": 12, "x": "hi"},
        {"wtl_uid": 15, "x": "hello"},
        {"wtl_uid": 7, "x": "whatup"},
        {"wtl_uid": 19, "x": "shoo bre"},
    ]

    snapshot = PageSnapshot(bs4.BeautifulSoup(source, Config.default().bs_html_parser), {}, metadata)

    assert snapshot.elements
    assert len(snapshot.elements) == 4

    assert str(snapshot.elements[1].tag) == '<p wtl-uid="15"></p>'
