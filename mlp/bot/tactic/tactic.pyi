from typing import (
    List,
    Dict,
    Any,
)

from ...protocol import Message
from ...unit import Unit
from ...actions.action import Action

class Tactic:

    def realize(self, unit: Unit) -> List[Message]: ...
    @staticmethod
    def random_aggression(unit: Unit) -> List[Action]: ...
    @staticmethod
    def search_in_aoe(action: Action, unit: Unit) -> Dict[str, Any]: ...
    @staticmethod
    def random_movement(unit: Unit) -> List[Action]: ...