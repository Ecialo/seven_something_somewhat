from typing import (
    List,
    Dict,
    Any,
    ClassVar,
    Optional,
)

import numpy as np

from ...unit import Unit
from ...actions.action import Action
from ...replication_manager import GameObjectRegistry

class Tactic:

    registry = ClassVar[GameObjectRegistry]

    def realize(self, unit: Unit, influence_map: Optional[np.ndarray]=None) -> List[Action]: ...
    @staticmethod
    def search_in_aoe(action: Action, unit: Unit) -> Dict[str, Any]: ...
    @staticmethod
    def random_actions_by_tag(unit: Unit, tag: str) -> List[Action]: ...
    @staticmethod
    def presume(actions: List[Action]) -> None: ...
    @staticmethod
    def forget(unit: Unit) -> None: ...
    @property
    def units(self) -> List[Unit]: ...