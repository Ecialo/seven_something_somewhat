from random import choice

from yaml import SequenceNode

from ...replication_manager import MetaRegistry
from ...bot.tactic import ALL_MAJOR_TACTIC

BEHAVIORS = MetaRegistry()['Behavior']
BehaviorMeta = MetaRegistry().make_registered_metaclass("Behavior")


class Behavior(metaclass=BehaviorMeta):

    def apply_to(self, unit):
        pass


class ManualBehavior(Behavior):
    name = "ManualBehavior"


class RandomTacticBehavior(Behavior):

    name = "RandomTacticBehavior"

    def __init__(self, tactics):
        self.tactics = [ALL_MAJOR_TACTIC[tactic]() for tactic in tactics]

    def apply_to(self, unit):
        tactic = choice(self.tactics)
        actions = tactic.realize(unit)
        for action in actions:
            unit.append_action(action)


def behavior_constructor(loader, node):
    b_s = {}
    for key_node, value_node in node.value:
        if isinstance(value_node, SequenceNode) and value_node.tag == "tag:yaml.org,2002:seq":
            value = loader.construct_sequence(value_node)
        else:
            value = loader.construct_object(value_node)
        b_s[key_node.value] = value
    name = b_s.pop("name")
    return BEHAVIORS[name](**b_s)


BEHAVIOR_TAG = "!beh"
