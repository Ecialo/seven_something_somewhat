from collections.abc import Iterable

import blinker

from ...commands.command import (
    Place,
    Revoke,
)
from ...commands import command as com
from .effect import (
    UnitEffect,
    MetaEffect,
    CellEffect,
    EFFECTS,
)
from .status import (
    Status,
    STATUSES,
)
from ..property.reference import ReferenceList
from ...replication_manager import MetaRegistry

trace = blinker.signal("trace")
summon = blinker.signal("summon")


class ActionsRegistry:

    meta_registry = MetaRegistry()

    def __getitem__(self, item):
        return self.meta_registry['Action'][item]

ACTIONS = ActionsRegistry()


class Move(UnitEffect):

    info_message = "{} move to {}"
    name = "Move"

    def __init__(self, **kwargs):
        self.path = kwargs['path']
        # print("TARGET COORD", self.target_coord)
        super().__init__(**kwargs)

    # def _apply(self, source_action, target):

    def _apply(self, target, context):
        # print("CONTEXT", context['action'].target_coord)
        with self.configure(context) as c:
            path = c.path
            grid = target.cell.grid
            if not isinstance(path, Iterable):
                path = [path]
            for path_part in path:
                # next_cell = grid.find_path(target.cell, path_part)[1]
                path = grid.find_path(target.cell, path_part)
                print(target.cell, path_part, path)
                next_cell = path[1]

                # send command

                if next_cell.object is None:
                    trace.send(command=com.Move(
                        unit=target,
                        path=[target.cell, next_cell]
                        # place=next_cell,
                        # old_place=target.cell
                    ))
                    # target.move(c.path)
                    target.move(next_cell)
            self.info_message = self.info_message.format(target, c.path)
            super()._apply(target, context)


class Damage(UnitEffect):

    name = "Damage"
    info_message = "{} take {} damage"
    _tags = ['harmful']

    def __init__(self, amount, **kwargs):
        super().__init__(**kwargs)
        self.amount = amount

    def _apply(self, target, context):
        with self.configure(context) as c:
            target.stats.health -= max(1, c.amount - target.stats.armor)
            if target.stats.health <= 0:
                trace.send(command=com.Revoke(target, target.cell))
                target.kill()
            self.info_message = self.info_message.format(target, c.amount)
            super()._apply(target, context)

    def __repr__(self):
        return "Damage: ({})".format(self.amount)


class AddStatus(UnitEffect):

    info_message = "add {} to {}"
    name = "AddStatus"

    def __init__(self, status, **kwargs):
        super().__init__(**kwargs)
        self.status = status

    def _apply(self, target, context):
        # if cell.object:
        with self.configure(context) as c:
            status = c.status.configure(context=context)
            target.add_status(status)
            self.info_message = self.info_message.format(c.status, target)
            super()._apply(target, context)

    def __repr__(self):
        return "Add Status {}".format(self.status.name)


class RemoveStatus(UnitEffect):

    info_message = "remove {} from {}"
    name = "RemoveStatus"

    def __init__(self, status, by_tag=False, **kwargs):
        super().__init__(**kwargs)
        self.status = ReferenceList(status)
        # self.status = status if isinstance(status, list) else [status]
        self.by_tag = by_tag

    def _apply(self, target, context):
        # if cell.object:
        with self.configure(context) as c:
            for status in c.status:
                if self.by_tag:
                    target.remove_status_by_tag(status)
                else:
                    target.remove_status(status)
            # self.info_message = self.info_message.format(c.status, target)
            # print(self.info_message)
            super()._apply(target, context)

    def __repr__(self):
        return "Remove Status {}{}".format(
            "by tag " if self.by_tag else "",
            self.status.get()
        )


class ChangeStat(UnitEffect):

    info_message = "change stat {} of {} to {}"
    name = "ChangeStat"

    def __init__(self, stat_name, value=None, **kwargs):
        self.stat_name = stat_name
        self.value = value
        super().__init__(stat_name=stat_name, value=value, **kwargs)

    # def configure(self, stat_name=None, value=None):
    #     self.value = value or self.value
    #     self.stat_name = stat_name or self.stat_name

    def _apply(self, target, context):
        with self.configure(context) as c:
            self.info_message = self.info_message.format(
                c.stat_name,
                target,
                c.value,
            )
            # print("SET")
            # print(target.stats, c.stat_name, c.value)
            setattr(target.stats, c.stat_name, c.value)
            super()._apply(target, context)

    def __repr__(self):
        return "Change stat {} to {}".format(self.stat_name, self.value)


# class Reflect(MetaEffect):
#
#     info_message = "reflect {} to {}"
#
#     def _apply(self, effect, context, effect_context):
#         print(context, "context")
#         print(effect_context, "effect_context")
#         effect.apply(effect_context['owner'].cell, context)
#         effect.cancel()


class Summon(CellEffect):

    name = "Summon"

    def __init__(self, unit, owner, **kwargs):
        super().__init__(**kwargs)
        self.unit = unit
        self.owner = owner

    def _apply(self, cell, context):
        with self.configure(context) as c:
            unit = c.unit
            unit.switch_state()
            unit.change_owner(c.owner)
            summon.send(unit=unit, cell=cell)
            super()._apply(cell, context)


class AddAction(UnitEffect):

    name = "AddAction"

    def __init__(self, action_name, **kwargs):
        super().__init__(**kwargs)
        self.action_name = action_name

    def _apply(self, target, context):
        with self.configure(context) as c:
            action = MetaRegistry()["Action"][c.action_name]
            target.stats.action_bar.append_action(action)


class RemoveAction(UnitEffect):

    name = "RemoveAction"

    def __init__(self, action_name, **kwargs):
        super().__init__(**kwargs)
        self.action_name = action_name

    def _apply(self, target, context):
        with self.configure(context) as c:
            action = MetaRegistry()["Action"][c.action_name]
            print(action, "ACTION REMOVE")
            target.stats.action_bar.remove_action(action)


class LaunchAction(CellEffect):

    def __init__(self, action_name, setup, **kwargs):
        super().__init__(**kwargs)
        self.action_name = action_name
        self.setup = setup

    def _apply(self, cell, context):
        with self.configure(context) as c:
            new_context = {
                'source': cell,
                'owner': context['owner']
            }
            action = ACTIONS[self.action_name](
                owner=context['owner'],
                context=new_context,
                **self.setup
            )
            action.context['action'] = action
            action.apply()


class Discard(MetaEffect):

    def _apply(self, effect, context):
        effect.cancel()


class Redirect(MetaEffect):

    def __init__(self, target, **kwargs):
        self.target = target
        super().__init__(**kwargs)

    def _apply(self, effect, context):
        with self.configure(context) as c:
            new_effect = effect.copy()
            new_context = {
                'source': context['source'],
                'owner': context['owner'],
            }
            new_effect.apply(c.target, new_context)


class ChangeEffectStat(MetaEffect):
    pass