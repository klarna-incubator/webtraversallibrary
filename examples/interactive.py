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
Simple example of an interactive "game", as an old-style text RPG, for web traversal.
"""

import logging
import random
from typing import List

import webtraversallibrary as wtl

from .util import parse_cli_args

initials = [
    "You see a house. Above the door hangs a sign: ",
    "You are in an open field. You find a note that says: ",
    "You are inside an old cottage. On the wall you see something written: ",
    "You are standing in the wtl office. It is loud. One of the screens say: ",
    "Rain is pouring through the broken roof. The rain patters a sound. You make out: ",
]


textfield_desc = [
    "A wild Croatian appears and asks you for a name. He hands you a paper and pen to write with.",
    "An empty notepad really wants something to be written.",
    "You see a dusty whiteboard with a pen that still works.",
    "A piece of paper is asking you what is on your mind. You have a pen in your hand.",
]


vague_desc = [
    "You can see people in the distance.",
    "wtluts are ringing a bell.",
    "Everything around you looks really clean.",
    "There are multiple paths forward.",
]


content_desc = [
    "A bleached old parchment says: ",
    "A pretty little note by your feet says: ",
    "You find an old metal bracelet with an inscription: ",
    "You are standing next to an old radio. When you try turning it on, it repeats over and over again: ",
]


@wtl.single_tab_coroutine
def policy():
    print("\n === === === \n")
    _, view = yield
    initial = random.choice(initials)
    spoken = False

    while True:
        if not spoken:
            title = view.snapshot.page_metadata["title"]
            print(f'{initial}"{title}"')
            spoken = True
        cmd = input("\n> ").strip().split(" ")
        action = None

        if cmd[0] == "help":
            print("\nAvailable commands:\nhelp: shows this message")
            continue

        if cmd[0] == "navigate" or cmd[0] == "jump":
            action = wtl.actions.Navigate(cmd[1])

        if cmd[0] == "look":
            buttons = view.actions.by_type(wtl.actions.Click)
            textfields = [v for v in view.actions.by_type(wtl.actions.FillText) if v.target.metadata["text"] == ""]
            texts = (
                view.snapshot.elements.by_selector(wtl.Selector("h1"))
                + view.snapshot.elements.by_selector(wtl.Selector("h2"))
                + view.snapshot.elements.by_selector(wtl.Selector("h3"))
                + view.snapshot.elements.by_selector(wtl.Selector("p"))
            )

            if textfields:
                print(random.choice(textfield_desc))

            elif buttons:
                print(random.choice(vague_desc))

            if texts:
                print(random.choice(content_desc) + '"' + random.choice(texts).metadata["text"] + '"')

            continue

        if cmd[0] == "click":
            text = " ".join(cmd[1:])
            elements = view.snapshot.elements.by_selector(wtl.Selector(f'[value~="{text}"]'))
            if not elements:
                elements = [e for e in view.snapshot.elements if text in e.metadata["text"]]
            if not elements:
                elements = view.snapshot.elements.by_selector(wtl.Selector(text))
            if elements:
                action = wtl.actions.Click(random.choice(elements))

        if cmd[0] == "move":
            action = random.choice(view.actions.by_type(wtl.actions.Click))
            initial = random.choice(initials)

        if cmd[0] == "write":
            textfields = [v for v in view.actions.by_type(wtl.actions.FillText) if v.target.metadata["text"] == ""]
            action = random.choice(textfields)(" ".join(cmd[1:]))

        if not action:
            print("I do not understand.")
            continue

        spoken = False
        _, view = yield action


def text_field_classifier_func(elements: wtl.Elements, _) -> List[wtl.PageElement]:
    return [e for e in elements if e.metadata["tag"] == "input" and e.metadata["type"] in ("text", "email", "password")]


if __name__ == "__main__":
    cli_args = parse_cli_args()

    workflow = wtl.Workflow(config=wtl.Config(cli_args.config), policy=policy, url=cli_args.url, output=cli_args.output)

    workflow.classifiers.add(wtl.ActiveElementFilter(action=wtl.actions.Click))
    workflow.classifiers.add(
        wtl.ElementClassifier(
            name="textfield", action=wtl.actions.FillText, callback=text_field_classifier_func, highlight=True
        )
    )

    logging.getLogger("wtl").setLevel(logging.ERROR)

    workflow.run()
    workflow.quit()
