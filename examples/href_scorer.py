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
Ranks all links on a page by the length of the HREF attribute.
Does nothing with them.
"""

import webtraversallibrary as wtl
from webtraversallibrary.actions import Wait

from .util import parse_cli_args


@wtl.single_tab
def policy(_, __):
    # Wait so that the classifier isn't run over and over again
    return Wait(10)


def url_length_classifier_func(elements, _):
    # Score all elements with an href attribute with a score of the length of the href attribute
    href_elements = [element for element in elements if element.metadata["href"]]
    return [(element, len(element.metadata["href"])) for element in href_elements]


if __name__ == "__main__":
    cli_args = parse_cli_args()

    workflow = wtl.Workflow(config=wtl.Config(cli_args.config), policy=policy, url=cli_args.url, output=cli_args.output)

    workflow.classifiers.add(
        wtl.ElementClassifier(
            name="url_length",
            highlight=True,
            mode=wtl.ScalingMode.LINEAR,
            highlight_color=wtl.Color(0, 0, 255),
            callback=url_length_classifier_func,
        )
    )

    workflow.run()
    workflow.quit()
