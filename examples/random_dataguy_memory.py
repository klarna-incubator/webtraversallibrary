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
Defines a subset of all active elements (menu items) and clicks randomly on those exactly once.
When they have all been clicked, abort the workflow.
"""

from random import choice
from typing import List

import webtraversallibrary as wtl
from webtraversallibrary.actions import Abort, Click

from .util import parse_cli_args


@wtl.single_tab
def policy(workflow: wtl.Workflow, view: wtl.View) -> wtl.Action:
    if "previous" not in view.metadata:
        view.metadata["previous"] = []
    else:
        workflow.js.annotate(
            wtl.Point(100, 100), wtl.Color(0, 0, 0), 30, "This is an annotation", wtl.Color(128, 128, 128, 128)
        )

        if workflow.config.debug.screenshots:
            # Create screenshot of previous actions with an emphasis on the latest
            scr = view.snapshot.new_screenshot("history", of="full")
            for prev in view.metadata["previous"]:
                scr.highlight(prev.bounds, color=wtl.Color(255, 0, 0, 100))
            scr.highlight(
                view.metadata["previous_action"][0].target.bounds, text="Latest action", color=wtl.Color(0, 0, 255, 100)
            )
            scr.save(workflow.output_path)

            # Save screenshot of the current live view
            workflow.scraper.capture_screenshot("live").save(workflow.output_path)

    # Get all elements tagged as "menu"
    menu_elements = view.snapshot.elements.by_score("menu")

    # Filter out those we have already clicked on
    menu_elements = [
        e for e in menu_elements if e.metadata["text"] not in [e.metadata["text"] for e in view.metadata["previous"]]
    ]

    if menu_elements:
        # If there are any left, click that and remember its text
        element = choice(menu_elements)
        action = Click(element)
        view.metadata["previous"].append(element)
    else:
        # Otherwise, stop everything
        action = Abort()

    # Return
    print("Here are the buttons I've clicked: ", [e.metadata["text"] for e in view.metadata["previous"]])
    print("Last time I did", view.metadata["previous_action"][0])
    return action


def menu_classifier_func(elements: wtl.Elements, _) -> List[wtl.PageElement]:
    # The condition here is completely hard-coded for the given page.
    return [elem for elem in elements if elem.location.x < 10 and elem.location.y < 200 and elem.metadata["tag"] == "a"]


if __name__ == "__main__":
    cli_args = parse_cli_args()

    wf = wtl.Workflow(config=wtl.Config(cli_args.config), policy=policy, url=cli_args.url, output=cli_args.output)

    wf.classifiers.add(wtl.ActiveElementFilter(action=Click))

    wf.classifiers.add(
        wtl.ElementClassifier(
            name="menu",
            action=Click,
            subset="is_active",  # Consider only active elements
            highlight=True,
            callback=menu_classifier_func,
        )
    )

    wf.run()
    wf.quit()
