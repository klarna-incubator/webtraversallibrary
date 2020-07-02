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
Remove an element, one at a time, until the page is empty.
"""

import random
from typing import List, Union

import webtraversallibrary as wtl

from .util import parse_cli_args


@wtl.single_tab
def policy(workflow: wtl.Workflow, view: wtl.View) -> Union[wtl.Action, List[wtl.Action]]:
    # After seven deletions, start over from step 3
    if workflow.loop_idx == 7:
        return wtl.actions.Revert(3)

    # Randomly pick one of the deleting actions
    return [
        random.choice(view.actions.by_type(wtl.actions.Remove)),
        wtl.actions.Wait(0.25),
        wtl.actions.Clear(viewport=False),
        wtl.actions.WaitForUser(),
    ]


if __name__ == "__main__":
    cli_args = parse_cli_args()

    wf = wtl.Workflow(config=wtl.Config(cli_args.config), policy=policy, url=cli_args.url, output=cli_args.output)

    wf.classifiers.add(
        wtl.ElementClassifier(
            name="dementor",
            enabled=True,
            highlight=False,
            action=wtl.actions.Remove,
            callback=lambda e, _: e,  # Will label _all_ elements removable
        )
    )

    wf.run()
    wf.quit()
