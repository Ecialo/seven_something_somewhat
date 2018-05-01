from .grid import HexGrid

GLOBALS = {
    'arena': HexGrid
}


def global_constructor(loader, node):
    glob = loader.construct_scalar(node)
    return GLOBALS[glob].get()


GLOBAL_TAG = "!glob"
