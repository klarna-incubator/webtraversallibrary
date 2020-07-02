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
Compute the zIndex of all active elements and highlights the top 1% elements.
"""

import logging
from typing import List, Tuple

import webtraversallibrary as wtl
from webtraversallibrary.logging import setup_logging

from .util import parse_cli_args


@wtl.single_tab
def policy(_, __) -> wtl.Action:
    return wtl.actions.WaitForUser()


# https://stackoverflow.com/questions/1388007/getting-the-z-index-of-a-div-in-javascript
Z_INDEX_JS = """
window.getZIndex = function (e) {
  if (e === null) {
    return 0;
  }
  let z = window.document.defaultView.getComputedStyle(e).getPropertyValue('z-index');
  if (isNaN(z)) {
    return window.getZIndex(e.parentElement);
  }
  return z;
};
console.log("Hello!");
let element = document.querySelector(arguments[0]);
if (element !== null) {
  return window.getZIndex(element);
}
"""


def _compute_z_index(elements: wtl.Elements, workflow: wtl.Workflow) -> List[Tuple[wtl.PageElement, float]]:
    # This may be slow for many elements. If you need more performance, consider a JS script
    # which computes all elements' z-values combined and returns the map directly.
    result = []
    for e in elements:
        zIndex = workflow.js.execute_script(Z_INDEX_JS, e.selector.css) or 0
        result.append((e, int(zIndex)))
    return result


if __name__ == "__main__":
    cli_args = parse_cli_args()

    wf = wtl.Workflow(config=wtl.Config(cli_args.config), policy=policy, url=cli_args.url, output=cli_args.output)

    wf.classifiers.add(wtl.ActiveElementFilter(action=wtl.actions.Click))

    wf.classifiers.add(
        wtl.ElementClassifier(
            name="zIndex",
            subset="is_active",
            enabled=True,
            highlight=0.99,
            mode=wtl.ScalingMode.LINEAR,
            callback=_compute_z_index,
        )
    )

    setup_logging(logging_level=logging.DEBUG)

    wf.run()
    wf.quit()
