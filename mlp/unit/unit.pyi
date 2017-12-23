from typing import (
    ClassVar,
    List,
    Optional,
    Dict,
    Any,
    Callable,
    Tuple,
    Sequence,
    Union,
)

from yaml import (
    Loader,
    MappingNode
)

from ..replication_manager import (
    GameObject,
    Registry
)
from ..actions.action import (
    ActionBar,
    CurrentActionBar,
)
from ..actions.property.reference import Reference
from ..actions.base.status import Status
from ..actions.base.effect import AbstractEffect
from ..stats.new_stats import (
    MajorStats,
    Stats,
)
from ..grid import Cell

PLANNING: int
ACTION: int
UNITS: Registry

class Unit(GameObject):
    hooks = ClassVar[List[str]]
    actions = ClassVar[List[str]]
    resources = ClassVar[Dict[str, Any]]

    _stats: MajorStats
    state: int
    current_action_bar: CurrentActionBar
    context: Dict[str, Any]

    def __init__(self, master_name: str, id_=Optional[int]) -> None: ...
    @property
    def action_bar(self) -> ActionBar: ...
    @property
    def _presumed_stats(self) -> Stats: ...
    @property
    def presumed_cell(self) -> Cell: ...
    @property
    def real_cell(self) -> Cell: ...
    @property
    def stats(self) -> Stats: ...
    cell: property(Callable[[Any], Cell], Callable[[Any, Cell], None])
    def place_in(self, cell: Cell) -> None: ...
    def update_position(self) -> None: ...
    def move(self, cell: Cell) -> None: ...
    pos: property(Callable[[Any], Tuple[int, int]], Callable[[Any, Tuple[int, int]], None])
    def append_action(self, action: type) -> None: ...
    def remove_action(self, action_index: int) -> None: ...
    def apply_actions(self, speed: int) -> bool: ...
    def refill_action_points(self) -> None: ...
    def clear_presumed(self) -> None: ...
    def switch_state(self) -> None: ...
    def add_status(self, status: Status) -> None: ...
    def remove_status(self, status: Status) -> None: ...
    def remove_status_by_tag(self, tag: str) -> None: ...
    def launch_triggers(self, tags: Sequence, target: Union[AbstractEffect, Unit], target_context: Dict[str, Any]) -> None: ...
    def change_owner(self, new_owner: str) -> None: ...
    def kill(self) -> None: ...
    def __contains__(self, item: Union[Status, str]) -> bool: ...
    @classmethod
    def locate(cls) -> List[Unit]: ...

def new_unit_constructor(loader: Loader, node: MappingNode) -> type: ...
def unit_constructor(loader: Loader, node: MappingNode) -> Reference: ...
UNIT_TAG: str
NEW_UNIT_TAG: str