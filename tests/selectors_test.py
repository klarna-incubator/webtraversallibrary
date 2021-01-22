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

from webtraversallibrary.selector import Selector


def test_selector_ordering():
    # This is the order in which selectors must be sorted
    selectors = [
        Selector(css="a"),
        Selector(css="b"),
        Selector(css="bb"),
        Selector(css="a b"),
        Selector(css="a.x"),
        Selector(css="aaaa"),
    ]

    assert sorted(selectors) == selectors


def test_selector_build():
    # Simple case
    source = """<html><body><div class="hi"></div></body></html>"""
    soup = bs4.BeautifulSoup(source, "html5lib")
    element = soup.body.select("div")[0]
    selector = Selector.build(soup, element)
    assert selector.css == "html>body>div"
    selector = Selector.build(soup, element)
    assert selector.css == "html>body>div"

    # Complex nesting
    source = """<html><body>
<a></a>
<div><a></a></div>
</body></html>"""
    soup = bs4.BeautifulSoup(source, "html5lib")
    elements = soup.body.select("a")
    selector = Selector.build(soup, elements[0])
    assert selector.css == "html>body>a"

    selector = Selector.build(soup, elements[1])
    assert selector.css == "html>body>div>a"

    # Deeply nested
    source = """<html><body>
<div class="a" wtl-uid="12"><div><div class="b"><div class="c"><div class="d"><div class="e"><div class="f">
<span>Hi</span>
</div></div></div></div></div></div></div>
<div class="a"><div><div class="b"><div class="c"><div class="d"><div class="f">
<span>Howdy</span>
</div></div></div></div></div></div></div>
</body></html>"""
    soup = bs4.BeautifulSoup(source, "html5lib")
    element = soup.body.select(".e span")[0]
    selector = Selector.build(soup, element)
    assert selector.css == "html>body>div:nth-of-type(1)>div>div>div>div>div>div>span"
    selector = Selector.build(soup, element)
    assert selector.css == "html>body>div:nth-of-type(1)>div>div>div>div>div>div>span"

    element = soup.body.select(".d > .f > span")[0]
    selector = Selector.build(soup, element)
    assert selector.css == "html>body>div:nth-of-type(2)>div>div>div>div>div>span"

    selector = Selector.build(soup, 12)
    assert selector.css == "html>body>div:nth-of-type(1)"

    # Unsafe names
    source = """<html><body>
<div:nonstandard><a></a></div>
</body></html>"""
    soup = bs4.BeautifulSoup(source, "html5lib")
    element = soup.body.select("a")[0]
    selector = Selector.build(soup, element)
    assert selector.css == "html>body>*>a"

    # Invalid WTL-uid
    selector = Selector.build(soup, 23)
    assert selector.css == "bad_wtl_uid_no_matches"
