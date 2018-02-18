import numpy as np


def compute_ap_map(grid):
    ap_map = np.zeros(grid.size, dtype='float64')
    # total_units = len(turn_order_manager)
    for cell in grid:
        obj = cell.object
        if obj:
            ap_map[cell.pos] = obj.stats.action_points / obj.stats.max__action_points
    return ap_map
