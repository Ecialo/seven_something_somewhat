import yaml
from .actions.action import (
    new_action_constructor,
    action_constructor,
    NEW_ACTION_TAG,
    ACTION_TAG
)
from .actions.base.effect import (
    effect_constructor,
    new_effect_constructor,
    NEW_EFFECT_TAG,
    EFFECT_TAG
)
from .actions.base.status import (
    status_constructor,
    STATUS_TAG,
    new_status_constructor,
    NEW_STATUS_TAG
)
from .actions.property.property import (
    property_constructor,
    PROPERTY_TAG,
)
from .actions.property.expression import (
    expression_constructor,
    EXPRESSION_TAG
)
from .actions.property.area import (
    area_constructor,
    AREA_TAG,
)
from .unit.unit import (
    unit_constructor,
    UNIT_TAG,
    new_unit_constructor,
    NEW_UNIT_TAG,
)
from .resource import (
    resource_constructor,
    RESOURCE_TAG,
)
from .grid import (
    cell_constructor,
    CELL_TAG,
)
from .player import Player

yaml.add_constructor(NEW_ACTION_TAG, new_action_constructor)
yaml.add_constructor(ACTION_TAG, action_constructor)

yaml.add_constructor(EFFECT_TAG, effect_constructor)
yaml.add_constructor(NEW_EFFECT_TAG, new_effect_constructor)

yaml.add_constructor(STATUS_TAG, status_constructor)
yaml.add_constructor(NEW_STATUS_TAG, new_status_constructor)

yaml.add_constructor(PROPERTY_TAG, property_constructor)
yaml.add_constructor(EXPRESSION_TAG, expression_constructor)
yaml.add_constructor(AREA_TAG, area_constructor)

yaml.add_constructor(UNIT_TAG, unit_constructor)
yaml.add_constructor(NEW_UNIT_TAG, new_unit_constructor)

yaml.add_constructor(RESOURCE_TAG, resource_constructor)

yaml.add_constructor(CELL_TAG, cell_constructor)


def load(paths=None):
    paths = paths or [
        './mlp/actions/base/effects.yaml',
        './mlp/actions/base/statuses.yaml',
        './mlp/actions/actions.yaml',
        './mlp/unit/units.yaml',
    ]
    for path in paths:
        with open(path) as a:
            yaml.load(a)
