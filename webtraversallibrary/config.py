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

"""Configuration object for discovery workflow"""
from __future__ import annotations

import functools
import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Union

from prodict import Prodict  # pylint: disable=syntax-error

from .driver_check import Drivers, is_driver_installed

logger = logging.getLogger("wtl")


class Config:
    """Represents a config object."""

    CONFIG_DIR = Path(os.path.abspath(os.path.dirname(__file__))) / "configs"

    REQUIRED_PARAMS = dict(
        [
            ("bs_html_parser", str),
            ("timeout", int),
            ("actions.abort.close", bool),
            ("scraping.disable_animations", bool),
            ("scraping.attempts", int),
            ("scraping.prescroll", bool),
            ("scraping.page_load_timeout", int),
            ("scraping.wait_loading", float),
            ("scraping.wait_scroll", float),
            ("scraping.wait_action", float),
            ("scraping.save_mhtml", bool),
            ("scraping.temp_path", str),
            ("scraping.mhtml_timeout", int),
            ("scraping.history", bool),
            ("scraping.full_history", bool),
            ("scrolling.max_page_height", int),
            ("browser.browser", str),
            ("browser.useragent", str),
            ("browser.width", int),
            ("browser.height", int),
            ("browser.headless", bool),
            ("browser.enable_mhtml", bool),
            ("browser.proxy", str),
            ("javascript.info", str),
            ("javascript.warning", str),
            ("javascript.severe", str),
            ("debug.autoscroll", bool),
            ("debug.default_canvas_viewport", bool),
            ("debug.live", bool),
            ("debug.live_delay", float),
            ("debug.live_annotation", bool),
            ("debug.screenshots", bool),
            ("debug.save", bool),
            ("debug.preserve_window", bool),
            ("debug.action_highlight_color", str),
        ]
    )

    def __init__(self, cfg: Iterable[Union[str, Path, dict]] = None):
        cfg = cfg or []

        self._instance = Prodict()
        for item in cfg:
            if item:
                self.update(item)

        self._ensure_has_all_params(Config.REQUIRED_PARAMS)
        logger.debug(f"Configuration loaded from {cfg}")

    def update(self, cfg: Union[str, Path, dict]):
        ddict = Config._parse_input_config(cfg)
        Config._update(self._instance, ddict)

    @staticmethod
    def _update(fst_dd, snd_dd):
        for key, snd_value in snd_dd.items():
            fst_value = fst_dd.get(key, None)
            do_recurse = isinstance(fst_value, dict) and isinstance(snd_value, dict)
            if key not in fst_dd or not do_recurse:
                if key in fst_dd:
                    logger.debug(f"Overwriting {key} -> {fst_value} with {snd_value}")
                else:
                    logger.debug(f"Adding {key} -> {snd_dd}")
                fst_dd[key] = snd_value
            elif do_recurse:
                Config._update(fst_value, snd_value)

    def to_json(self):
        return json.loads(json.dumps(self._instance))

    def __getattr__(self, item):
        return getattr(self._instance, item)

    def __getitem__(self, item):
        return functools.reduce(lambda obj, key: obj[key], item.split("."), self._instance)

    def __contains__(self, item):
        obj = self._instance
        for attr in item.split("."):
            if attr not in obj:
                return False
            obj = obj[attr]
        return True

    def _ensure_has_all_params(self, params):
        for param_name, param_type in params.items():
            if param_name not in self:
                raise ValueError(f"Missing required parameter '{param_name}'")
            if not isinstance(self[param_name], param_type):
                raise ValueError(
                    f"Expected parameter '{param_name}' to be of type '{param_type}',"
                    f"got '{type(self[param_name])}' instead"
                )

    def __repr__(self):
        return repr(self._instance)

    def __str__(self):
        return str(self._instance)

    def __len__(self):
        return len(self._instance)

    def validate(self):
        """
        Performs basic sanity checks on the configuration values.
        Throws AssertionError if something is incorrect.
        """
        LOG_LEVELS = ["", "debug", "info", "warning", "error", "critical"]
        BROWSERS = ["chrome", "firefox"]
        cfg = self._instance

        assert cfg.javascript.info in LOG_LEVELS
        assert cfg.javascript.warning in LOG_LEVELS
        assert cfg.javascript.severe in LOG_LEVELS
        assert cfg.timeout >= 0
        assert cfg.scraping.attempts >= 1
        assert cfg.scraping.page_load_timeout >= 0
        assert cfg.scrolling.max_page_height >= 0
        assert cfg.browser.width >= 1
        assert cfg.browser.height >= 1
        assert cfg.debug.live_delay >= 0
        assert cfg.browser.browser in BROWSERS

        if cfg.browser.browser == "chrome":
            assert is_driver_installed(Drivers.GOOGLE_CHROME) or is_driver_installed(Drivers.CHROMIUM)
            assert is_driver_installed(Drivers.CHROMEDRIVER)
        elif cfg.browser.browser == "firefox":
            assert is_driver_installed(Drivers.FIREFOX)
            assert is_driver_installed(Drivers.GECKODRIVER)

    @staticmethod
    def default(cfg: List[Union[str, Path, dict]] = None) -> Config:
        """Creates a Config object based on all default values"""
        cfg = cfg or []
        return Config([Path("default.json")] + cfg)  # type: ignore

    @staticmethod
    def _parse_input_config(cfg: Union[str, Path, dict]):
        if isinstance(cfg, dict):
            return Prodict.from_dict(cfg)

        if isinstance(cfg, str) and "=" in cfg:
            key, value = cfg.split("=")
            parsed_value: Any

            if value == "True":
                parsed_value = True
            elif value == "False":
                parsed_value = False
            elif re.match(r"^[-+]?[0-9]+$", value):
                parsed_value = int(value)
            elif re.match(r"^[-+]?[0-9]*\.?[0-9]+$", value):
                parsed_value = float(value)
            else:
                parsed_value = value

            key_chain = key.split(".")
            result: Dict[str, Any] = {}
            ref = result
            while len(key_chain) > 1:
                next_key = key_chain.pop(0)
                ref[next_key] = {}
                ref = ref[next_key]
            ref[key_chain.pop(0)] = parsed_value
            return Prodict.from_dict(result)

        if isinstance(cfg, str):
            cfg = Path(cfg)

        if isinstance(cfg, Path):
            if not cfg.suffix:
                cfg = cfg.with_suffix(".json")
            if not cfg.exists():
                cfg = Config.CONFIG_DIR / cfg
            if not cfg.exists():
                raise FileNotFoundError(f"Given config {str(cfg)} does not exist locally or as part of wtl.")

            json_data = json.load(Path(cfg).open(encoding="utf8"))
            return Prodict.from_dict(json_data)

        raise ValueError(f"Unexpected config input: {cfg}")
