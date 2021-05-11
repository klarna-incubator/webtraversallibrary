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
Helper function for logging.
"""

import logging
import pathlib
from typing import Optional


def setup_logging(log_dir: Optional[pathlib.Path] = None, logging_level: int = logging.INFO):
    """
    Sets up logging: create a directory to write log files to, configure handlers. Sets sane
    default values for in-house and third-party modules.

    Will remove any existing logging handlers with the name "webtraversallibrary" before proceeding.

    :param log_dir: directory to write log files to.
    :param logging_level: level of logging you wish to have, accepts number or logging.LEVEL
    """
    logging.getLogger("selenium").setLevel(logging.INFO)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    logger = logging.getLogger()

    for h in logger.handlers[:]:
        if h.name and "webtraversallibrary" in h.name:
            logger.removeHandler(h)

    formatter = logging.Formatter("{asctime} {levelname:8} {name:12} - {message}", "%H:%M:%S", style="{")
    to_console = logging.StreamHandler()
    to_console.setFormatter(formatter)
    to_console.set_name("webtraversallibrary-console")  # type: ignore
    logger.setLevel(logging_level)
    logger.addHandler(to_console)

    if log_dir:
        # If log directory is provided, write to there as well
        log_dir.mkdir(exist_ok=True, parents=True)
        to_file = logging.FileHandler(log_dir / "output.log", mode="w", encoding="utf-8")
        to_file.setFormatter(formatter)
        to_file.set_name("webtraversallibrary-file")  # type: ignore
        logger.addHandler(to_file)
