from typing import (
    List,
    Dict,
    Any,
)

from ...unit import Unit
from ...actions.action import Action

class Tactic:

    def realize(self, unit: Unit) -> List[Action]: ...
    @staticmethod
    def search_in_aoe(action: Action, unit: Unit) -> Dict[str, Any]: ...
    @staticmethod
    def random_actions_by_tag(unit: Unit, tag: str) -> List[Action]: ...
    @staticmethod
    def presume(actions: List[Action]) -> None: ...
    @staticmethod
    def forget(unit: Unit) -> None: ...