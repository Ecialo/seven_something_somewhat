import io

import yaml

from ..mlp.loader import load
from ..mlp.grid import (
    HexGrid,
    HexCell,
)

load()


class TestGrid:

    def setUp(self):
        self.grid = HexGrid((5, 5))

    def test_get(self):
        grid = self.grid
        assert grid[0, 0] == grid._grid[0][0]

    def test_center_area(self):
        grid = self.grid
        cells = grid.get_area((2, 2), 1)
        assert cells == {
            grid[1, 3], grid[2, 3], grid[3, 3],
            grid[1, 2], grid[2, 1], grid[3, 2],
            grid[2, 2]
        }

    def test_left_top_area(self):
        grid = self.grid
        cells = grid.get_area((0, 4), 1)
        assert cells == {grid[0, 4], grid[0, 3], grid[1, 4]}

    def test_left_bottom_area(self):
        grid = self.grid
        cells = grid.get_area((0, 0), 1)
        assert cells == {grid[0, 1], grid[1, 1], grid[1, 0], grid[0, 0]}

    def test_right_bottom_area(self):
        grid = self.grid
        cells = grid.get_area((4, 0), 1)
        assert cells == {grid[3, 0], grid[4, 0], grid[3, 1], grid[4, 1]}

    def test_right_top_area(self):
        grid = self.grid
        cells = grid.get_area((4, 4), 1)
        assert cells == {grid[3, 4], grid[4, 3], grid[4, 4]}

    def test_cell_load(self):
        cell = yaml.load(io.StringIO("!cell [0, 0]"))
        assert cell == self.grid[0, 0]

    def test_cell_type(self):
        cell = yaml.load(io.StringIO("!cell [0, 0]"))
        assert isinstance(cell, HexCell)

    def test_ring_r0(self):
        grid = self.grid
        cells = grid.get_ring((2, 2), 0, 0)
        assert cells == {grid[2, 2]}

    def test_ring_r1(self):
        grid = self.grid
        cells = grid.get_ring((2, 2), 1, 1)
        assert cells == {
            grid[2, 3],
            grid[1, 3],
            grid[1, 2],
            grid[2, 1],
            grid[3, 2],
            grid[3, 3],
        }

    def test_ring_r2(self):
        grid = self.grid
        cells = grid.get_ring((2, 2), 2, 2)
        assert cells == {
            grid[2, 4],
            grid[3, 4],
            grid[1, 4],

            grid[0, 3],
            grid[0, 2],
            grid[0, 1],

            grid[1, 1],
            grid[2, 0],
            grid[3, 1],

            grid[4, 3],
            grid[4, 2],
            grid[4, 1],
        }
