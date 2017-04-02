from .effect import (
    UnitEffect,
    MetaEffect,
    EFFECTS,
)
from .status import (
    Status,
    STATUSES,
)
from .trigger import (
    Trigger,
    TRIGGERS,
)


class Move(UnitEffect):

    info_message = "{} move to {}"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.target_coord = None

    def configure(self, target_coord):
        self.target_coord = target_coord

    # def _apply(self, source_action, target):

    def _apply(self, target, source):
        # if cell.object:
        print(self.info_message.format(target, self.target_coord))
        # print(target.object)
        target.move(self.target_coord)
        self.info_message = self.info_message.format(target, self.target_coord)
        super()._apply(target, source)


class Damage(UnitEffect):

    info_message = "{} take {} damage"

    def __init__(self, amount, **kwargs):
        super().__init__(**kwargs)
        self.amount = amount

    def _apply(self, target, source):
        # if cell.object:
            # for cell in cells:
            #     if cell.object:
        target.stats.health -= self.amount
        self.info_message = self.info_message.format(target, self.amount)
        super()._apply(target, source)


class AddStatus(UnitEffect):

    info_message = "add {} to {}"

    def __init__(self, status, **kwargs):
        super().__init__(**kwargs)
        self.status = status

    def _apply(self, target, source):
        # if cell.object:
        status = self.status.copy()
        status.configure(source=source)
        target.add_status(status)
        self.info_message = self.info_message.format(self.status, target)
        super()._apply(target, source)


class RemoveStatus(UnitEffect):

    info_message = "remove {} from {}"

    def __init__(self, status, **kwargs):
        super().__init__(**kwargs)
        self.status = status

    def _apply(self, target, source):
        # if cell.object:
        target.remove_status(self.status)
        self.info_message = self.info_message.format(self.status, target)
        print(self.info_message)
        super()._apply(target, source)


class ChangeStat(UnitEffect):

    info_message = "change stat {} of {} to {}"

    def __init__(self, stat_name, value=None, **kwargs):
        super().__init__(**kwargs)
        self.stat_name = stat_name
        self.value = value

    def configure(self, stat_name=None, value=None):
        self.value = value or self.value
        self.stat_name = stat_name or self.stat_name

    def _apply(self, target, source):
        self.info_message = self.info_message.format(
            self.stat_name,
            target,
            self.value,
        )
        setattr(target.stats, self.stat_name, self.value)
        super()._apply(target, source)


class Reflect(MetaEffect):

    info_message = "reflect {} to {}"

    def _apply(self, effect, source, effect_source):
        # print(source, "source")
        # print(effect_source, "effect_source")
        effect.apply(effect_source.cell, source)
        effect.cancel()


class WithRifle(Status):

    # name = "WithRifle"

    def on_add(self, target):
        target.stats.unit_state = "rifle"

    def on_remove(self, target):
        target.stats.unit_state = "sword"


class Parry(Status):

    name = "Parry"

    def on_add(self, target):
        target.add_trigger(ParryTrigger(source=self.source))

    def on_remove(self, target):
        target.remove_trigger(ParryTrigger())


class ParryTrigger(Trigger):

    name = "Parry"
    events = ["on_phase_start", "on_take_damage"]
    on_take_damage = [Reflect()]#, RemoveStatus(Parry())]
    on_phase_start = [RemoveStatus(Parry())]


TRIGGERS.update({
    'Parry': ParryTrigger,
})


STATUSES.update({
    "WithRifle": WithRifle,
    "Parry": Parry,
})


EFFECTS.update({
    'Move': Move,
    'Damage': Damage,
    'AddStatus': AddStatus,
    'RemoveStatus': RemoveStatus,
    'Reflect': Reflect,
    'ChangeStat': ChangeStat,
})
