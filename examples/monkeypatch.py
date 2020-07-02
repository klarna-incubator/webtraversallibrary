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
Click any active element, but all links lead to Rome, literally, using workflow.monkeypatches.
"""

from random import choice

import webtraversallibrary as wtl
from webtraversallibrary.actions import Click

from .util import parse_cli_args


@wtl.single_tab
def policy(_, view: wtl.View) -> wtl.Action:
    menu_actions = view.actions.by_type(Click).by_score("is_active")
    return choice(menu_actions)


if __name__ == "__main__":
    cli_args = parse_cli_args()

    workflow = wtl.Workflow(config=wtl.Config(cli_args.config), policy=policy, url=cli_args.url, output=cli_args.output)

    workflow.monkeypatches.set_default("https://en.wikipedia.org/wiki/Rome")

    workflow.classifiers.add(wtl.ActiveElementFilter(action=Click))

    workflow.run()
    workflow.quit()
