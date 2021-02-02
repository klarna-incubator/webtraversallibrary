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

from functools import partial
from random import choice, random

import webtraversallibrary as wtl
from webtraversallibrary.actions import Click, Refresh

from .util import parse_cli_args


@wtl.single_tab
def policy(workflow: wtl.Workflow, view: wtl.View) -> wtl.Action:
    assert workflow.duplicate_loop_idx == workflow.loop_idx

    # With some small probabilty, refresh instead of clicking.
    return choice(view.actions.by_type(Click)) if random() < 0.95 else view.actions.by_type(Refresh).unique()


def set_duplicate_loop_idx(workflow: wtl.Workflow):
    workflow.duplicate_loop_idx = workflow.loop_idx


if __name__ == "__main__":
    cli_args = parse_cli_args()

    wf = wtl.Workflow(config=wtl.Config(cli_args.config), policy=policy, url=cli_args.url, output=cli_args.output)

    wf.classifiers.add(wtl.ActiveElementFilter(action=Click))

    wf.postload_callbacks.append(partial(set_duplicate_loop_idx, wf))

    wf.run()
    wf.quit()
