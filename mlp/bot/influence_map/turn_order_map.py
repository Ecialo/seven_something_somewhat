import numpy as np


def compute_turn_order_map(grid, turn_order_manager):
    turn_order_map = np.zeros(grid.size, dtype='float64')
    total_units = len(turn_order_manager)
    for cell in grid:
        obj = cell.object
        if obj:
            turn_order_map[cell.pos] = turn_order_manager[obj]/total_units
    return turn_order_map
