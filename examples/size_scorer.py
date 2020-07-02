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
Classifies active elements with a "size score" and then clicks some element with average size.
"""

from random import choice
from typing import Dict

import webtraversallibrary as wtl
from webtraversallibrary.actions import Click

from .util import parse_cli_args


@wtl.single_tab
def policy(_, view: wtl.View) -> wtl.Action:
    return choice(view.actions.by_type(Click).by_score("size__average"))


def size_classifier_func(elements: wtl.Elements, _) -> Dict[str, float]:
    # Computes a normalized size.
    # Note that this is not the simplest way of clicking the largest clickable element.

    largest_area = max(e.bounds.area for e in elements)

    def score(element):
        return element.bounds.area / largest_area

    return {
        "big": [(e, score(e)) for e in elements if score(e) > 0.75],
        "average": [(e, abs(0.5 - score(e))) for e in elements if 0.25 < score(e) <= 0.75],
    }


if __name__ == "__main__":
    cli_args = parse_cli_args()

    workflow = wtl.Workflow(config=wtl.Config(cli_args.config), policy=policy, url=cli_args.url, output=cli_args.output)

    workflow.classifiers.add(wtl.ActiveElementFilter())

    workflow.classifiers.add(
        wtl.ElementClassifier(
            name="size", subset="is_active", highlight=0.5, action=Click, callback=size_classifier_func
        )
    )

    with workflow:
        workflow.run()
