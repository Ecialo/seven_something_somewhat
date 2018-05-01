from unittest import skip

import blinker
import numpy as np

from ..mlp.grid import HexGrid
from ..mlp.replication_manager import MetaRegistry
from ..mlp.loader import load
from ..mlp.bot.tactic.flee import Flee

load()

UNITS = MetaRegistry()["Unit"]

summon = blinker.signal('summon')
revoke = blinker.signal('revoke')
collect_garbage = blinker.signal('collect')


class TestTactic:

    grid = HexGrid((5, 5))

    def setUp(self):
        self.units = []
        summon.connect(self.track_units)

    def tearDown(self):
        summon.disconnect(self.track_units)
        for unit in self.units:
            unit.kill()
            # revoke.send(unit=unit, cell=unit.cell)
        collect_garbage.send()

    def track_units(self, _, unit, cell):
        self.units.append(unit)

    @skip
    def test_units_in_tactic(self):
        units_l = len(Flee().units)
        # print(Flee().units)
        assert units_l == 0

    def test_flee_tactic(self):
        unit_A = UNITS['Dummy']("A")
        unit_A.switch_state()
        summon.send(None, unit=unit_A, cell=self.grid[(0, 0)])

        for unit in self.units:
            unit.clear_presumed()
            unit.update_position()

        threat_map = np.ones((5, 5), dtype='float64')
        threat_map[0, 2] = 0.5
        threat_map[1, 2] = 0.7

        tactic = Flee()
        actions = tactic.realize(unit_A, threat_map)

        for action in actions:
            action.apply()

        for unit in self.units:
            unit.clear_presumed()
            unit.update_position()

        assert self.grid[0, 2].object == unit_A
