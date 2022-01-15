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


class MockWebDriver:
    @property
    def title(self):
        return "Website title"

    @property
    def current_url(self):
        return "Current URL"

    @property
    def name(self):
        return "Driver name"

    def get(self, *_):
        pass

    def find_element(self, *_):
        return self

    def refresh(self):
        pass

    def get_attribute(self, *_):
        return "<div>Hello</div>"

    def get_log(self, _):
        return []

    def execute_script(self, *_, **__):
        return None


def test_simple():
    config = wtl.Config.default()
    config.scraping.page_load_timeout = 1
    config.scraping.prescroll = True

    driver = MockWebDriver()
    scraper = wtl.Scraper(driver, config)
    assert scraper

    scraper.navigate("some url")
    scraper.refresh()

    page = scraper.scrape_current_page()
    assert str(page.page_source) == "<!DOCTYPE html>\n<html><head></head><body><div>Hello</div></body></html>"
    assert page.page_metadata
    assert not page.elements
    assert not page.elements_metadata
    assert not page.screenshots
    assert page.mhtml_source is None

    mhtml_page = scraper.get_page_as_mhtml()
    assert mhtml_page is None
