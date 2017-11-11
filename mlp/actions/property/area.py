from random import shuffle
from .property import Property
from ...grid import HexGrid
from ...tools import dotdict
from ...replication_manager import MetaRegistry

AREAS = MetaRegistry()['Area']
AreaMeta = MetaRegistry().make_registered_metaclass("Area")


class Area(Property, metaclass=AreaMeta):

    _grid = None

    def get(self, context):
        pass

    @property
    def grid(self):
        if not self._grid:
            self._grid = HexGrid.locate()
        return self._grid


class Cell(Area):

    def __init__(self, cell):
        self.cell = cell

    def get(self, context):
        return [self.cell.get(context)]


class Adjacent(Area):

    def __init__(self, center):
        self.center = center

    def get(self, context):
        center = self.center.get(context)
        return center.adjacent


class Melee(Area):

    def __init__(self, radius, center):
        self.radius = radius
        self.center = center

    def get(self, context):
        grid = self.grid
        for cell in grid.get_area(self.center.get(context), self.radius):
            if cell.object and cell.object.stats.owner != context['owner'].stats.owner:
                return [cell]
        return []


class Line(Area):

    def __init__(self, source, target, length):
        self.source = source
        self.target = target
        self.length = length

    def get(self, context):
        grid = self.grid
        return grid.get_line(self.source.get(context), self.target.get(context), self.length)


class KNearestNeighbors(Area):

    def __init__(self, source, area, k, filter):
        self.source = source
        self.area = area
        self.k = k
        self.filter = filter

    def get(self, context):
        grid = self.grid
        area = self.area.get(context)
        filter_ = self.filter
        source = self.source.get(context)
        d_pairs = [
            (grid.distance(cell, source), cell) for cell in area if filter_.get(dotdict({'object': cell.object}))
        ]
        return [pair[-1] for pair in sorted(d_pairs, reverse=True)[:self.k:]]


class KRandomCells(Area):

    def __init__(self, area, k, filter):
        self.area = area
        self.filter = filter
        self.k = k

    def get(self, context):
        cells = self.area.get(context)
        filter_ = self.filter
        actual_cells = [cell for cell in cells if filter_.get(dotdict({'cell': cell}))]
        shuffle(actual_cells)
        return actual_cells[:self.k:]


class Circle(Area):

    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    def get(self, context):
        return self.grid.get_area(self.center.get(context), self.radius)
        
class Ray(Area):

    def __init__(self, source, target, length):
        self.source = source
        self.target = target
        self.length = length

    def get(self, context):
        grid = self.grid
        line = grid.get_line(self.source.get(context), self.target.get(context), self.length)[1:]
        for i, cell in enumerate(line):
            if cell.object:
                return line[:i + 1]
        return line
        
class Tail(Area):

    def __init__(self, source, target, length, start=None):
        self.source = source
        self.target = target
        self.length = length
        self.start = start

    def get(self, context):
        grid = self.grid
        distance = grid.distance(self.source.get(context), self.target.get(context))
        start = self.start or distance
        line = grid.get_line(self.source.get(context), self.target.get(context), self.length + start)[start + 1:]
        return line
        
class CardinalWave(Area):

    def __init__(self, source, target, length):
        self.source = source
        self.target = target
        self.length = length

    def get(self, context):
        grid = self.grid
        distance = grid.distance(self.source.get(context), self.target.get(context))
        if distance == 0:
            return [self.source.get(context)]
        cardinal_target = grid.get_line(self.source.get(context), self.target.get(context), 2)[1]
        target_x, target_y, target_z = grid.offsets_to_cube(cardinal_target.pos)
        source_x, source_y, source_z = grid.offsets_to_cube(self.source.get(context).pos)
        left_x, left_y, left_z = (source_x + source_y - target_y - target_x, source_y + source_z - target_z - target_y, source_z + source_x - target_x - target_z)
        right_x, right_y, right_z = (source_x + source_z - target_z - target_x, source_y + source_x - target_x - target_y, source_z + source_y - target_y - target_z)
        center_line = grid.get_line(self.source.get(context), cardinal_target, self.length)[1:]
        result = []
        for cell in center_line:
            x, y, z = grid.offsets_to_cube(cell.pos)
            left = grid[grid.cube_to_offsets((x + left_x, y + left_y, z + left_z))]
            right = grid[grid.cube_to_offsets((x + right_x, y + right_y, z + right_z))]
            if left is not None:
                result.append(left)
            if right is not None:
                result.append(right)
        return center_line + result

def area_constructor(loader, node):
    a_s = loader.construct_mapping(node)
    name = a_s.pop("name")
    area = AREAS[name](**a_s)
    return area

AREA_TAG = "!area"
