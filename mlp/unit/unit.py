from itertools import (
    chain,
    combinations,
)
from collections import ChainMap
import logging as log

import blinker

from ..replication_manager import (
    GameObject,
    MetaRegistry,
)
from ..stats.new_stats import MajorStats
from ..grid import (
    Grid,
)
from .behavior.behavior import ManualBehavior, RandomTacticBehavior
from ..actions.action import *
from ..tools import dict_merge
from ..actions.property.reference import Reference
from ..actions.base.status import Status
from ..bind_widget import bind_widget
from ..bot.influence_map.threat_map import threat_signal
from ..bot.tactic import ALL_MAJOR_TACTIC

summon_event = blinker.signal("summon")
revoke = blinker.signal("revoke")
death = blinker.signal("death")
kill = blinker.signal('kill')
PLANNING, ACTION = range(2)


class UnitsRegistry:

    meta_registry = MetaRegistry()

    def __getitem__(self, item):
        return self.meta_registry['Unit'][item]


UNITS = UnitsRegistry()


class Unit(GameObject):

    """
    Контекстные значения юнита
    owner: сам юнит
    source: клетка в которой находится юнит в момент взятия контекста
    """

    behavior = None
    hooks = []
    actions = []
    resources = {}
    initial_statuses = []
    playable = False

    exposed = [
        'has_status_by_tag'
    ]

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
        self._context = ChainMap({
            'owner': self,
        })
        self.switch_state()
        context = self.context.copy()
        context['carrier'] = self
        for status_ref in self.initial_statuses:
            status = status_ref.get().configure(context)
            self.add_status(status)
        self.switch_state()

        kill.connect(self.on_kill)

    def __getattribute__(self, item):
        try:
            return super().__getattribute__(item)
        except AttributeError:
            return getattr(super().__getattribute__('stats'), item)

    @property
    def context(self):
        context = self._context.new_child()
        context['source'] = self.cell
        return context

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
            self.stats.add_status(status)
            status.on_add(self)
        # # print("STATUS", self.state, self.stats.statuses)

    def remove_status(self, status):
        s = self.stats.remove_status(status)
        s.on_remove(self)

    def remove_status_by_tag(self, tag):
        status_to_remove = []
        for status in self.stats.statuses.values():
            if tag in status.tags:
                status_to_remove.append(status)
        for status in status_to_remove:
            self.remove_status(status)

    def launch_triggers(self, tags, target, target_context):
        """
        target: для эффекта это эффект, для иного сам юнит
        """
        log.debug("{tags}, {unit}".format(tags=tags, unit=self))
        is_on_apply = "apply" in tags
        if is_on_apply:
            tags.remove("apply")
        l = len(tags)
        for event in chain(*(combinations(tags, j) for j in range(1, l + 1))):
            if is_on_apply:
                event += ("apply", )
            event = frozenset(event)
            for trigger in list(self.stats.triggers[event].values()):
                trigger.apply(event, target, target_context)

    def change_owner(self, new_owner):
        self._stats.owner = new_owner
        self._presumed_stats.owner = new_owner

    def kill(self):
        if self.is_alive:
            self.is_alive = False
            kill.disconnect(self.on_kill)
            self.current_action_bar.clear()
            death.send(unit=self)
            revoke.send(unit=self, cell=self.cell)

    def expand(self):
        self._stats.expand()

    def __contains__(self, item):
        if isinstance(item, Status):
            return item.name in self.stats.statuses
        elif isinstance(item, str):
            return item in self.stats.statuses
        else:
            raise TypeError("Wrong status type")

    @property
    def signal(self):
        signals = []
        for action in self.action_bar:
            if action.check():
                signals.append(action.signal)
        # return threat_signal(**self.raw_signal)

    def behave(self):
        self.behavior.apply_to(self)

    def on_kill(self, killer, victim):
        context = self.context.new_child({
            'target': self,
            'killer': killer,
            'victim': victim,
        })
        self.launch_triggers(['kill'], self, context)

    def has_status_by_tag(self, tag):
        for status in self.stats.statuses.values():
            if tag in status.tags:
                return True
        return False

def new_unit_constructor(loader, node):
    u_s = loader.construct_mapping(node)

    behavior = u_s.get('behavior', ManualBehavior())
    # print(behavior)
    if isinstance(behavior, dict):
        # print(behavior)
        tactics = [ALL_MAJOR_TACTIC[tactic_name] for tactic_name in behavior['tactics']]
        class_behavior = RandomTacticBehavior(tactics)
        # class_behavior = behavior
    else:
        # pass
        class_behavior = behavior

    @bind_widget('Unit')
    class NewUnit(Unit):
        name = u_s['name']
        actions = u_s['actions']
        widget = u_s['widget']
        resources = u_s['resources']
        playable = u_s.get('playable', False)
        initial_statuses = u_s.get('statuses', [])
        behavior = class_behavior
        # behavior = None

    NewUnit.__name__ = NewUnit.name
    return NewUnit


NEW_UNIT_TAG = "!new_unit"


def unit_constructor(loader, node):
    u_s = loader.construct_mapping(node)
    name = u_s.pop("name")
    # return UNITS[name](**u_s)
    return Reference(name, u_s, UNITS)


UNIT_TAG = "!unit"
