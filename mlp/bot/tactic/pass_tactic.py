from .tactic import Tactic


class PassTactic(Tactic):

    def realize(self, unit):
        return []
