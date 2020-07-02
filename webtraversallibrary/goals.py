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

"""Contains built-in simple, common goals."""


class N_STEPS:
    """Will return False (continue) exactly n times, and then return True."""

    def __init__(self, n: int):
        assert n >= 0
        self.n = n + 1

    def __call__(self, *_, **__):
        self.n -= 1
        return self.n <= 0


class ONCE(N_STEPS):
    """Will return False (continue) exactly once."""

    def __init__(self):
        super().__init__(n=1)


def FOREVER(*_, **__):
    """Will always return False (continue)."""
    return False
