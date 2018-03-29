import blinker

from ..mlp.grid import HexGrid
from ..mlp.replication_manager import MetaRegistry
from ..mlp.loader import load

load()

UNITS = MetaRegistry()["Unit"]

summon = blinker.signal('summon')
revoke = blinker.signal('revoke')


class TestBehavior:

    grid = HexGrid((5, 5))

    def setUp(self):
        self.units = []
        summon.connect(self.track_units)

    def tearDown(self):
        summon.disconnect(self.track_units)
        for unit in self.units:
            revoke.send(unit=unit, cell=unit.cell)

    def track_units(self, _, unit, cell):
        # print(unit)
        self.units.append(unit)

    def test_behavior(self):
        unit_A = UNITS['Dog']("A")
        # print(unit_A.behavior)
        unit_A.switch_state()
        unit_B = UNITS['Dog']("B")
        unit_B.switch_state()
        summon.send(None, unit=unit_A, cell=self.grid[(0, 0)])
        summon.send(None, unit=unit_B, cell=self.grid[(1, 1)])
        #
        for unit in self.units:
            unit.clear_presumed()
            unit.update_position()

        actions = unit_A.behave()
        print(actions)
        assert False
