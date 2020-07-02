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
Randomly fill all random text input fields on a page with a preset list of names.
"""

from random import choice
from typing import List

import webtraversallibrary as wtl
from webtraversallibrary.actions import Clear, FillText

from .util import parse_cli_args


@wtl.single_tab
def goal(_, view: wtl.View) -> bool:
    # Find all elements we could fill in text on
    targets: List[wtl.Action] = [action.target for action in view.actions.by_type(FillText)]
    # Get all their collective contents
    texts: str = [element.metadata["text"] for element in targets]
    # Stop running if they have all been filled
    return all(t != "" for t in texts)


content = ["Robin Carpenter", "Kenny Turner", "Ernestine Ferguson", "Marcelo Allen", "Marilyn Rich", "Rupert Strong"]


@wtl.single_tab
def policy(_, view: wtl.View) -> List[wtl.Action]:
    # Filter out all the FillText actions where the element is still empty
    fill_actions: List[wtl.Action] = [
        action for action in view.actions.by_type(FillText) if not action.target.metadata["text"]
    ]
    # Randomly pick an action and a text
    action: wtl.Action = choice(fill_actions)
    text: str = choice(content)
    # Execute
    return [Clear(), action(text)]


def text_field_classifier_func(elements: wtl.Elements, _) -> List[wtl.PageElement]:
    # For now, we consider all input fields where the type attribute has a specific value.
    return [e for e in elements if e.metadata["tag"] == "input" and e.metadata["type"] in ("text", "email", "password")]


if __name__ == "__main__":
    cli_args = parse_cli_args()

    workflow = wtl.Workflow(
        config=wtl.Config(cli_args.config),
        policy=policy,
        goal=goal,
        url="https://www.getharvest.com/signup",
        output=cli_args.output,
    )

    # We just need a text field classifier, no need to consider what's active (all of them should be).
    workflow.classifiers.add(
        wtl.ElementClassifier(name="textfield", action=FillText, callback=text_field_classifier_func, highlight=True)
    )

    workflow.run()
    workflow.quit()

    print("Workflow successful?", workflow.success)

    # This is the last view, i.e. the one where goal() returned True
    final_view: wtl.View = workflow.history[-1]

    # Get all texts
    final_texts: List[str] = [action.target.metadata["text"] for action in final_view.actions.by_type(FillText)]

    print("Names entered: ", ", ".join(final_texts))
