from collections import ChainMap

from ...replication_manager import MetaRegistry
from ..property.property import (
    Property,
)
from .effect import MetaEffect
from ..property.reference import (
    Reference
)
from ...tools import dotdict

STATUSES = MetaRegistry()["Status"]
StatusMeta = MetaRegistry().make_registered_metaclass("Status")


class Status(metaclass=StatusMeta):

    """
    Контекстные значения статуса

    Наследуются от юнита
    owner: юнит наложивший статус
    source: клетка в которой находится юнит в момент взятия контекста
    ----
    Наследуются от действия
    action: действие наложившее статус
    ---
    Наследуются от эффекта
    effect: эффект наложивший статус
    carrier: юнит на который наложен статус
    ---
    Своё
    status: сам статус
    """

    name = None
    events = {}
    on_add_effects = []
    on_remove_effects = []
    params = []
    _tags = []

    def __init__(self, context=None, duration=-1, **kwargs):
        self.context = context
        self.duration = duration
        self.extra_tags = kwargs.get('extra_tags', [])
        if 'extra_tags' in kwargs:
            kwargs.pop('extra_tags')
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def tags(self):
        return self.extra_tags + self._tags

    def configure(self, context):
        # context = context.copy()
        # context['status'] = self
        context_values = {}
        for k, v in vars(self).items():
            if isinstance(v, Property):
                context_values[k] = v.get(context)
            else:
                context_values[k] = v
        new_status = self.__class__(**context_values)
        context = context.new_child()
        context['status'] = new_status
        new_status.context = context
        # new_status.on_add_effects = [e.get() for e in self.on_add_effects]
        # new_status.on_remove_effects = [e.get() for e in self.on_remove_effects]
        # new_status.events = {k: [v.get() for v in vv] for k, vv in self.events.items()}
        return new_status

    def on_add(self, target):
        for effect in self.on_add_effects:
            effect.get().apply(target.cell, self.context)

    def on_remove(self, target):
        for effect in self.on_remove_effects:
            effect.get().apply(target.cell, self.context)

    def tick(self):
        self.duration -= 1
        if self.duration == -1:
            self.context['target'].remove_status(self)

    def dump(self):
        params = vars(self).copy()
        # print("PARAMS", params)
        params['context'] = dict(params['context'])
        params['context'].pop('status')
        params['context'].pop('effect', None)
        params['context']['target'] = params['context']['target'].cell
        params['context']['owner'] = params['context']['owner'].cell
        params['context']['carrier'] = params['context']['carrier'].cell
        return {
            "name": self.name,
            "params": params,
        }

    def apply(self, event, target, context):
        effects = self.events.get(event, [])
        for effect_ref in effects:
            effect = effect_ref.get()
            if isinstance(effect, MetaEffect):
                effect.apply(target, self.context.new_child(), effect_context=context.new_child())
            else:
                new_context = self.context.new_child()
                for k, v in context.items():
                    if k in new_context:
                        new_context["target_" + k] = v
                    else:
                        new_context[k] = v
                # new_context['target_context'] = dotdict(context)
                # print(new_context)
                # new_context = {
                #     **self.context,
                #     **context,
                # }
                # print(new_context)
                effect.apply(self.context['carrier'].cell, new_context)

    def __repr__(self):
        return "Status {}".format(self.name)

    def __add__(self, other):
        assert self.__class__ is other.__class__
        return other

    def copy(self):
        return self.__class__(**vars(self))

    def expand(self):
        # pass
        # print(self.name)
        # print(self.context)
        self.context['target'] = self.context['target'].object
        self.context['owner'] = self.context['owner'].object
        self.context['carrier'] = self.context['carrier'].object
        self.context['status'] = self


class Dot(Status):
    params = ["power"]
    _tags = ["dot"]

    def __add__(self, other):
        assert self.__class__ is other.__class__
        self.power = max(self.power, other.power)
        self.duration = max(self.duration, other.duration)
        return self


def status_constructor(loader, node):
    s_s = loader.construct_mapping(node)
    name = s_s.pop("name")
    # status = STATUSES[name](**s_s)
    return Reference(name, s_s, STATUSES)


STATUS_TAG = "!status"


def new_status_constructor(loader, node):
    s_s = loader.construct_mapping(node)

    subtype = s_s.pop('subtype', None)
    # print(subtype)
    if subtype:
        status_type = STATUSES[subtype]
    else:
        status_type = Status

    class NewStatus(status_type):

        name = s_s.pop("name")
        on_add_effects = s_s.pop("on_add", []) or status_type.on_add_effects.copy()
        on_remove_effects = s_s.pop("on_remove", []) or status_type.on_remove_effects.copy()
        params = s_s.pop("params", []) or status_type.params.copy()
        events = {frozenset(k.split("_")[1::]): v for k, v in s_s.items()} or status_type.events.copy()
        _tags = s_s.pop("tags", []) or status_type._tags.copy()

    return NewStatus

NEW_STATUS_TAG = "!new_status"
