import logging as log
from random import shuffle
from contextlib import contextmanager

from .property import Property
from ...grid import (
    HexGrid,
    FixedArea
)
from ...tools import dotdict
from ...replication_manager import MetaRegistry

AREAS = MetaRegistry()['Area']
AreaMeta = MetaRegistry().make_registered_metaclass("Area")


class Area(Property, metaclass=AreaMeta):

    _grid = None
    color = None

    def get(self, context):
        return FixedArea(self._get(context), self.color)

    def _get(self, context):
        pass

    @contextmanager
    def configure(self, context):
        context_values = dotdict()
        for k, v in vars(self).items():
            if isinstance(v, Property):
                context_values[k] = v.get(context)
            else:
                context_values[k] = v
        yield context_values

    @property
    def grid(self):
        if not self._grid:
            self._grid = HexGrid.locate()
        return self._grid


class Cell(Area):

    def __init__(self, cell):
        self.cell = cell

    def _get(self, context):
        return [self.cell.get(context)]


class Adjacent(Area):

    def __init__(self, center):
        self.center = center

    def _get(self, context):
        center = self.center.get(context)
        return center.adjacent


class Melee(Area):

    def __init__(self, radius, center):
        self.radius = radius
        self.center = center

    def _get(self, context):
        grid = self.grid
        for cell in grid.get_area(self.center.get(context), self.radius):
            log.debug("Cell {} CellObj {} Owner {}".format(
                cell,
                cell.object.stats.owner if cell.object else None,
                context['owner'].stats.owner
            ))
            if cell.object and cell.object.stats.owner != context['owner'].stats.owner:
                return [cell]
        return []


class Line(Area):

    def __init__(self, source, target, length):
        self.source = source
        self.target = target
        self.length = length

    def _get(self, context):
        grid = self.grid
        with self.configure(context) as c:
            return grid.get_line(c.source, c.target, c.length)
            # return grid.get_line(self.source.get(context), self.target.get(context), self.length)


class KNearestNeighbors(Area):

    def __init__(self, source, area, k, filter):
        self.source = source
        self.area = area
        self.k = k
        self.filter = filter

    def _get(self, context):
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

    def _get(self, context):
        cells = self.area.get(context)
        filter_ = self.filter
        actual_cells = [cell for cell in cells if filter_.get(dotdict({'cell': cell}))]
        shuffle(actual_cells)
        return actual_cells[:self.k:]


class Circle(Area):

    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    def _get(self, context):
        return self.grid.get_area(self.center.get(context), self.radius)


class Ring(Area):

    def __init__(self, center, radius, inner_radius=None):
        self.center = center
        self.radius = radius
        self.inner_radius = inner_radius

    def _get(self, context):
        return self.grid.get_ring(self.center.get(context), self.radius, self.inner_radius)


class Ray(Area):

    def __init__(self, source, target, length):
        self.source = source
        self.target = target
        self.length = length

    def _get(self, context):
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

    def _get(self, context):
        grid = self.grid
        distance = grid.distance(self.source.get(context), self.target.get(context))
        if self.start is None:
            start = distance
        else:
            start = self.start
        line = grid.get_line(self.source.get(context), self.target.get(context), self.length + start)[start + 1:]
        return line


class CardinalWave(Area):

    def __init__(self, source, target, length):
        self.source = source
        self.target = target
        self.length = length

    def _get(self, context):
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

