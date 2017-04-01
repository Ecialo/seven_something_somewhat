import yaml
from ..replication_manager import (
    # ActionsRegistry,
    ActionMeta,
)
from . import base
from .base.status import STATUSES
from ..protocol import Enum
from .base.effect import EFFECTS
from .base.trigger import TRIGGERS
from .area import AREAS
from ..bind_widget import bind_widget
from ..tools import dict_merge


FULL, MOVE, STANDARD = range(3)
type_ = Enum(
    "FULL",
    "MOVE",
    "STANDARD",
)
# FAST, NORMAL, SLOW = range(3)
speed = Enum(
    "FAST",
    "NORMAL",
    "SLOW",
)


class Property:

    def get(self, action):
        pass


class Attribute(Property):

    def __init__(self, name):
        self.name = name

    def get(self, action):
        return getattr(action, self.name)

    def __repr__(self):
        return "get {} from action".format(self.name)


class OwnerCell(Property):

    def get(self, action):
        return action.owner.cell

    def __repr__(self):
        return "get action owner cell"


class PresumedCell(Property):

    def get(self, action):
        return action.owner.presumed_cell


PROPERTY_TABLE = {
    'owner_cell': OwnerCell,
    'presumed_cell': PresumedCell,
}


class Action(metaclass=ActionMeta):
# class Action:
    hooks = []

    name = None
    cost = 0
    action_type = None
    action_speed = None

    setup_fields = []
    effects = []
    # area = None

    widget = None

    def __init__(self, owner, **kwargs):
        self.owner = owner
        for setup_struct in self.setup_fields:
            field_name = setup_struct['name']
            setattr(self, field_name, None)
        for key, value in kwargs.items():
            # field_name = setup_struct['name']
            setattr(self, key, value)
        effects = []
        for effect in self.effects:
            effects.append({
                'effect': effect['effect'].copy(),
                'configure': effect['configure'],
                'area': effect['area']
            })
        self.effects = effects
        # self.effects = [effect.copy() for effect in self.effects]

    def setup(self):
        for setup_struct in self.setup_fields:
            cursor_params = [
                p.get(self) if isinstance(p, Property) else p
                for p in setup_struct['cursor_params']
            ]
            value = yield [setup_struct['cursor']] + [cursor_params]
            setattr(self, setup_struct['name'], value)

    def clear(self):
        for setup_struct in self.setup_fields:
            field_name = setup_struct['name']
            setattr(self, field_name, None)

    def apply(self):
        # pass
        for effect_struct in self.effects:
            effect = effect_struct['effect']
            effect_args = {k: arg.get(self) for k, arg in effect_struct['configure'].items()}
            effect.configure(**effect_args)
            cells = effect_struct['area'].get(self)
            effect.apply(cells, self.owner)

    def pre_check(self):
        return True

    def post_check(self):
        return True

    def append_to_bar_effect(self):
        pass

    def remove_from_bar_effect(self):
        pass

    def dump(self):
        fields = {}
        for setup_field in self.setup_fields:
            name = setup_field['name']
            fields[name] = getattr(self, name)
        return dict_merge(
            {
                'name': self.name,
                'owner': self.owner,
            },
            fields
        )

    # def load(self, struct):
    #     for name, val in struct:
    #         pass


def property_constructor(loader, node):
    property_ = loader.construct_scalar(node)
    if property_ in PROPERTY_TABLE:
        return PROPERTY_TABLE[property_]()
    else:
        return Attribute(property_)

yaml.add_constructor("!prop", property_constructor)

ACTIONS_TABLE = {}


def actions_constructor(loader, node):
    a_s = loader.construct_mapping(node)

    @bind_widget("NewAction")
    class NewAction(Action):
        name = a_s['name']
        action_type = getattr(type_, a_s['action_type'])
        action_speed = getattr(speed, a_s['speed'])
        cost = a_s['cost']
        setup_fields = a_s['setup']
        # area = a_s['area']
        effects = a_s['effects']
        widget = a_s['widget']

    return NewAction

yaml.add_constructor("!new_action", actions_constructor)


def effect_constructor(loader, node):
    e_s = loader.construct_mapping(node)
    name = e_s.pop("name")
    effect = EFFECTS[name](**e_s)
    return effect

yaml.add_constructor("!eff", effect_constructor)


def area_constructor(loader, node):
    a_s = loader.construct_mapping(node)
    name = a_s.pop("name")
    area = AREAS[name](**a_s)
    return area

yaml.add_constructor("!area", area_constructor)


def status_constructor(loader, node):
    s_s = loader.construct_mapping(node)
    name = s_s.pop("name")
    status = STATUSES[name](**s_s)
    return status

yaml.add_constructor("!status", status_constructor)


def trigger_constructor(loader, node):
    s_s = loader.construct_mapping(node)
    name = s_s.pop("name")
    status = TRIGGERS[name](**s_s)
    return status

with open('./mlp/actions/actions.yaml') as a:
    c = yaml.load(a)

if __name__ == '__main__':
    print(c)
