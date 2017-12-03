from .replication_manager import GameObject


class Cell:
    pass


class Grid(GameObject):

    def distance(self, cell_a, cell_b) -> int: ...


class HexGrid(Grid):

    @classmethod
    def locate(cls) -> HexGrid: ...
