from ..mlp.grid import HexGrid


class TestGrid:

    def setUp(self):
        self.grid = HexGrid((9, 9))

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
        assert cells == {grid[0, 4], grid[3, 3], grid[1, 4]}

    def test_left_bottom_area(self):
        grid = self.grid
        cells = grid.get_area((0, 0), 1)
        assert cells == {grid[0, 1], grid[1, 1], grid[1, 0], grid[0, 0  ]}