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
Not an example, just helper functions for the other examples.
"""
import os
import subprocess
from argparse import ArgumentParser
from pathlib import Path

import webtraversallibrary as wtl


def start_server() -> str:
    my_env = os.environ.copy()
    my_env["FLASK_APP"] = "tests/site/flask_app.py"
    subprocess.Popen("python3 -m flask run".split(), env=my_env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return "http://localhost:5000"


def parse_cli_args() -> ArgumentParser:
    """
    Parses CLI flags relevant for examples.
    """
    parser = ArgumentParser()

    group = parser.add_argument_group("Run parameters")
    group.add_argument("--url", type=str, default="DEFAULT", help="URL to run the workflow on.")
    group.add_argument(
        "--output",
        type=Path,
        help="Where to save the result locally. If save, remember to also add save flag for config.",
        default=None,
    )
    group.add_argument(
        "--windows",
        type=str,
        nargs="*",
        default=[wtl.Workflow.SINGLE_TAB],
        help="Tab names (comma-separated). Use space separation for multiple windows.",
    )
    group.add_argument(
        "--config",
        type=str,
        nargs="*",
        default=[],
        required=False,
        help="Names of config files in config/, such as " '"iphone_x_mobile", or key=value pairs.',
    )

    cli_args = parser.parse_args()
    cli_args.config.insert(0, "default")

    if cli_args.url == "DEFAULT":
        cli_args.url = start_server()

    return cli_args
