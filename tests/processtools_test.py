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

from time import sleep

import pytest

from webtraversallibrary.driver_check import OS, get_current_os
from webtraversallibrary.processtools import TimeoutContext


def test_timeout_context_within_limits():
    with TimeoutContext(n_seconds=3):
        sleep(0.1)

    with TimeoutContext(n_seconds=0):
        sleep(0.1)


@pytest.mark.skipif(get_current_os() == OS.WINDOWS, reason="Windows don't have proper SIGALRM handling.")
def test_timeout_context_exceeds():
    with pytest.raises(TimeoutError):
        with TimeoutContext(n_seconds=1):
            sleep(2)
