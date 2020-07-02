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
Clicks hard-coded menu items by element and selector.
"""
from typing import List

import webtraversallibrary as wtl

from .util import parse_cli_args


@wtl.single_tab
def policy(_, view: wtl.View) -> List[wtl.Action]:
    # Picking an action at random relating to one of these elements
    elements = view.snapshot.elements
    menu_elements = [e for e in elements if e.location.x < 10 and e.location.y < 200 and e.metadata["tag"] == "a"]
    actions_a: wtl.Action = view.actions.by_element(menu_elements[0])

    # Another way is doing it by selector - this one matches all the menu items (equivalent to the above)
    actions_b: wtl.Action = view.actions.by_selector(wtl.Selector(css=".sidenav div a"))

    # Click the first menu item and then, before snapshotting, the second
    return [actions_a[0], actions_b[1]]


if __name__ == "__main__":
    cli_args = parse_cli_args()

    workflow = wtl.Workflow(config=wtl.Config(cli_args.config), policy=policy, url=cli_args.url, output=cli_args.output)

    workflow.classifiers.add(wtl.ActiveElementFilter(action=wtl.actions.Click))

    workflow.run()
    workflow.quit()
