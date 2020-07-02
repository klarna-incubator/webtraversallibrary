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
Plays TicTacToe online by using a simple AI implementation.
"""
from typing import List

import webtraversallibrary as wtl
from webtraversallibrary.actions import Click

from .util import parse_cli_args


def checkWin(board, player) -> bool:
    for i in range(0, 3):
        if board[i * 3] == player and board[i * 3 + 1] == player and board[i * 3 + 2] == player:
            return True
        if board[i] == player and board[i + 3] == player and board[i + 6] == player:
            return True
    if board[0] == player and board[4] == player and board[8] == player:
        return True
    if board[2] == player and board[4] == player and board[6] == player:
        return True
    return False


def getAIMove(board, nextMove, aiPlayer):
    if checkWin(board, aiPlayer):
        return (-1, 10)
    if checkWin(board, "O" if aiPlayer == "X" else "X"):
        return (-1, -10)

    free = [i for i, b in enumerate(board) if b == " "]
    if not free:
        return (-1, 0)
    if len(free) == len(board):
        return (4, 0)

    moves = []
    for i in free:
        nextBoard = board[:]
        nextBoard[i] = nextMove
        score = getAIMove(nextBoard, ("X" if nextMove == "O" else "O"), aiPlayer)[1]
        moves.append((i, score))

    moves.sort(key=lambda m: m[1], reverse=nextMove == aiPlayer)
    return moves[0]


def printBoard(board):
    print("\n")
    for i in range(9):
        if not board[i] == " ":
            print(board[i], end="   ")
        else:
            print("_", end="   ")
        if i in (2, 5):
            print("")
    print("\n")


@wtl.single_tab
def policy(_, view: wtl.View) -> List[wtl.Action]:
    start = view.actions.by_score("start")
    if start:
        return [start[0]]

    tiles = [t.target for t in view.actions.by_score("tile")]
    board = [t.metadata["class"][5].upper() if t.metadata["class"] else " " for t in tiles]
    move = getAIMove(board, "X", "X")

    printBoard(board)

    return [wtl.actions.Clear(viewport=False), wtl.actions.Click(tiles[move[0]])]


def _start_btn(elements, _):
    return [e for e in elements if e.metadata["id"] == "sync-task-cover" and "block" in e.metadata["display"]]


def _tile_div(elements, _):
    return [
        e
        for e in elements
        if e.metadata["tag"] == "span" and e.metadata["id"].startswith("ttt") and e.tag.parent.name == "div"
    ]


if __name__ == "__main__":
    cli_args = parse_cli_args()

    workflow = wtl.Workflow(
        config=wtl.Config(cli_args.config),
        policy=policy,
        url="https://stanfordnlp.github.io/miniwob-plusplus/html/miniwob/tic-tac-toe.html",
        output=cli_args.output,
    )

    workflow.classifiers.add(wtl.ActiveElementFilter())
    workflow.classifiers.add(wtl.ActiveElementFilter(name="start", callback=_start_btn, action=Click))
    workflow.classifiers.add(wtl.ActiveElementFilter(name="tile", callback=_tile_div, action=Click))

    workflow.run()
    workflow.quit()
