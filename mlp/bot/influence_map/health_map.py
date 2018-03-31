import numpy as np


def compute_health_map(grid):
    health_map = np.zeros(grid.size, dtype='float64')
    # total_units = len(turn_order_manager)
    for cell in grid:
        obj = cell.object
        if obj:
            health_map[cell.pos] = obj.stats.health / obj.stats.max__health
    return health_map
