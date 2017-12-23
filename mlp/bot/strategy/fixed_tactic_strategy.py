from .strategy import Strategy
from ...protocol import (
    message_type as mt,
    game_message as gm
)
from ...serialization import remote_action_append


class FixedTacticStrategy(Strategy):

    def __init__(self, tactic):
        self.tactic = tactic

    def make_decisions(self, player):
        actions = []
        print("\n\n\nSTART THINKING")
        for unit in player.units:
            print("TRY UNIT")
            actions += self.tactic.realize(unit)
        actions = [remote_action_append(action) for action in actions]
        actions.append(((mt.GAME, gm.READY), {}))
        return actions
