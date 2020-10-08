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

"""Base representation of the current state of a tab."""

from dataclasses import dataclass, field
from typing import Any, Dict, Set

from .actions import Actions
from .snapshot import PageSnapshot


@dataclass(frozen=True)
class View:
    """
    Base representation of the current state of a tab. Holds a snapshot, a list of
    available actions, and output from the prior classifiers.
    Note: The `metadata` field can be added to arbitrarily, and contents will be deeply
    copied to the next view (do not store too large objects!)
    If you need large metadata storage, use the workflow.metadata instead.
    """

    name: str
    snapshot: PageSnapshot = field(hash=False)
    actions: Actions = field(hash=False, default_factory=Actions, repr=False)
    tags: Set[str] = field(hash=False, default_factory=set)
    metadata: Dict[Any, Any] = field(hash=False, default_factory=dict)

    def copy(self, no_snapshot: bool = False):
        """Creates a shallow copy"""
        return View(
            name=self.name,
            snapshot=None if no_snapshot else self.snapshot,
            actions=None if no_snapshot else self.actions,
            tags=self.tags,
            metadata=self.metadata,
        )
