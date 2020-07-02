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
Dynamically handles multiple tabs and windows.
Creates new windows and/or tabs every iteration.
"""

from random import choice
from typing import Dict

import webtraversallibrary as wtl

from .util import parse_cli_args


def policy(workflow: wtl.Workflow, view: wtl.View) -> Dict[wtl.View, wtl.Action]:
    loop_idx: int = workflow.loop_idx + 1
    window_idx: int = loop_idx // 3

    # Every third tab, create a new window, otherwise use the latest window
    if window_idx >= len(workflow.windows):
        window: wtl.window = workflow.create_window(str(window_idx))
    else:
        window: wtl.window = workflow.windows[-1]

    # Create a window to a new Wikipedia number link
    window.create_tab(str(loop_idx), url=f"https://en.wikipedia.org/wiki/{loop_idx}")

    # For every view, click a random clickable element
    return {v: choice(v.actions.by_type(wtl.actions.Click)) for v in view.values()}


if __name__ == "__main__":
    cli_args = parse_cli_args()

    wf = wtl.Workflow(
        config=wtl.Config(cli_args.config), policy=policy, url="https://en.wikipedia.org/wiki/0", output=cli_args.output
    )

    wf.classifiers.add(wtl.ActiveElementFilter(action=wtl.actions.Click))

    wf.run()
    wf.quit()
