# -*- coding: utf-8 -*-
from math import cos, sin, pi, sqrt, degrees, radians

import numpy as np
from numpy import matlib as mtl
from kivy.lang import Builder
import kivy.uix.widget as widget
from kivy.uix import (
    relativelayout,
    label,
)
from kivy.properties import (
    ListProperty,
    NumericProperty,
    BooleanProperty,
)
from kivy.uix.image import Image

from ..sprite_manager.sprite_layer import (
    SpriteLayer,
    Anchor
)

__author__ = 'ecialo'
H_COEF = sqrt(3)/2
R2 = radians(60)

Builder.load_file('./mlp/widgets/grid/gridwidget.kv')


def in_polygon(x, y, xp, yp):
    c = 0
    for i in range(len(xp)):
        if (((yp[i] <= y < yp[i-1]) or (yp[i-1] <= y < yp[i])) and
           (x > (xp[i-1] - xp[i]) * (y - yp[i]) / (yp[i-1] - yp[i]) + xp[i])):
                c = 1 - c
    return bool(c)


class HexCellWidget(relativelayout.FloatLayout):

    default_select_color = [1.0, 0, 0]
    mesh_vertices = ListProperty([])
    circuit = ListProperty([])
    is_selected = BooleanProperty(False)
    is_highlighted = BooleanProperty(False)
    rotator = mtl.eye(3)
    select_color = ListProperty([1.0, 0, 0])

    def __init__(self, cell, **kwargs):
        self.cell = cell
        hex_size = kwargs.pop('hex_size')
        super(HexCellWidget, self).__init__(
            size=(hex_size*2, hex_size*2),
            **kwargs
        )
        self.anchor = Anchor()
        self.add_widget(self.anchor)

    @property
    def hex_size(self):
        return self.parent.cell_size

    def update_vertices(self):
        vertices = []
        points = []
        step = 6
        istep = (pi * 2) / float(step)
        offset = pi/6
        xs = []
        ys = []
        for i in range(step):
            x = cos(istep * i + offset) * self.hex_size + self.hex_size
            y = sin(istep * i + offset) * self.hex_size + self.hex_size*H_COEF

            c = np.matrix([[x], [y], [0]])
            m = (self.rotator * c)
            nx, ny = m[0, 0], m[1, 0]
            x, y = nx, ny

            vertices.extend([x, y, 0.5 + cos(istep * i)/2, 0.5 + sin(istep * i)/2])
            points.extend([x, y])
            xs.append(x)
            ys.append(y)

        self.circuit = points + points[0:2]
        self.mesh_vertices = vertices
        self.size = (int(max(xs) - min(xs)), int(max(ys) - min(ys)))
        # for child in self.children:
        #     if isinstance(child, Unit):
        #         child.scale = self.parent.scale * child.default_scale

    @property
    def cell_pos(self):
        return self.cell.pos

    def on_touch_down(self, touch):
        ret = False
        touch.push()
        touch.apply_transform_2d(self.to_local)
        if self.collide_point(*touch.pos):
            self.parent.select_cell(self)
            ret = True
        touch.pop()
        return ret

    def collide_point(self, x, y):
        xs = self.mesh_vertices[::4]
        ys = self.mesh_vertices[1::4]
        return in_polygon(x, y, xs, ys)

    def to_local(self, x, y, relative=True):
        return super().to_local(x, y, relative)


class Hexgrid(widget.Widget):

    cell_indices = range(6)
    cell_size = NumericProperty(110)
    base_cell_size = 110
    rotation = NumericProperty(0)
    rotator = mtl.eye(3)
    scale = NumericProperty(1.0)

    def __init__(self, grid, **kwargs):
        hexgrid = grid
        self.grid = grid
        self.hexgrid = hexgrid
        w, h = len(hexgrid._grid), len(hexgrid._grid[0])
        self._grid = [
            [None for _ in range(h)] for _ in range(w)]
        super(Hexgrid, self).__init__(
            **kwargs
        )

        self.make_cells()
        self.bind(rotation=self.change_rotator)
        self.bind(cell_size=self.update_children)
        self.bind(scale=self.rescale)

        self.update_size()

    def make_cells(self):
        for cell in reversed(list(self.grid)):
            pos = cell.pos
            # terrain = cell.terrain
            x, y = pos
            w = cell.make_widget(
                hex_size=self.cell_size,
                pos=self.grid_to_window(pos)
            )
            self._grid[x][y] = w
            self.add_widget(w)
            w.add_widget(label.Label(text=str(pos), pos_hint={'center_x': 0.5, 'center_y': 0.5}))
        self.update_children()

    def change_rotator(self, _, value):
        rad = radians(value)
        self.rotator = np.matrix([
            [1.0, 0.0, 0.0],
            [0.0, cos(rad), sin(rad)],
            [0.0, -sin(rad), cos(rad)]
        ])
        for child in self.children:
            if isinstance(child, HexCellWidget):
                child.rotator = self.rotator
        self.update_children()

    def update_size(self):
        xs = []
        ys = []
        self.rotation = 56
        for child in self.children:
            xs.append(child.x)
            ys.append(child.y)
        width, height = self._grid[0][0].size
        self.size = (int(max(xs) - min(xs)) + width, int(max(ys) - min(ys)) + height)

    def on_pos(self, inst, value):
        self.update_children()

    def rescale(self, _, scale):
        self.cell_size = self.base_cell_size*scale
        self.update_size()

    def update_children(self, _=None, __=None):
        for child in self.children:
            if isinstance(child, HexCellWidget):
                child.pos = self.grid_to_window(child.cell_pos)
                child.update_vertices()

    def grid_to_window(self, pos):
        sx, sy = self.pos
        size = self.cell_size
        col, row = pos

        # x = size * 3 / 2 * col
        # y = size * sqrt(3) * (row - 0.5 * (col & 1))

        x = size * sqrt(3) * (col + 0.5 * (row & 1))
        y = size * 3 / 2 * row

        x, y = sx+x, sy+y
        c = np.matrix([[x], [y], [0]])
        m = (self.rotator * c)
        nx, ny = m[0, 0], m[1, 0]
        x, y = float(nx), float(ny)
        return x, y

    def select_cell(self, cell):
        self.parent.cursor.select(cell)


class FullImage(Image):
    pass


class CompositeArena(relativelayout.RelativeLayout):

    def __init__(self, gridwidget, **kwargs):
        super().__init__(**kwargs)
        self.gridwidget = gridwidget
        self.sprite_layer = SpriteLayer()
        self.add_widget(gridwidget)
        self.add_widget(self.sprite_layer)
        self.bind(scale=self.rescale)
        # for child in self.ids.sprite_layer.children:
            # child.scale = scale * child.default_scale
            # child.update_pos()

    def rescale(self, _, scale):
        self.sprite_layer.rescale(scale)
        self.gridwidget.scale = scale
            # child.update_pos()

    # def on_pos(self, inst, value):
    #     for child in self.ids.sprite_layer.children:
    #         child.scale = scale * child.default_scale
            # child.update_pos()


    @property
    def cursor(self):
        return self.parent.parent.cursor


