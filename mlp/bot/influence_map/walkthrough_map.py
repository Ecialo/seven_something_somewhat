import numpy as np


def compute_walkthrough_map(grid):
    result_map = np.ones(grid.size, dtype='float64')
    for cell in grid:
        if cell.object:
            result_map[cell.pos] = 0.0
    return result_map
