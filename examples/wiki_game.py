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

"""
Click on any random clickable element on a page.
Also demonstrates the use of postload_callbacks.
"""

from random import choice

import webtraversallibrary as wtl
from webtraversallibrary.actions import Abort, Click

from .util import parse_cli_args


@wtl.single_tab_coroutine
def policy():
    workflow, view = yield

    # Store Page A's URL
    page_a_url = workflow.current_window.driver.current_url
    workflow, view = yield Click(
        choice(view.snapshot.elements.by_subtree(wtl.Selector("div[id='bodyContent']")).by_selector(wtl.Selector("a")))
    )

    # Store Page B's URL
    page_b_url = workflow.current_window.driver.current_url

    description = ""
    # Stores first paragraph from page B's body
    try:
        description = view.snapshot.elements.by_selector(wtl.Selector("div p:nth-of-type(1)"))[0].metadata["text"]
        if description.empty:
            raise IndexError()
    except IndexError:
        description = view.snapshot.elements.by_selector(wtl.Selector("div p:nth-of-type(2)"))[0].metadata["text"]

    # Limit the description to 50 characters to improve search
    description_subset = str(description[0:49])

    # Navigate back to page A
    workflow, view = yield wtl.actions.Navigate(page_a_url)

    link_to_click = view.snapshot.elements.by_selector(wtl.Selector("input[type='submit']"))

    # In the search bar in page A, fill text with description_subset and
    # click search to get search results for the descriptions

    workflow, view = yield [
        wtl.actions.FillText(wtl.Selector("input[type='search']"), str(description_subset)),
        Click(link_to_click[0]),
    ]

    # Store search result's URL
    search_url = workflow.current_window.driver.current_url

    search_results = view.snapshot.elements.by_selector(wtl.Selector("div[class=mw-search-result-heading] a"))

    i = 0

    # Go to first link in the search result
    try:
        workflow, view = yield Click(search_results[i])
    except IndexError:
        print("Empty search results!!")
        yield Abort()

    # Check if landing URL equals PAGE B URL, if yes, break, else iterate and go to next link in the search result
    # untill the URL's match

    while True:
        if workflow.current_window.driver.current_url == page_b_url:
            print("Woohoo!!!")
            break

        try:
            workflow, view = yield [wtl.actions.Navigate(search_url), Click(search_results[i + 1])]
            i += 1
        except IndexError:
            print("Search result exhausted!!")
            break

        yield None


if __name__ == "__main__":
    cli_args = parse_cli_args()

    wf = wtl.Workflow(
        config=wtl.Config(cli_args.config),
        policy=policy,
        url="https://en.wikipedia.org/wiki/Special:Random",
        output=cli_args.output,
    )

    wf.classifiers.add(wtl.ActiveElementFilter(action=Click))

    wf.classifiers.add(wtl.ElementClassifier(name="textfield", action=wtl.actions.FillText, highlight=True))

    wf.run()
    wf.quit()
