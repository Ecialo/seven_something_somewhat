import logging
import os
from yaml import SequenceNode
from ...tools import (
    # convert,
    dotdict,
)
from ..property.property import (
    Property,
    # Const,
)
from ..property.reference import (
    Reference
)
from ...replication_manager import MetaRegistry
from collections.abc import Iterable
from contextlib import contextmanager

# logger = logging.getLogger(__name__)
# handler = logging.FileHandler(
#     './game_logs/apply_effects{}.log'.format("_server" if os.environ.get("IS_SERVER") else ""),
#     'w',
# )
# logger.addHandler(handler)
# logger.setLevel(logging.DEBUG)

PLANNING = 0
EFFECTS = MetaRegistry()['Effect']
EffectMeta = MetaRegistry().make_registered_metaclass("Effect")


class AbstractEffect(metaclass=EffectMeta):

    info_message = ""
    name = ""
    _tags = []

    def __init__(self, area=None, **kwargs):
        self.is_canceled = False
        self.extra_tags = kwargs.get('extra_tags', [])
        self.area = area

    def log(self, source):
        pass
        # logger.debug(
        #     "Effect {} with context".format(self.name)
        # )

    @property
    def tags(self):
        return self.extra_tags + self._tags

    @contextmanager
    def configure(self, context):
        context_values = dotdict()
        for k, v in vars(self).items():
            if isinstance(v, Property):
                context_values[k] = v.get(context)
            else:
                context_values[k] = v
        yield context_values

    def apply(self, *args, **kwargs):
        pass

    def cancel(self):
        self.is_canceled = True


class UnitEffect(AbstractEffect):

    def __init__(self, **kwargs):
        self.info_message = self.info_message
        super().__init__(**kwargs)

    def _apply(self, target, context):
        source = context['source']
        self.log(source)

    def apply(self, cells, context):
        """
        Контекст, это контекст действия вызывающего эффект
        """
        logging.debug("Effect {} cells {}".format(self, cells))
        if self.area:
            cells = self.area.get(context)
        if context['owner'].state is PLANNING and "plan" not in self.tags:
            return
        if not isinstance(cells, Iterable):
            cells = [cells]
        for cell in cells:
            if cell.object is not None:
                # effect_context = context.copy()
                effect_context = context
                effect_context['target'] = cell.object
                effect = self.copy()
                cell.object.launch_triggers(self.tags, effect, effect_context.new_child())
                if not effect.is_canceled:
                    effect._apply(cell.object, effect_context)
                    context['owner'].launch_triggers(["apply"] + self.tags, effect, effect_context.new_child())

    def copy(self):
        return self.__class__(**vars(self))


class CellEffect(AbstractEffect):

    def _apply(self, cell, context):
        source = context['source']
        self.log(source)

    def apply(self, cells, context):
        """
        Контекст, это контекст действия вызывающего эффект
        """
        if self.area:
            cells = self.area.get(context)
        if context['owner'].state is PLANNING and "plan" not in self.tags:
            return
        if not isinstance(cells, Iterable):
            cells = [cells]
        for cell in cells:
            # effect_context = context.copy()
            effect_context = context
            effect_context['cell'] = cell
            effect = self.copy()
            if not effect.is_canceled:
                effect._apply(cell, effect_context.new_child())

    def copy(self):
        return self.__class__(**vars(self))


class MetaEffect(AbstractEffect):

    def log(self, source):
        pass
        # source.action_log.append(self.info_message)

    def _apply(self, effect, context):
        self.log(context)

    def apply(self, effect, context, effect_context):
        """
        Контекст, это контекст действия вызывающего эффект
        """
        # context = context
        context['incoming_effect'] = effect
        context['incoming_effect_context'] = dotdict(effect_context)
        self._apply(effect, context.new_child())

    def copy(self):
        return self.__class__(**vars(self))


class CustomUnitEffect(UnitEffect):
    """
    Контекстные значения эффекта

    Наследуются от юнита
    owner: юнит делающий действие вызывающее эффект
    source: клетка в которой находится юнит в момент взятия контекста
    ----
    Наследуются от действия
    action: действие вызывающее эффект
    ---
    Свои
    effect: сам эффект
    """

    name = None
    params = []
    effects = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for k, v in kwargs.items():
            setattr(self, k, v)

    def apply(self, cells, context):
        context['effect'] = self
        super().apply(cells, context.new_child())

    def _apply(self, target, context):
        for e_s in self.effects:
            cond = e_s.get('condition')
            # print(context)
            if cond is None or cond.get(context):
                effect = e_s['effect'].get()
                # print(context)
                # print(effect)
                effect._apply(target, context)     # TODO перепроектировать это


class CustomMetaEffect(MetaEffect):

    name = None
    params = []
    effects = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for k, v in kwargs.items():
            setattr(self, k, v)

    def apply(self, effect, context, effect_context):
        # context = context.copy()
        context['incoming_effect'] = effect
        context['incoming_effect_context'] = dotdict(effect_context)
        context['effect'] = self
        self._apply(effect, context.new_child())

    def _apply(self, effect, context):
        for e_s in self.effects:
            cond = e_s.get('condition')
            # print(cond)
            if cond is None or cond.get(context):
                # print('SUCC')
                effect_ = e_s['effect']
                effect_ = effect_.get()
                effect_._apply(effect, context)


def effect_constructor(loader, node):
    e_s = {}
    for key_node, value_node in node.value:
        if isinstance(value_node, SequenceNode) and value_node.tag == "tag:yaml.org,2002:seq":
            value = loader.construct_sequence(value_node)
        else:
            value = loader.construct_object(value_node)
        e_s[key_node.value] = value
    name = e_s.pop("name")
    return Reference(name, e_s, EFFECTS)


def new_effect_constructor(loader, node):
    n_e = loader.construct_mapping(node)

    if "type" in n_e:
        type_ = n_e.pop("type")
    else:
        type_ = "unit"

    if type_ == "unit":
        class NewEffect(CustomUnitEffect):
            name = n_e["name"]
            effects = n_e['effects']
            params = n_e['params']
    elif type_ == "meta":
        class NewEffect(CustomMetaEffect):
            name = n_e["name"]
            effects = n_e['effects']
            params = n_e['params']
    else:
        raise ValueError("Effect type might be 'unit' or 'meta'")
    return NewEffect


EFFECT_TAG = "!eff"
NEW_EFFECT_TAG = "!new_eff"
