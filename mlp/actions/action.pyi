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
    pass

class CurrentActionBar:
    pass