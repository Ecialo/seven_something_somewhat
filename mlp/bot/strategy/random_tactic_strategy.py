import random as rnd
import operator as op

from ..tactic import ALL_MAJOR_TACTIC
from .strategy import Strategy
from ...protocol import (
    message_type as mt,
    game_message as gm
)
from ...serialization import remote_action_append
from ..influence_map.threat_map import compute_threat_map
from ...grid import HexGrid


class RandomTacticStrategy(Strategy):

    def make_decisions(self, player):
        grid = HexGrid.locate()
        threat_map = compute_threat_map(grid, player.name, op.ne)

        actions = []
        tactic_name = rnd.choice(list(ALL_MAJOR_TACTIC.keys()))
        tactic = ALL_MAJOR_TACTIC[tactic_name]()
        for unit in player.units:
            if unit.is_alive:
                actions += tactic.realize(unit, threat_map)
        actions = [remote_action_append(action) for action in actions]
        actions.append(((mt.GAME, gm.READY), {}))
        return tactic_name, actions
