from typing import (
    List,
    Iterator,
)

from .replication_manager import (
    GameObjectRegistry,
    GameObject,
)
from .unit import Unit

class TurnOrderManager(GameObject):

    def __iter__(self) -> Iterator[Unit]: ...
    def rearrange(self) -> None: ...

class Game:

    registry: GameObjectRegistry

    @property
    def units(self) -> List[Unit]: ...
    @property
    def turn_order_manager(self) -> TurnOrderManager: ...