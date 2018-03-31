from random import shuffle

import blinker

from ...replication_manager import GameObjectRegistry

presume = blinker.signal("presume")
forget = blinker.signal("forget")


class Tactic:

    registry = GameObjectRegistry()

    def realize(self, unit, influence_map=None):
        pass

    @property
    def units(self):
        return self.registry.categories["Unit"]#.__name__]

    @staticmethod
    def random_actions_by_tag(unit, tag):
        a = []
        for action in unit.stats.action_bar:
            if tag in action.tags and action.check():
                a.append(action)
        shuffle(a)
        return a

    @staticmethod
    def search_in_aoe(action, unit):
        result_params = {}
        for cursor_name, cursor in action.cursors():
            params = cursor.search_in_aoe(unit)
            if params:
                result_params[cursor_name] = params
        return result_params

    @staticmethod
    def presume(actions):
        presume.send(None, actions=actions)

    @staticmethod
    def forget(unit):
        forget.send(None, unit=unit)
