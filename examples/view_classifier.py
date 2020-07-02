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
Clicks randomly on a page until _dataguy_ is not part of the URL anymore, using a ViewClassifier.
"""

from random import choice
from typing import List, Set

import webtraversallibrary as wtl
from webtraversallibrary.actions import Annotate, Clear, Click

from .util import parse_cli_args


@wtl.single_tab
def goal(_, view):
    # Stop when we dataguy is not part of the URL
    return "dataguy" not in view.tags


@wtl.single_tab
def policy(_, view: wtl.View) -> List[wtl.Action]:
    # Do any random click
    return [
        Clear(),
        Annotate(
            location=wtl.Point(30, 30),
            color=wtl.Color(0, 0, 0),
            size=20,
            text="Still dataguy",
            background=wtl.Color(128, 50, 128),
        ),
        choice(view.actions.by_type(Click)),
    ]


def dataguy_classifier_func(view: wtl.View) -> Set[str]:
    # This will assign "dataguy" to a view if the URL contains that, otherwise "other"
    # It can be retreived with view.tags
    return {"dataguy" if "dataguy" in view.snapshot.page_metadata["url"] else "other"}


if __name__ == "__main__":
    cli_args = parse_cli_args()

    workflow = wtl.Workflow(config=wtl.Config(cli_args.config), policy=policy, url=cli_args.url, output=cli_args.output)

    workflow.classifiers.add(wtl.ActiveElementFilter(action=Click))

    # The syntax for a ViewClassifier is similar, but simpler
    workflow.classifiers.add(wtl.ViewClassifier(name="dataguy", callback=dataguy_classifier_func))

    workflow.run()
    workflow.quit()
