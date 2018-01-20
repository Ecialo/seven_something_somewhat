import blinker

from .tactic import Tactic
from ...grid import HexGrid

MAX_ACTIONS_IN_PHASE = 2


def unit_in_area(unit):

    def extractor(cells):
        return unit in (cell.object for cell in cells)

    return extractor


def find_success(params_space):

    for param, result in params_space.items():
        if result:
            return param
    else:
        return None


def distance_to_cell(cell):

    def extractor(cells):
        return HexGrid.distance(cell, cells[-1])

    return extractor


def find_min(params_space):
    return min(params_space.items(), key=lambda x: x[1])[0]


class WalkTo(Tactic):

    def __init__(self, target):
        self.target = target
        self.extractor = distance_to_cell(target)

    def realize(self, unit):
        actions = []
        for action in self.random_actions_by_tag(unit, 'movement'):
            params = action.search_in_aoe(find_min, self.extractor)
            actions.append(action.instant_setup(**params))
            break
        return actions


class Attack(Tactic):

    def __init__(self, target):
        self.target = target
        self.extractor = unit_in_area(target)

    def realize(self, unit):
        actions = []
        for action in self.random_actions_by_tag(unit, 'aggression'):
            params = action.search_in_aoe(find_success, self.extractor)
            if all(params.values()):
                actions.append(action.instant_setup(**params))
        return actions


class ApproachAndAttack(Tactic):

    def __init__(self, target):
        self.target = target

    def realize(self, unit):
        actions = []
        for i in range(MAX_ACTIONS_IN_PHASE):
            attack = Attack(self.target).realize(unit)
            if not attack:
                move = WalkTo(self.target.cell).realize(unit)
                actions += move
                self.presume(move)
            else:
                actions += attack
                break
        return actions


class AttackNearest(Tactic):

    def realize(self, unit, _):
        min_distance = 999
        target = None
        for other_unit in self.units:
            if other_unit.stats.owner != unit.stats.owner:
                d = HexGrid.distance(unit.cell, other_unit.cell)
                if d < min_distance:
                    min_distance = d
                    target = other_unit
        return ApproachAndAttack(target).realize(unit)
