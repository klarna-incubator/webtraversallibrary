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

from webtraversallibrary import ScalingMode


def test_identity():
    data = [-1.0, -0.5, 0.5, 1.0, 1.5]
    data_i = ScalingMode.IDENTITY.scale(data)
    assert data == data_i


def test_clamp():
    data = [-1.0, -0.5, 0.5, 1.0, 1.5]
    data_c = ScalingMode.CLAMP.scale(data)
    assert data_c == [0, 0, 0.5, 1, 1]


def test_linear():
    data = [25]
    data_lin = ScalingMode.LINEAR.scale(data)
    assert data_lin == [1]

    data = [-1.0, -0.5, 0.5, 1.0, 1.5]
    data_lin = ScalingMode.LINEAR.scale(data)
    assert data_lin == [0, 0.2, 0.6, 0.8, 1.0]

    data = list(reversed([-1.0, -0.5, 0.5, 1.0, 1.5]))
    data_lin = ScalingMode.LINEAR.scale(data)
    assert data_lin == list(reversed([0, 0.2, 0.6, 0.8, 1.0]))


def test_log():
    data = [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
    data_log = ScalingMode.LOG.scale(data)
    assert data_log == [
        0.0,
        0.26957728969081496,
        0.46084542061837014,
        0.6092045089156072,
        0.7304227103091849,
        0.8329112392623182,
        0.9216908412367402,
        1.0,
    ]
