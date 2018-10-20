from .freezable import Freezable


class World(Freezable):
    """
    All data required for game:
    * Grid
    * Units
    * Players
    """

    def __init__(self, grid, units, players):
        self._grid = grid
        self._units = units
        self._players = players

    def freeze(self):
        pass

    def unfreeze(self):
        pass

    def rollback(self):
        pass
