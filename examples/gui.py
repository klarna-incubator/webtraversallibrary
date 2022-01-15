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
Basic example of using WTL together with a graphical frontend.
"""

# pylint: disable=global-statement

import tkinter as tk
from pathlib import Path
from threading import Lock, Thread
from time import sleep
from tkinter import font

import webtraversallibrary as wtl

from .util import parse_cli_args

# === THREAD SYNC ===
# Global variables used for communicating.
# Uses a single lock for everything.
# 0=Waiting for new view, 1=Update GUI image, 2=Waiting for new action

data_lock = Lock()
current_view = None
current_action = None
state = 0


# === WTL THREAD ===
# Running WTL in a separate thread (so GUI can run on the main thread).
# Very simple state machine that saves the current view and busy waits
# until an action has been set from the GUI.


@wtl.single_tab
def policy(_, view: wtl.View) -> wtl.Action:
    global state, current_view

    with data_lock:
        current_view = view
        state = 1

    while True:
        with data_lock:
            if state == 0:
                return current_action

        sleep(0.5)


def wtl_thread(cli_args):
    workflow = wtl.Workflow(config=wtl.Config(cli_args.config), policy=policy, url=cli_args.url, output=cli_args.output)

    workflow.classifiers.add(wtl.ActiveElementFilter(action=wtl.actions.Click, highlight=True))

    workflow.run()
    workflow.quit()


# === GUI THREAD (MAIN) ===
#

show_actives = None
current_filename = ""


def gui_thread():
    """
    Sets up the window with design and all callbacks.
    """
    global show_actives

    window = tk.Tk()
    window.title("WTL browser")
    window.geometry("1920x1080")

    top_frame = tk.Frame()

    canvas = tk.Canvas(top_frame, width=1280, height=1080)
    canvas.pack(padx=10, pady=10, side=tk.LEFT)
    img = None

    show_actives = tk.IntVar()
    ch = tk.Checkbutton(top_frame, text="Show active elements", variable=show_actives)
    ch.pack(side=tk.LEFT)

    small_font = font.Font(size=16)
    listbox = tk.Listbox(top_frame, width=375, height=200, font=small_font)
    listbox.pack(padx=5, pady=5, side=tk.LEFT)

    label_frame = tk.Frame(window, width=1400, height=100, bg="white")
    label_frame.pack_propagate(0)

    desc_label = tk.Label(label_frame, text="Hello", justify=tk.LEFT, wraplength=1300, bg="white")
    desc_label.pack()
    label_frame.pack()
    top_frame.pack()

    def get_element(mouse):  # pylint: disable=inconsistent-return-statements
        """
        Look for the element at current coords with smallest bounds
        """
        point = wtl.Point(mouse.x - 5, mouse.y - 5)

        with data_lock:
            if not current_view:
                return

            smallest_element, smallest_area = None, 999999
            for e in current_view.snapshot.elements:
                if point in e.bounds and e.bounds.area < smallest_area:
                    smallest_area, smallest_element = e.bounds.area, e

        return smallest_element

    def hover(mouse):
        """
        Update the top label when hovering over an element.
        """
        nonlocal desc_label

        smallest_element = get_element(mouse)

        with data_lock:
            if smallest_element:
                output = [f"{k}={str(v)}" for k, v in smallest_element.metadata.items() if k != "text"]
                desc_label.config(text=", ".join(output))
            else:
                desc_label.config(text=str("{}"))

    def double_clicked(mouse):
        """
        Set action of the clicked element.
        Does not check if it's active or not.
        """
        global state, current_action

        smallest_element = get_element(mouse)

        with data_lock:
            if smallest_element:
                state = 0
                current_action = wtl.actions.Click(wtl.Selector(f'[wtl-uid="{smallest_element.wtl_uid}"]'))

    def selected(_):
        """
        Sets action by clicking an element in the listbox.
        """
        global state, current_action
        nonlocal listbox

        with data_lock:
            data = str(listbox.get(listbox.curselection())).split(" (", maxsplit=1)[0]
            state = 0
            current_action = wtl.actions.Click(wtl.Selector(f'[wtl-uid="{data}"]'))

    # Bind functions to the GUI objects
    canvas.bind("<Motion>", hover)
    canvas.bind("<Double-Button-1>", double_clicked)
    listbox.bind("<<ListboxSelect>>", selected)

    def upd_view():
        """
        Checks state and updates the GUI with screenshot and list of actions.
        """
        global state, current_filename
        nonlocal img, listbox

        with data_lock:
            if state == 1:
                current_filename = None
                state = 2
                listbox.delete(0, tk.END)
                for item in current_view.actions.by_type(wtl.actions.Click):
                    wtl_uid = str(item.target.wtl_uid)
                    text = item.target.metadata["text"]
                    listbox.insert(tk.END, wtl_uid + f" ({text})")

            if state == 2:
                filename = "first" if show_actives.get() == 0 else "is_active"
                if filename != current_filename:
                    current_filename = filename
                    current_view.snapshot.screenshots[filename].save(Path("."))
                    img = tk.PhotoImage(file=f"{filename}.png")
                    canvas.create_image(5, 5, anchor=tk.NW, image=img)

        window.after(250, upd_view)

    window.after(1000, upd_view)
    window.mainloop()


# === === === === ===
# Entry point: Setup WTL thread and run GUI on this (main) thread.

if __name__ == "__main__":
    _cli_args = parse_cli_args()
    _wtl_thread = Thread(target=wtl_thread, args=(_cli_args,))
    _wtl_thread.start()
    gui_thread()
    _wtl_thread.join()
