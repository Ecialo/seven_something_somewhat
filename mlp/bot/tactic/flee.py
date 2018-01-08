from .tactic import Tactic
from ...grid import HexGrid


class Flee(Tactic):

    def realize(self, unit, influence_map=None):
        grid = HexGrid.locate()
        threat_map = influence_map
        pos = unit.pos
        min_ = 666.0
        arg_min = None
        for cell in grid.get_ring(pos, 2, 1):
            pass
