import operator as op

import numpy as np


def compute_position_map(grid, player, comp=op.eq):
    position_map = np.zeros(grid.size, dtype='float64')
    for cell in grid:
        if cell.object and comp(cell.object.stats.owner, player):
            position_map[cell.pos] += 1.0
            for r_cell in grid.get_ring(cell, 1, 1):
                position_map[r_cell.pos] += 0.5
            for r_cell in grid.get_ring(cell, 2, 2):
                position_map[r_cell.pos] += 0.25
    return position_map

