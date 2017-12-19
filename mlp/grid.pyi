from typing import (
    Sequence
)

from .replication_manager import GameObject


class Cell:
    pass


class Grid(GameObject):

    def __getitem__(self, item: Sequence[int]) -> Cell: ...
    def distance(self, cell_a, cell_b) -> int: ...

class HexGrid(Grid):

    @classmethod
    def locate(cls) -> HexGrid: ...
