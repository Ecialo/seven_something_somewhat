from .tactic import Tactic


class RandomWalkTactic(Tactic):

    def realize(self, unit):
        req_action = None
        for action in unit.action_bar:
            if action.name == "Move":
                req_action = action
                break

