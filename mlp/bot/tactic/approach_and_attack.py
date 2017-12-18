from .tactic import Tactic
from .attack_nearest import AttackNearest


class ApproachAndAttack(Tactic):

    def __init__(self, target):
        self.unit = target

    def realize(self, unit):
        pass