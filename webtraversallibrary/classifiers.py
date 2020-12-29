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

"""Base classes for prior classifiers."""

import math
from abc import ABC
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Iterable, List, Sequence, Union

from .actions import Action
from .color import Color


class ScalingMode(Enum):
    """No scaling at all, preserve the raw score"""

    IDENTITY = auto()

    """Any values less than 0 are set to 0, any values larger than 1 are set to 1"""
    CLAMP = auto()

    """Map values to the [0,1] range"""
    LINEAR = auto()

    """Map the logarithm of the values to the [0,1] range"""
    LOG = auto()

    def scale(self, values: Sequence[float]) -> List[float]:
        """Scales a list of scores according to a given mode"""
        if self == ScalingMode.IDENTITY:
            return list(values)

        if self == ScalingMode.CLAMP:
            return [min(1, max(0, score)) for score in values]

        minimum, maximum = min(values), max(values)

        if minimum == maximum or len(values) <= 1:
            return [1.0] * len(values)

        if self == ScalingMode.LINEAR:
            return [(score - minimum) / (maximum - minimum) for score in values]

        return [(math.log(score) - math.log(minimum)) / (math.log(maximum) - math.log(minimum)) for score in values]


@dataclass
class Classifier(ABC):
    """
    Base class for all prior classifiers. Do not use,
    refer instead to :class:`ElementClassifier` or :class:`ViewClassifier`.
    """

    name: str
    enabled: bool = True
    callback: Any = None


@dataclass
class ElementClassifier(Classifier):
    """
    Classifies a set of elements. The callback will receive a list of
    elements that have have tags for all tags given in subset.

    The callback either returns a sublist of elements, or a list of tuples
    mapping element to a numeric score.

    If the callback is doing multi-class prediction, then the output should be
    a dictionary mapping class name to a sublist or list of tuples described above.
    The prediction results would be stored as <classifier_name>__<class name>.

    If highlight is True, highlight every element returned by this classifier.
    If highlight is a float x, highlight every element with a score larger than x.
    If highlight is an int N, highlight the top N scoring elemnets.
    """

    action: Action = None
    highlight: Union[float, bool] = False
    mode: ScalingMode = ScalingMode.CLAMP
    highlight_color: Color = Color.from_str("#5A1911")
    subset: Union[str, Iterable[str]] = "all"
    result_type: type = float


@dataclass
class ViewClassifier(Classifier):
    """
    Classifies a given view. The callback will receive a view
    and return an iterable of string tags.
    """


def _active_element_filter_func(elements, workflow):
    actives = set(workflow.js.execute_file(Path("find_active_elements.js")))
    return [elem for elem in elements if elem.wtl_uid in actives]


@dataclass
class ActiveElementFilter(ElementClassifier):
    """
    Returns all elements that are considered active, i.e. interactable in some way.
    Will also add a boolean `is_active` field to every element's metadata.
    """

    name: str = "is_active"
    callback: Callable = _active_element_filter_func
    result_type: type = bool
