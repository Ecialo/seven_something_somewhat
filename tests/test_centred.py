import numpy as np

from ..mlp.tools import centred


class TestCentred:

    def setUp(self):
        # 6x6
        self.layout = np.array([
            [1, 7, 13, 19, 25, 31],
            [2, 8, 14, 20, 26, 32],
            [3, 9, 15, 21, 27, 33],
            [4, 10, 16, 22, 28, 34],
            [5, 11, 17, 23, 29, 35],
            [6, 12, 18, 24, 30, 36],
        ], dtype='float64')

    def test_orientation(self):
        assert self.layout[1, 0] == 2
        assert self.layout[2, 3] == 21

    def test_center(self):
        l = self.layout
        view = centred((3, 3), l, 1)
        assert (view == np.array([
            [l[2, 2], l[2, 3], l[2, 4]],
            [l[3, 2], l[3, 3], l[3, 4]],
            [l[4, 2], l[4, 3], l[4, 4]],
        ], dtype='float64')).all()

    def test_left_side(self):
        l = self.layout
        view = centred((0, 3), l, 1)
        assert (view == np.array([
            [0, l[2, 0], l[2, 1]],
            [0, l[3, 0], l[3, 1]],
            [0, l[4, 0], l[4, 1]],
        ], dtype='float64')).all()

    def test_right_side(self):
        l = self.layout
        view = centred((5, 3), l, 1)
        assert (view == np.array([
            [l[2, 4], l[2, 5], 0],
            [l[3, 4], l[3, 5], 0],
            [l[4, 4], l[4, 5], 0],
        ], dtype='float64')).all()

    def test_top(self):
        l = self.layout
        view = centred((3, 0), l, 1)
        assert (view == np.array([
            [0, 0, 0],
            [l[0, 2], l[0, 3], l[0, 4]],
            [l[1, 2], l[1, 3], l[1, 4]],
        ], dtype='float64')).all()

    def test_bottom(self):
        l = self.layout
        view = centred((3, 5), l, 1)
        assert (view == np.array([
            [l[4, 2], l[4, 3], l[4, 4]],
            [l[5, 2], l[5, 3], l[5, 4]],
            [0, 0, 0],
        ], dtype='float64')).all()

    def test_top_left(self):
        l = self.layout
        view = centred((0, 0), l, 1)
        assert (view == np.array([
            [0, 0, 0],
            [0, l[0, 0], l[0, 1]],
            [0, l[1, 0], l[1, 1]],
        ], dtype='float64')).all()

    def test_bottom_right(self):
        l = self.layout
        view = centred((5, 5), l, 1)
        assert (view == np.array([
            [l[4, 4], l[4, 5], 0],
            [l[5, 4], l[5, 5], 0],
            [0, 0, 0],
        ], dtype='float64')).all()