import operator as op

import numpy as np


def threat_signal(melee=None, ranged=None):
    # assert melee == 1
    # assert ranged == [1, 3]
    melee_power = melee or 0.0
    ranged_power, ranged_distance = ranged or [0.0, 1]
    print("SIGNAL")
    melee_power = float(melee_power)
    print(melee_power, ranged_power, ranged_distance)
    melee_signal = {
        0: melee_power,
        1: melee_power,
        2: 0.5*melee_power,
        3: 0.25*melee_power,
        4: 0.1*melee_power,
    }
    step = ranged_power/ranged_distance
    ranged_signal = {i: step*i for i in range(ranged_distance + 1)}
    ranged_signal[ranged_distance + 1] = ranged_power*0.5
    ranged_signal[ranged_distance + 2] = ranged_power*0.25
    ranged_signal[ranged_distance + 3] = ranged_power*0.1
    return {k: max(melee_signal.get(k, 0.0), ranged_signal[k]) for k in ranged_signal}


def compute_threat_map(grid, player, comp=op.eq):
    threat_map = np.zeros(grid.size, dtype='float64')
    for cell in grid:
        if cell.object and comp(cell.object.stats.owner, player):
            signal_desc = cell.object.signal
            for r, p in signal_desc.items():
                for r_cell in grid.get_ring(cell, r, r):
                    threat_map[r_cell.pos] += p
    return threat_map
