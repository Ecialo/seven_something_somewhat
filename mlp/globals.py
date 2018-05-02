from .grid import HexGrid
from .actions.property.property import Property


class GridGlob(Property):
    def get(self, context=None):
        return HexGrid.get()


GLOBALS = {
    'arena': GridGlob()
}


def global_constructor(loader, node):
    glob = loader.construct_scalar(node)
    return GLOBALS[glob]


GLOBAL_TAG = "!glob"
