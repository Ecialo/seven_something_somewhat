import os
import logging

from ..replication_manager import MetaRegistry
from ..bind_widget import bind_widget
from ..protocol import Enum
from .property.reference import Reference
from ..tools import dict_merge
from ..cursor import GeometrySelectCursor

# logger = logging.getLogger(__name__)
# handler = logging.FileHandler(
#     './game_logs/actions_sequence{}.log'.format("_server" if os.environ.get("IS_SERVER") else ""),
#     'w',
# )
# logger.addHandler(handler)
# logger.setLevel(logging.DEBUG)

ACTIONS = MetaRegistry()["Action"]
ActionMeta = MetaRegistry().make_registered_metaclass("Action")


FULL, MOVE, STANDARD = range(3)
type_ = Enum(
    "FULL",
    "MOVE",
    "STANDARD",
)

SPEED = Enum(
    "FAST",
    "NORMAL",
    "SLOW",
)


class Action(metaclass=ActionMeta):
    """
    Контекстные значения действия

    Наследуются от юнита
    owner: юнит делающий действие
    source: клетка в которой находится юнит в момент взятия контекста
    ----
    Свои
    action: само действие
    """

    hooks = []

    name = None
    cost = {}
    action_type = None
    action_speed = None

    setup_fields = []
    effects = []
    # area = None

    widget = None
    _check = None
    _tags = None

    def __init__(self, owner, speed=None, **kwargs):
        self.owner = owner
        self._context = None
        self.action_speed = self.action_speed if speed is None else speed
        for setup_struct in self.setup_fields:
            field_name = setup_struct['name']
            setattr(self, field_name, None)
        for key, value in kwargs.items():
            setattr(self, key, value)
        effects = []
        for effect in self.effects:
            effects.append({
                'effect': effect['effect'],
                'area': effect['area']
            })
        self.effects = effects

    @property
    def context(self):
        if self._context:
            return self._context
        else:
            context = self.owner.context
            context['action'] = self
            return context.new_child()

    @context.setter
    def context(self, value):
        self._context = value

    @property
    def tags(self):
        return self._tags

    def cursors(self):
        for setup_struct in self.setup_fields:
            if setup_struct['cursor'] == 'geometry':
                yield setup_struct['name'], GeometrySelectCursor(self, *setup_struct['cursor_params'])

    def setup(self, setup_dict=None):
        setup_dict = setup_dict or {}
        print(self.setup_fields, setup_dict)
        for setup_struct in self.setup_fields:
            print(setup_struct['name'], setup_dict)
            if setup_struct['name'] in setup_dict:
                value = setup_dict[setup_struct['name']]
            else:
                cursor_params = setup_struct['cursor_params']
                value = yield [setup_struct['cursor']] + [cursor_params]
            setattr(self, setup_struct['name'], value)

    def instant_setup(self, **fields):
        for setup_struct in self.setup_fields:
            value = fields[setup_struct['name']]
            setattr(self, setup_struct['name'], value)
        return self

    def clear(self):
        for setup_struct in self.setup_fields:
            field_name = setup_struct['name']
            setattr(self, field_name, None)

    def apply(self):
        for resource, cost in self.cost.items():
            setattr(self.owner.stats, resource, getattr(self.owner.stats, resource) - cost)
            # res = res and (getattr(self.owner.stats, resource) >= cost)
        # self.owner.stats.action_points -= self.cost
        for effect_struct in self.effects:
            effect = effect_struct['effect'].get()
            cells = effect_struct['area'].get(self.context)
            effect.apply(cells, self.context)

    def check(self):
        if self._check:
            res = self._check.get(self.context)
        else:
            res = True
        for resource, cost in self.cost.items():
            res = res and (getattr(self.owner.stats, resource) >= cost)
        return res

    def pre_check(self):
        return self.check()

    def append_to_bar_effect(self):
        pass

    def remove_from_bar_effect(self):
        pass

    def search_in_aoe(self, aggregator, extractor):
        for cursor_name, cursor in self.cursors():
            result = cursor.search_in_aoe(extractor)
            return {cursor_name: aggregator(result)}

    def dump(self):
        fields = {}
        for setup_field in self.setup_fields:
            name = setup_field['name']
            fields[name] = getattr(self, name)
        s = dict_merge(
            {
                'name': self.name,
                'owner': self.owner,
                'speed': self.action_speed,
            },
            fields
        )
        return s

    def copy(self):
        kwargs = {ss['name']: getattr(self, ss['name']) for ss in self.setup_fields}
        return self.__class__(self.owner, **kwargs)

    def __repr__(self):
        return "{} of {}".format(self.name, self.owner)


def action_constructor(loader, node):
    u_s = loader.construct_mapping(node)
    name = u_s.pop("name")
    return Reference(name, u_s, ACTIONS)


def new_action_constructor(loader, node):
    a_s = loader.construct_mapping(node)

    @bind_widget("NewAction")
    class NewAction(Action):
        name = a_s['name']
        action_type = getattr(type_, a_s['action_type'])
        action_speed = getattr(SPEED, a_s['speed'])
        cost = {'action_points': a_s['cost']} if isinstance(a_s['cost'], int) else a_s['cost']
        setup_fields = a_s['setup']
        effects = a_s['effects']
        widget = a_s['widget']
        _check = a_s.get('check')
        _tags = a_s.get('tags', [])
        signal = a_s.get('signal', {})

    return NewAction

NEW_ACTION_TAG = "!new_action"
ACTION_TAG = "!action"


@bind_widget("ActionBar")
class ActionBar:

    hooks = ["load", "append_action", "remove_action"]
    registry = MetaRegistry()["Action"]

    def __init__(self, owner):
        self.owner = owner
        self.actions = []

    def __iter__(self):
        return iter(self.actions)

    def append_action(self, action):
        self.actions.append(action(self.owner))

    def remove_action(self, action_to_remove):
        for i, action in enumerate(self.actions):
            if action.name == action_to_remove.name:
                action_index = i
                break
        else:
            return
        self.actions.pop(action_index)

    def dump(self):
        return [action.name for action in self.actions]

    def load(self, struct):
        self.actions = [self.registry[action_name](self.owner) for action_name in struct]


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
                # logger.debug("Action {}, Owner {}, Owner State {}, Speed {}, Actual Speed {}".format(
                #     action, action.owner, action.owner.state, speed, action.action_speed
                # ))
                action.apply()
        # self.clear()
        return any_action

    def clear(self):
        for i in range(len(self.actions)):
            self.remove_action(0)

    def dump(self):
        # return [ActionTag(action) for action in self.actions]
        return [action for action in self.actions]

    def load(self, struct):
        self.clear()
        for action in struct:
            self.append_action(action)

    def __iter__(self):
        return iter(self.actions)
