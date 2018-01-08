from typing import (
    Sequence,
    Union,
    Tuple,
    Set,
    Optional,
    List,
)

from .replication_manager import GameObject


class Cell:
    pass


class HexCell(Cell):
    pass


class Grid(GameObject):

    def __getitem__(self, item: Sequence[int]) -> Cell: ...
    @classmethod
    def distance(cls, cell_a: Cell, cell_b: Cell) -> int: ...
    def find_path(
            self,
            from_pos_or_cell: Union[Tuple[int, int], Cell],
            to_pos_or_cell: Union[Tuple[int, int], Cell]
    ) -> List[Cell]: ...

class HexGrid(Grid):

    @classmethod
    def locate(cls) -> HexGrid: ...
    def get_area(self, pos_or_cell: Union[Tuple[int, int], Cell], r: int) -> Set[Cell]: ...
    def get_ring(self, pos_or_cell: Union[Tuple[int, int], Cell], r: int, inner_r: Optional[int] = None) -> Set[Cell]: ...
