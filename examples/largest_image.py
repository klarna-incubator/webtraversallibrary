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
Ranks all images on a page by their geometric size.
Clicks on the largest, then checks if the URL changed, then stops.
"""
from typing import Optional

import webtraversallibrary as wtl
from webtraversallibrary.actions import Click
from webtraversallibrary.goals import N_STEPS

from .util import parse_cli_args

goal = N_STEPS(2)


@wtl.single_tab
def policy(workflow: wtl.Workflow, view: wtl.View) -> Optional[wtl.Action]:
    if len(workflow.history) == 1:
        images_by_size = sorted(
            view.snapshot.elements.by_score("image"), key=lambda element: element.bounds.area, reverse=True
        )
        return Click(images_by_size[0])

    print("\n", view.snapshot.page_metadata["url"] != workflow.history[0].snapshot.page_metadata["url"], "\n")
    return None


def image_classifier_func(elements, _):
    return [elem for elem in elements if elem.metadata["tag"] == "img"]


if __name__ == "__main__":
    cli_args = parse_cli_args()

    wf = wtl.Workflow(
        config=wtl.Config(cli_args.config), policy=policy, goal=goal, url=cli_args.url, output=cli_args.output
    )

    wf.classifiers.add(wtl.ElementClassifier(name="image", highlight=True, callback=image_classifier_func))

    wf.run()
    wf.quit()
