from typing import (
    Iterable,
    Tuple,
    ClassVar,
    List,
    Dict,
    Any,
    Callable,
)

import yaml

from ..unit import Unit
from ..cursor import GeometrySelectCursor
from ..protocol import Enum
from .property.reference import Reference

SPEED: Enum

class Action:

    setup_fields: ClassVar[List[Dict[str, Any]]]

    def cursors(self) -> Iterable[Tuple(str, GeometrySelectCursor)]: ...
    def copy(self) -> Action: ...
    def instant_setup(self, **kwargs) -> Action: ...
    def search_in_aoe(
            self,
            aggregator: Callable[[Dict[Any, Any]], Any],
            extractor: Callable,
    ) -> Dict[str, Any]: ...
    def check(self) -> bool: ...

class ActionBar:

    def __iter__(self) -> Iterable[Action]: ...

class CurrentActionBar:

    actions: List[Action]

    def __init__(self, owner: Unit) -> None: ...

    def clear(self) -> None: ...
    def remove_action(self, action_index: int) -> None: ...

def new_action_constructor(loader: yaml.Loader, node: yaml.Node) -> type: ...
NEW_ACTION_TAG: str

def action_constructor(loader: yaml.Loader, node: yaml.Node) -> Reference: ...
ACTION_TAG: str
