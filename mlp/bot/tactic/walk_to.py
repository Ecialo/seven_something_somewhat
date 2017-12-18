from ...grid import HexGrid
from .tactic import Tactic


class WalkTo(Tactic):

    grid = HexGrid.locate()

    def __init__(self, target):
        self.target = target

    def compute_distance(self, path):
        d = self.grid.distance(self.target.cell, path[-1])
        return d

    def realize(self, unit):
        for action in self.random_movement(unit):
            self.search_in_aoe(action, )