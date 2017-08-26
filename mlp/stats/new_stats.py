from collections import defaultdict
from .stats import (
    PLANNING
)
from ..actions.action import ActionBar
from ..tools import dict_merge
from ..bind_widget import bind_widget
from ..resource import (
    Resource,
    RESOURCE_TABLE,
)


class Stats:

    # hooks = ['load']
    hooks = []

    def __init__(self, owner, owner_name, resources):#, is_presumed=False):
        # self.resources = resources.copy()
        self.resources = {}
        self.state = PLANNING
        self.name = owner.__class__.__name__
        self.owner = owner_name
        self._triggers = defaultdict(dict)
        self.statuses = {}
        self.cell = None
        self.action_bar = ActionBar(owner)
        for name, resource in resources.items():
            if isinstance(resource, Resource):
                resource = resource.copy()
                setattr(self, name, resource)
                self.resources[name] = resource.copy()
            else:
                resource = RESOURCE_TABLE[type(resource)](name, resource)
                setattr(self, name, resource)
                # self.resources[name] = RESOURCE_TABLE[type(resource)](name, resource)
                self.resources[name] = resource
            # resource.name_ = name
        print("\n\nSTATS", self.resources, "\n\n")

    @property
    def triggers(self):
        return self._triggers

    @triggers.setter
    def triggers(self, value):
        self._triggers = defaultdict(value)

    def load(self, struct):
        action_bar = struct.pop("action_bar")
        resources = struct.pop("resources")
        self.action_bar.load(action_bar)
        for key, value in struct.items():
            setattr(self, key, value)
        for key, value in resources.items():
            self.resources[key].value = value
            # setattr(self, key, value)
        struct["action_bar"] = action_bar
        # print(self.statuses)

    def dump(self):
        print("\n\n", self.resources, "\n\n")
        # status = self.statuses.copy()
        struct = {
            "name": self.name,
            "owner": self.owner,
            'cell': self.cell,
            'statuses': self.statuses.copy(),
            'resources': {key: value.dump() for key, value in self.resources.items()},
            'action_bar': self.action_bar.dump(),
        }
        return struct

    def __setattr__(self, key, value):
        try:
            if key in self.resources:
                self.resources[key].value = value
                value = self.resources[key]
        except AttributeError:
            pass
        super().__setattr__(key, value)

    def __getattribute__(self, item):
        item = super().__getattribute__(item)
        if isinstance(item, Resource):
            return item.value
        else:
            return item

    def __repr__(self):
        return "Stats with resources {}".format(self.resources)


@bind_widget("Stats")
class MajorStats(Stats):

    def __init__(self, name, owner, resources):
        super().__init__(name, owner, resources)
        self.presumed = Stats(name, owner, resources)

    def load(self, struct):
        presumed = struct.pop('presumed')
        self.presumed.load(presumed)
        super().load(struct)

    def dump(self):
        return dict_merge(
            super().dump(),
            {'presumed': self.presumed.dump()}
        )

    def update_presumed(self):
        struct = self.dump()
        struct.pop('presumed')
        self.presumed.load(struct)

    def __repr__(self):
        return "Major stats with resources {}".format(self.resources)
