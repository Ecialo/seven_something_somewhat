from itertools import (
    chain,
    combinations,
)


import blinker


from ..replication_manager import (
    GameObject,
)
from ..stats.new_stats import MajorStats
from ..grid import (
    Grid,
    Cell,
)
from ..actions.action import *
from ..tools import dict_merge
from ..actions.property.reference import Reference
from ..actions.base.status import Status

summon_event = blinker.signal("summon")
revoke = blinker.signal("revoke")
death = blinker.signal("death")
PLANNING, ACTION = range(2)


class UnitsRegistry:

    meta_registry = MetaRegistry()

    def __getitem__(self, item):
        return self.meta_registry['Unit'][item]

UNITS = UnitsRegistry()


class Unit(GameObject):

    # name = "Unit"
    hooks = []
    actions = []
    resources = {}

    def __init__(self, master_name=None, id_=None):
        super().__init__(id_)
        self.is_alive = True
        self._last_cell = None
        self.state = PLANNING
        self.presumed_path = []
        self.action_log = []
        self._stats = MajorStats(self, master_name, self.resources)
        self.current_action_bar = CurrentActionBar(self)
        registry = MetaRegistry()["Action"]
        for action_name in self.actions:
            self._stats.action_bar.append_action(registry[action_name])
        self.clear_presumed()
        self.context = {
            'source': self.cell,
            'owner': self
        }

    @property
    def action_bar(self):
        return self._stats.action_bar

    @property
    def _presumed_stats(self):
        return self._stats.presumed

    @property
    def presumed_cell(self):
        return self.cell

    @property
    def real_cell(self):
        return self._stats.cell

    @property
    def stats(self):
        if self.state == ACTION:
            return self._stats
        else:
            return self._presumed_stats

    @property
    def cell(self):
        return self.stats.cell

    @cell.setter
    def cell(self, cell):
        self.stats.cell = cell

    def place_in(self, cell):
        """
        Указать, что юнит на самом деле в этой клетке
        """
        self._stats.cell = cell

    def update_position(self):
        """
        Поместить юнит в нужную клетку
        """
        if self._last_cell:
            self._last_cell.take(self)
        if self.cell:
            self._last_cell = self.cell
            self.cell.place(self)

    def move(self, cell):
        """
        Передвинуть юнит
        """
        if self.state == PLANNING:
            self._presumed_stats.cell = cell
        else:
            self._stats.cell = cell
            self.update_position()

    def dump(self):
        return dict_merge(
            super().dump(),
            {
                'stats': self._stats.dump(),
                'is_alive': self.is_alive,
                'current_actions': self.current_action_bar.dump(),
            }
        )

    def load(self, struct):
        self._stats.load(struct['stats'])
        self.current_action_bar.load(struct['current_actions'])
        self.update_position()
        self.is_alive = struct['is_alive']

    @property
    def pos(self):
        try:
            return self.cell.pos
        except AttributeError:
            return None

    @pos.setter
    def pos(self, pos):
        if pos is None:
            return
        try:
            self.place_in(self.cell.grid[pos])
        except AttributeError:
            for obj in self.registry:
                if isinstance(obj, Grid):
                    self.place_in(obj[pos])

    def append_action(self, action):
        self.current_action_bar.append_action(action)

    def remove_action(self, action_index):
        self.current_action_bar.remove_action(action_index)

    def apply_actions(self, speed=SPEED.NORMAL):
        return self.current_action_bar.apply_actions(speed)

    def refill_action_points(self):
        self.stats.action_points += 999       # TODO сделать по людски
        for status in list(self.stats.statuses.values()):
            status.tick()

    def clear_presumed(self):
        self._stats.update_presumed()

    def __repr__(self):
        who = "{} {} at".format(self.stats.owner, self.__class__.__name__)
        where = "{}".format(self.stats.cell)
        return " ".join((who, where))

    def __cmp__(self, other):
        return 1 if id(self) > id(other) else (-1 if id(self) < id(other) else 0)

    def __eq__(self, other):
        return id(self) == id(other)

    def __lt__(self, other):
        return id(self) < id(other)

    def switch_state(self):
        self.state = int(not self.state)
        self.update_position()

    def add_status(self, status):
        if status.name in self.stats.statuses:
            old_status = self.stats.statuses[status.name]
            self.remove_status(old_status)
            new_status = old_status + status
            self.add_status(new_status)
        else:
            self.stats.statuses[status.name] = status
            for event in status.events:
                self.stats.triggers[event][status.name] = status
            status.on_add(self)
        # # print("STATUS", self.state, self.stats.statuses)

    def remove_status(self, status):
        s = self.stats.statuses.pop(status.name)
        for event in status.events:
            self.stats.triggers[event].pop(status.name)
        s.on_remove(self)

    def remove_status_by_tag(self, tag):
        status_to_remove = []
        for status in self.stats.statuses.values():
            if tag in status.tags:
                status_to_remove.append(status)
        for status in status_to_remove:
            self.remove_status(status)

    def launch_triggers(self, tags, target, target_context):
        l = len(tags)
        for event in chain(*(combinations(tags, j) for j in range(1, l+1))):
            event = frozenset(event)
            for trigger in list(self.stats.triggers[event].values()):
                trigger.apply(event, target, target_context)

    def change_owner(self, new_owner):
        self._stats.owner = new_owner
        self._presumed_stats.owner = new_owner

    def kill(self):
        self.is_alive = False
        death.send(unit=self)
        revoke.send(unit=self, cell=self.cell)

    def __contains__(self, item):
        if isinstance(item, Status):
            return item.name in self.stats.statuses
        elif isinstance(item, str):
            return item in self.stats.statuses
        else:
            raise TypeError("Wrong status type")


def new_unit_constructor(loader, node):
    u_s = loader.construct_mapping(node)

    @bind_widget('Unit')
    class NewUnit(Unit):
        name = u_s['name']
        actions = u_s['actions']
        widget = u_s['widget']
        resources = u_s['resources']

    NewUnit.__name__ = NewUnit.name
    return NewUnit

NEW_UNIT_TAG = "!new_unit"


def unit_constructor(loader, node):
    u_s = loader.construct_mapping(node)
    name = u_s.pop("name")
    # return UNITS[name](**u_s)
    return Reference(name, u_s, UNITS)

UNIT_TAG = "!unit"
