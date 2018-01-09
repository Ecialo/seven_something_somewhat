from typing import (
    Iterable,
    Tuple,
    ClassVar,
    List,
    Dict,
    Any,
    Callable,
)

from ..cursor import GeometrySelectCursor
from ..protocol import Enum

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

class ActionBar:

    def __iter__(self) -> Iterable[Action]: ...

class CurrentActionBar:

    actions: List[Action]

    def clear(self) -> None: ...
    def remove_action(self, action_index: int) -> None: ...