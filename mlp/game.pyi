from typing import (
    List,
    Dict,
    Iterator,
    Optional,
    Any,
    Tuple,
)

from .replication_manager import (
    GameObjectRegistry,
    GameObject,
)
from .unit import Unit
from .grid import (
    Grid,
    Cell,
)
from .player import Player
from .commands.command import Command

class TurnOrderManager(GameObject):

    _current_turn_order: List[Unit]

    def __iter__(self) -> Iterator[Unit]: ...
    @staticmethod
    def get_current_unit_initiative(unit: Unit) -> Tuple[int, int, Unit]: ...
    def rearrange(self) -> None: ...

class Game:

    registry: GameObjectRegistry
    players: Optional[List[Player]]
    state: int
    commands: List[Command]

    def __init__(
            self,
            players: Optional[List[Player]],
            grid: Optional[Grid],
            turn_order_manager: Optional[TurnOrderManager],
    ) -> None: ...
    @property
    def units(self) -> List[Unit]: ...
    @property
    def turn_order_manager(self) -> TurnOrderManager: ...
    def append_action(self, action_struct: Dict[str, Any]) -> None: ...
    def remove_action(self, action_struct: Dict[str, Any]) -> None: ...
    def envoke_commands(self, new_commands: List[Command]) -> None: ...
    def setup_and_run(self, payload: Dict[str, Any]) -> None: ...
    def run(self) -> bool: ...
    def apply_actions(self, log: bool) -> bool: ...
    def switch_state(self) -> None: ...
    def update_position(self) -> None: ...
    def clear_presumed(self) -> None: ...
    def add_to_commands(self, _: Any, command: Command) -> None: ...
    def on_summon(self,  _: Any, unit: Unit, cell: Cell) -> None: ...