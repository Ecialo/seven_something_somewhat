from ...grid import HexGrid
from ..influence_map import *


class Strategy:

    def make_decisions(self, player):
        pass


class InfluenceMapStrategy(Strategy):

    def make_decisions(self, player):
        grid = HexGrid.locate()