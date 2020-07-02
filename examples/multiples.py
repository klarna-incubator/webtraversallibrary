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
Creates a total of three tabs in two windows, and clicks randomly on all of them.
"""

from random import choice
from typing import Dict

import webtraversallibrary as wtl

from .util import parse_cli_args


def policy(_, view: wtl.View) -> Dict[wtl.View, wtl.Action]:
    return {v: choice(v.actions.by_type(wtl.actions.Click)) for v in view.values()}


if __name__ == "__main__":
    cli_args = parse_cli_args()

    workflow = wtl.Workflow(
        config=wtl.Config(cli_args.config),
        policy=policy,
        url={
            "first": {"A": "www.uppsalahandkraft.se", "B": "https://www.uppsalamodemassa.se"},
            "second": {"C": "shop.biskopsgarden.com"},
        },
        output=cli_args.output,
    )

    workflow.classifiers.add(wtl.ActiveElementFilter(action=wtl.actions.Click))

    workflow.run()
    workflow.quit()
