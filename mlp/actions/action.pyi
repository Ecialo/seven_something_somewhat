from typing import (
    Iterable,
    Tuple,
    ClassVar,
    List,
    Dict,
    Any,
)

from ..cursor import GeometrySelectCursor


class Action:

    setup_fields: ClassVar[List[Dict[str, Any]]]

    def cursors(self) -> Iterable[Tuple(str, GeometrySelectCursor)]: ...
    def copy(self) -> Action: ...

class ActionBar:
    pass

class CurrentActionBar:
    pass