class Cone60(Area):

    def __init__(self, source, target, length):
        self.source = source
        self.target = target
        self.length = length

    def _get(self,context):
        grid = self.grid
        distance = grid.distance(self.source.get(context), self.target.get(context))
        if distance == 0:
            return [self.source.get(context)]
        cardinal_target = grid.get_line(self.source.get(context), self.target.get(context), 2)[1]
        target_x, target_y, target_z = grid.offsets_to_cube(cardinal_target.pos)
        source_x, source_y, source_z = grid.offsets_to_cube(self.source.get(context).pos)
        abs_target_x, abs_target_y, abs_target_z = grid.offsets_to_cube(self.target.get(context).pos)
        left_x, left_y, left_z = (source_x + source_y - target_y, source_y + source_z - target_z, source_z + source_x - target_x)
        right_x, right_y, right_z = (source_x + source_z - target_z, source_y + source_x - target_x, source_z + source_y - target_y)

        dist_to_left = max((abs(abs_target_x - left_x), abs(abs_target_y - left_y), abs(abs_target_z - left_z)))
        dist_to_right = max((abs(abs_target_x - right_x), abs(abs_target_y - right_y), abs(abs_target_z - right_z)))

        cell0 = [source_x, source_y, source_z]
        cell1 = [target_x, target_y, target_z]
        cell2 = [left_x, left_y, left_z]
        if dist_to_left > dist_to_right:
            cell2 = [right_x, right_y, right_z]

        delta1 = [b - a for a,b in zip(cell0, cell1)]
        delta2 = [b - a for a,b in zip(cell0, cell2)]
        delta_inner = [b - a for a,b in zip(cell1, cell2)]
        cells = [grid.cube_to_offsets(cell0)]
        for i in range(1, self.length + 1):
            cells.append(grid.cube_to_offsets(tuple(a + i * b for a,b in zip(cell0, delta1))))
            cells.append(grid.cube_to_offsets(tuple(a + i * b for a,b in zip(cell0, delta2))))
            for j in range(1, i):
                cells.append(grid.cube_to_offsets(tuple(a + i * b + j * c for a,b,c in zip(cell0, delta1, delta_inner))))

        result = []
        for cell in cells:
            col, row = cell
            width, height = grid.size
            if col < width and col >= 0 and row < height and row >= 0:
                result.append(grid[(col, row)])

        return result

class Cone60Enemy(Area):

    def __init__(self, source, target, length):
        self.source = source
        self.target = target
        self.length = length

    def _get(self,context):
        grid = self.grid
        distance = grid.distance(self.source.get(context), self.target.get(context))
        if distance == 0:
            return [self.source.get(context)]
        cardinal_target = grid.get_line(self.source.get(context), self.target.get(context), 2)[1]
        target_x, target_y, target_z = grid.offsets_to_cube(cardinal_target.pos)
        source_x, source_y, source_z = grid.offsets_to_cube(self.source.get(context).pos)
        abs_target_x, abs_target_y, abs_target_z = grid.offsets_to_cube(self.target.get(context).pos)
        left_x, left_y, left_z = (source_x + source_y - target_y, source_y + source_z - target_z, source_z + source_x - target_x)
        right_x, right_y, right_z = (source_x + source_z - target_z, source_y + source_x - target_x, source_z + source_y - target_y)

        dist_to_left = max((abs(abs_target_x - left_x), abs(abs_target_y - left_y), abs(abs_target_z - left_z)))
        dist_to_right = max((abs(abs_target_x - right_x), abs(abs_target_y - right_y), abs(abs_target_z - right_z)))

        cell0 = [source_x, source_y, source_z]
        cell1 = [target_x, target_y, target_z]
        cell2 = [left_x, left_y, left_z]
        if dist_to_left > dist_to_right:
            cell2 = [right_x, right_y, right_z]

        delta1 = [b - a for a,b in zip(cell0, cell1)]
        delta2 = [b - a for a,b in zip(cell0, cell2)]
        delta_inner = [b - a for a,b in zip(cell1, cell2)]
        cells = [grid.cube_to_offsets(cell0)]
        for i in range(1, self.length + 1):
            cells.append(grid.cube_to_offsets(tuple(a + i * b for a,b in zip(cell0, delta1))))
            cells.append(grid.cube_to_offsets(tuple(a + i * b for a,b in zip(cell0, delta2))))
            for j in range(1, i):
                cells.append(grid.cube_to_offsets(tuple(a + i * b + j * c for a,b,c in zip(cell0, delta1, delta_inner))))

        result = []
        for cell in cells:
            col, row = cell
            width, height = grid.size
            if col < width and col >= 0 and row < height and row >= 0:
                result.append(grid[(col, row)])

        shuffle(result)
        for cell in result:
            if cell.object and cell.object.stats.owner != context['owner'].stats.owner:
                return [cell]
        return []


def area_constructor(loader, node):
    a_s = loader.construct_mapping(node)
    name = a_s.pop("name")
    color = a_s.pop("widget", None)
    area = AREAS[name](**a_s)
    area.color = color
    return area

AREA_TAG = "!area"
