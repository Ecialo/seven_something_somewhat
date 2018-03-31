from .tactic import Tactic
from ...grid import HexGrid


class Flee(Tactic):

    def realize(self, unit, influence_map=None):
        grid = HexGrid.locate()
        threat_map = influence_map
        pos = unit.pos
        min_threat = 666.0
        arg_min = None
        for cell in grid.get_ring(pos, 2, 0):
            threat = threat_map[cell.pos]
            if threat <= min_threat:
                min_threat = threat
                arg_min = cell
        req_action = None
        for action in unit.action_bar:
            if action.name == "Move":
                req_action = action
                break
        actions = []
        if req_action.check():
            actions.append(req_action.copy().instant_setup(path=arg_min))
            actions.append(req_action.copy().instant_setup(path=arg_min))
        return actions
