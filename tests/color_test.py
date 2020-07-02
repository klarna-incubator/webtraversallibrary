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

from webtraversallibrary.color import Color


def test_basic_use():
    c = Color(255, 255, 255)
    assert c.to_str() == "#FFFFFF"
    assert c.to_str(with_alpha=True) == "#FFFFFFFF"
    assert c.to_tuple() == (255, 255, 255)
    assert c.to_tuple(with_alpha=True) == (255, 255, 255, 255)

    c = Color(75, 200, 1, 64)
    assert c.to_str() == "#4BC801"
    assert c.to_str(with_alpha=True) == "#4BC80140"
    assert c.to_tuple() == (75, 200, 1)
    assert c.to_tuple(with_alpha=True) == (75, 200, 1, 64)


def test_from_str():
    c = Color.from_str("AABBCC")
    assert c.r == 170
    assert c.g == 187
    assert c.b == 204
    assert c.a == 255

    c = Color.from_str("AABBCCDD")
    assert c.r == 170
    assert c.g == 187
    assert c.b == 204
    assert c.a == 221

    assert c.to_str(with_alpha=True) == "#AABBCCDD"
