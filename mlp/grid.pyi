from typing import (
    Sequence,
    Union,
    Tuple,
    Set,
    Optional,
    List,
    Deque,
)

import yaml

from .replication_manager import GameObject
from .freezable import Freezable
from pyrsistent import PMap

Pos = Tuple[int, int]

class FixedArea:

    def __init__(self, cells, color): ...

class Cell(Freezable):

    pos: Pos
    data: PMap
    _checkpoints: Deque[PMap]

    def __init__(self, pos: Pos, grid: Optional[Grid] = None, terrain=None) -> None: ...
    def freeze(self) -> None: ...
    def unfreeze(self) -> None: ...
    def rollback(self) -> None: ...


class HexCell(Cell):
    pass


class Grid(GameObject, Freezable):

    def __getitem__(self, item: Sequence[int]) -> Cell: ...
    def __iter__(self) -> Sequence[Cell]: ...
    @classmethod
    def distance(cls, cell_a: Cell, cell_b: Cell) -> int: ...
    def find_path(
            self,
            from_pos_or_cell: Union[Tuple[int, int], Cell],
            to_pos_or_cell: Union[Tuple[int, int], Cell]
    ) -> List[Cell]: ...
    def freeze(self) -> None: ...
    def unfreeze(self) -> None: ...
    def rollback(self) -> None: ...

class HexGrid(Grid):

    @classmethod
    def locate(cls) -> HexGrid: ...
    def get_area(self, pos_or_cell: Union[Tuple[int, int], Cell], r: int) -> Set[Cell]: ...
    def get_ring(
            self,
            pos_or_cell: Union[Tuple[int, int], Cell],
            r: int, inner_r: Optional[int] = None
    ) -> Set[Cell]: ...


CELL_TAG: str

def cell_constructor(loader: yaml.Loader, node: yaml.Node) -> Cell: ...