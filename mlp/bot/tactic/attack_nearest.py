from ...serialization import remote_action_append
from ...unit import Unit
from ...grid import HexGrid
from .tactic import Tactic

MAX_DIST = 999


class AttackNearest(Tactic):

    def realize(self, unit):
        result_actions = []

        grid = HexGrid.locate()
        closest_enemy_unit = min(
            filter(lambda un: un.stats.owner != unit.stats.owner, Unit.locate()),
            key=lambda un: grid.distance(un.cell, unit.cell)
        )

        for action in self.random_agression(unit):
            params = self.search_in_aoe(action, closest_enemy_unit)
            if params is not None:
                result_actions.append(remote_action_append(action.copy().instanst_setup(**params)))

        return result_actions
