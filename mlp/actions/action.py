import os
from .new_action import SPEED
from ..replication_manager import MetaRegistry
from ..serialization import ActionTag
from ..bind_widget import bind_widget
# from ..tools import dict_merge
import logging
logger = logging.getLogger(__name__)
handler = logging.FileHandler(
    './game_logs/actions_sequence{}.log'.format("_server" if os.environ.get("IS_SERVER") else ""),
    'w',
)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
FULL, MOVE, STANDARD = range(3)
# FAST, NORMAL, SLOW = range(3)


@bind_widget("ActionBar")
class ActionBar:

    hooks = ["load", "append_action", "remove_action"]
    registry = MetaRegistry()["Action"]

    def __init__(self, owner):
        self.owner = owner
        self.actions = []

    def append_action(self, action):
        self.actions.append(action(self.owner))

    def remove_action(self, action_to_remove):
        for i, action in enumerate(self.actions):
            if action.name == action_to_remove.name:
                action_index = i
                print("HOORAY FOR", i)
                break
        else:
            return
        self.actions.pop(action_index)

    def dump(self):
        return [action.name for action in self.actions]

    def load(self, struct):
        self.actions = [self.registry[action_name](self.owner) for action_name in struct]
        print(self.actions)


@bind_widget("CurrentActionBar")
class CurrentActionBar:

    hooks = ['append_action', 'remove_action']

    def __init__(self, owner):
        self.owner = owner
        self.actions = []

    def append_action(self, action):
        # if self.check_slots(action) and action.pre_check() and action.post_check():
        if self.check_slots(action) and action.check():
            if self.actions and self.actions[-1].action_speed > action.action_speed:
                action.action_speed = self.actions[-1].action_speed
            self.actions.append(action)
            # action.append_to_bar_effect()

    def remove_action(self, action_index):
        self.actions.clear()
        # try:
        #     action = self.actions.pop(action_index)
        # except IndexError:
        #     action = self.actions.pop(0)
        # finally:
        # action.remove_from_bar_effect()

    def check_slots(self, action):
        action_type = action.action_type
        actions = self.actions
        l = len(actions)
        if l >= 2:
            print("NO TOMANY")
            return False
        elif l == 1:
            l_a_t = actions[-1].action_type
            if l_a_t == FULL:
                print("NO FULL")
                return False
            elif (
                    l_a_t == STANDARD and action_type == MOVE or
                    l_a_t == MOVE and action_type != FULL
            ):
                return True
            else:
                print("NO", action, actions)
                return False
        else:
            return True

    def apply_actions(self, speed=SPEED.NORMAL):
        any_action = bool(self.actions)
        for action in (action for action in self.actions if action.action_speed == speed):
            if action.pre_check():
                logger.debug("Action {}, Owner {}, Owner State {}, Speed {}, Actual Speed {}".format(
                    action, action.owner, action.owner.state, speed, action.action_speed
                ))
                action.apply()
        # self.clear()
        return any_action

    def clear(self):
        for i in range(len(self.actions)):
            self.remove_action(0)

    def dump(self):
        return [ActionTag(action) for action in self.actions]

    def load(self, struct):
        self.clear()
        for action in struct:
            self.append_action(action)

    def __iter__(self):
        return iter(self.actions)
