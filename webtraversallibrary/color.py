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

"""Representation of an RGB(A) color."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(order=True)
class Color:
    """Representation of an 8-bit RGBA color."""

    r: int
    g: int
    b: int
    a: int = 255

    def __post_init__(self):
        assert all(0 <= channel <= 255 for channel in (self.r, self.g, self.b, self.a))

    @staticmethod
    def from_str(color: str) -> Color:
        """Creates a color from a "#RRGGBBAA" representation. Alpha is optional."""
        if color.startswith("#"):
            color = color[1:]
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        a = int(color[6:], 16) if len(color) == 8 else 255
        return Color(r, g, b, a)

    def to_str(self, with_alpha: bool = False) -> str:
        """Creates an "#RRGGBBAA" string from this color. Alpha is optional."""

        def _hex(n):
            return hex(n)[2:].zfill(2)

        color = f"#{_hex(self.r)}{_hex(self.g)}{_hex(self.b)}"
        if with_alpha:
            color += f"{hex(self.a)[2:]}"
        return color.upper()

    def to_tuple(self, with_alpha: bool = False) -> Tuple:
        """
        Returns either a 3- or a 4-tuple with the values,
        depending on the value of `with_alpha`.
        """
        if with_alpha:
            return (self.r, self.g, self.b, self.a)
        return (self.r, self.g, self.b)
