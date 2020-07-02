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
Simple example showing a hard-coded generator of actions.
"""

import webtraversallibrary as wtl
from webtraversallibrary.actions import Clear, Click, Highlight

from .util import parse_cli_args, start_server


@wtl.single_tab_coroutine
def policy():
    # Highlight some titles, and then click a menu item.
    # Once the generator is exhausted, workflow will interpret StopIteration as cancelling the tabs.

    yield
    for i in range(1, 6):
        yield [Clear(), Highlight(target=wtl.Selector(f"h2:nth-of-type({i}) > a"))]
    yield Click(wtl.Selector("h2:nth-of-type(1) > a"))


if __name__ == "__main__":
    cli_args = parse_cli_args()

    workflow = wtl.Workflow(
        config=wtl.Config(cli_args.config), policy=policy, url=start_server() + "/blog", output=cli_args.output
    )

    workflow.run()
    workflow.quit()
