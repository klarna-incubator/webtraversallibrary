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

from webtraversallibrary.config import Config


def test_default():
    config = Config.default()
    assert "browser" in config


def test_update():
    config = Config.default()
    assert "browser" in config
    config.update({"x": "y"})
    assert config.x == "y"

    config.update("x=z")
    assert config.x == "z"

    config.update("a.b.c=True")
    assert config.a.b.c
    config.update("a.b.d=False")
    assert not config.a.b.d
    config.update("a.b.e=123")
    assert config.a.b.e == 123
    config.update("a.b.e=123.4")
    assert config.a.b.e == 123.4


def test_json():
    config = Config.default()
    json = config.to_json()
    assert len(json) == len(config)
