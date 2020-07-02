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
Extract version information from several possible sources in a pre-assigned priority:
 * environment
 * git context
 * .gitinfo file
 * default value
"""

import os
import subprocess


def get_commit_hash(short: bool = False) -> str:
    """
    Extract commit hash from either the environment, or the ``.gitinfo`` file.
    If nothing works, returns "unknown".
    """
    git_command = ["git", "rev-parse", "HEAD"]

    if short:
        git_command.insert(2, "--short")

    try:
        return subprocess.check_output(git_command, universal_newlines=True, stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:
        pass

    # This may be a source copy without .git information. Look for .gitinfo file
    try:
        with open(".gitinfo") as f:
            return f.readline().strip()
    except OSError:
        pass

    # As a last resort, return a special value
    return "unknown"


def get_branch_name() -> str:
    """
    Extract branch name from either the environment, or the ``.gitinfo`` file.
    Returns "unknown" if it couldn't be found.
    """

    # If explicitly set, take the environment variable
    if "BRANCH_NAME" in os.environ:
        return os.environ["BRANCH_NAME"]

    # Otherwise, try to get the context from current directory git metadata
    try:
        branch_name = subprocess.check_output(
            ["bash", "-c", 'git branch --list | grep -e "*" | cut -c 3-'],
            universal_newlines=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if branch_name:
            # The piped command chain will "succeed" even if "git branch --list" returns nothing
            # In that case, branch_name will be empty and should not be returned
            return branch_name
    except subprocess.CalledProcessError:
        pass

    # If that's not available either, look for the .gitinfo file that gets added to Docker containers
    try:
        with open(".gitinfo") as f:
            return f.readlines()[-1].strip()
    except OSError:
        pass

    # As a last resort, return a special value
    return "unknown"
