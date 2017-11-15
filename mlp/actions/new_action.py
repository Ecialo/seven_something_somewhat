import yaml
from ..replication_manager import (
    MetaRegistry
)
from ..protocol import Enum
from ..bind_widget import bind_widget
from ..tools import dict_merge
from .property.property import (
    Property,
    Const,
)
from .property.reference import Reference


FULL, MOVE, STANDARD = range(3)
type_ = Enum(
    "FULL",
    "MOVE",
    "STANDARD",
)
# FAST, NORMAL, SLOW = range(3)
SPEED = Enum(
    "FAST",
    "NORMAL",
    "SLOW",
)

ACTIONS = MetaRegistry()["Action"]
ActionMeta = MetaRegistry().make_registered_metaclass("Action")


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
    _check = None

    def __init__(self, owner, speed=None, **kwargs):
        # print("CREATE NEW")
        # print(kwargs)
        self.owner = owner
        self._context = None
        self.action_speed = self.action_speed if speed is None else speed
        for setup_struct in self.setup_fields:
            field_name = setup_struct['name']
            setattr(self, field_name, None)
        for key, value in kwargs.items():
            # field_name = setup_struct['name']
            setattr(self, key, value)
        effects = []
        for effect in self.effects:
            effects.append({
                # 'effect': effect['effect'].copy(),
                'effect': effect['effect'],
                # 'configure': effect['configure'],
                'area': effect['area']
            })
        self.effects = effects

    @property
    def context(self):
        if self._context:
            return self._context
        else:
            return {
                'action': self,
                'owner': self.owner,
                'source': self.owner.cell,
            }

    @context.setter
    def context(self, value):
        self._context = value

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

    def clear(self):
        for setup_struct in self.setup_fields:
            field_name = setup_struct['name']
            setattr(self, field_name, None)

    def apply(self):
        self.owner.stats.action_points -= self.cost
        for effect_struct in self.effects:
            effect = effect_struct['effect'].get()
            # effect_args = {k: arg.get(self) for k, arg in effect_struct['configure'].items()}
            # effect.configure(**effect_args)
            cells = effect_struct['area'].get(self.context)
            # effect.apply(cells, self.owner)
            effect.apply(cells, self.context)

    def check(self):
        if self._check:
            res = self._check.get(self.context)
        else:
            res = True
        return res and self.owner.stats.action_points >= self.cost

    def pre_check(self):
        # res = self.check.get(self)
        # print(res, self.check)
        return self.check()

    # def post_check(self):
    #     return self.pre_check()

    def append_to_bar_effect(self):
        pass

    def remove_from_bar_effect(self):
        pass

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

        # print("DUMP ACTION", s)
        return s

    def copy(self):
        kwargs = {ss['name']: getattr(self, ss['name']) for ss in self.setup_fields}
        return self.__class__(self.owner, **kwargs)

    def __repr__(self):
        return "{} of {}".format(self.name, self.owner)

    # def load(self, struct):
    #     for name, val in struct:
    #         pass

# ACTIONS_TABLE = {}


def action_constructor(loader, node):
    u_s = loader.construct_mapping(node)
    name = u_s.pop("name")
    # return UNITS[name](**u_s)
    return Reference(name, u_s, ACTIONS)


def new_action_constructor(loader, node):
    a_s = loader.construct_mapping(node)

    @bind_widget("NewAction")
    class NewAction(Action):
        name = a_s['name']
        action_type = getattr(type_, a_s['action_type'])
        action_speed = getattr(SPEED, a_s['speed'])
        cost = a_s['cost']
        setup_fields = a_s['setup']
        effects = a_s['effects']
        widget = a_s['widget']
        _check = a_s.get('check')

    return NewAction

NEW_ACTION_TAG = "!new_action"
ACTION_TAG = "!action"


# def trigger_constructor(loader, node):
#     s_s = loader.construct_mapping(node)
#     name = s_s.pop("name")
#     status = TRIGGERS[name](**s_s)
#     return status
#
# with open('./mlp/actions/actions.yaml') as a:
#     c = yaml.load(a)

# if __name__ == '__main__':
#     print(c)
