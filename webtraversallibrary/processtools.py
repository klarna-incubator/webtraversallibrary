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
Module collecting helper functions for common processing tasks, such as muting stdout within a context.
"""

import logging
import os
import signal
from threading import Thread
from time import sleep

from webtraversallibrary.driver_check import OS, get_current_os

logger = logging.getLogger("wtl")


_ON_WINDOWS = get_current_os() == OS.WINDOWS


class cached_property:
    """
    Decorator that caches a property return value and will return it on later calls.
    Adapted from The Python Cookbok, 2nd edition.

    .. note::
        If you want to map different arguments to values, use `functools.lru_cache`!
    """

    def __init__(self, method):
        self.method = method
        self.name = method.__name__
        self.__doc__ = method.__doc__

    def __get__(self, inst, cls):
        if inst is None:
            return self
        result = self.method(inst)
        object.__setattr__(inst, self.name, result)
        return result


class Alarm(Thread):
    """Helper class to run a timeout thread on Windows"""

    def __init__(self, timeout):
        Thread.__init__(self)
        self.timeout = timeout
        self._stop_gracefully = False
        self.setDaemon(True)

    def stop(self):
        self._stop_gracefully = True

    def run(self):
        sleep(self.timeout)
        if not self._stop_gracefully:
            os._exit(1)  # pylint: disable=protected-access


class TimeoutContext:
    """
    Uses :mod:`signal` to raise TimeoutError within the block, if execution went over a specified timeout.
    """

    def __init__(self, n_seconds, error_class=TimeoutError):
        self.n_seconds = n_seconds
        self.error_cls = error_class
        self.alarm = None

    def __enter__(self):
        # pylint: disable=no-member
        if self.n_seconds > 0:
            if _ON_WINDOWS:
                self.alarm = Alarm(self.n_seconds)
                self.alarm.start()
            else:
                signal.signal(signal.SIGALRM, self.raise_error)
                signal.alarm(self.n_seconds)
            logger.debug(f"TimeoutContext: Operation timeout is set to {self.n_seconds} sec.")

    def __exit__(self, *args, **kwargs):
        # pylint: disable=no-member
        # Cancel the alarm
        if self.n_seconds > 0:
            if _ON_WINDOWS:
                self.alarm.stop()
            else:
                signal.signal(signal.SIGALRM, signal.SIG_DFL)
                time_left = signal.alarm(0)
                if time_left <= 0:
                    logger.debug("TimeoutContext: Operation was interrupted by the timeout")

    def raise_error(self, signal_num, _):
        """
        Raises error on timeout.
        """
        # pylint: disable=no-member
        assert signal_num == signal.SIGALRM
        raise self.error_cls(f"Operation timed out after {self.n_seconds} sec.")
