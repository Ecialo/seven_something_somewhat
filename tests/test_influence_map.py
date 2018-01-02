import blinker

from ..mlp.grid import HexGrid
from ..mlp.replication_manager import MetaRegistry
from ..mlp.loader import load
from ..mlp.bot.influence_map.position_map import (
    compute_position_map,
)
from ..mlp.bot.influence_map.threat_map import threat_signal

summon = blinker.signal("summon")
revoke = blinker.signal("revoke")

load()

ACTIONS = MetaRegistry()["Action"]
UNITS = MetaRegistry()["Unit"]


class TestSearchInAOE:

    grid = HexGrid((5, 5))

    def setUp(self):
        self.units = []
        summon.connect(self.track_units)

    def tearDown(self):
        summon.disconnect(self.track_units)
        for unit in self.units:
            revoke.send(unit=unit, cell=unit.cell)

    def track_units(self, _, unit, cell):
        self.units.append(unit)

    def test_position_single_unit(self):
        unit_A = UNITS['Dummy']("A")
        unit_A.switch_state()
        summon.send(None, unit=unit_A, cell=self.grid[(2, 2)])
        for unit in self.units:
            unit.clear_presumed()
            unit.update_position()

        pos_map = compute_position_map(self.grid, "A")
        assert pos_map[2, 2] == 1.0

        assert pos_map[2, 3] == 0.5
        assert pos_map[1, 3] == 0.5
        assert pos_map[1, 2] == 0.5
        assert pos_map[2, 1] == 0.5
        assert pos_map[3, 2] == 0.5
        assert pos_map[3, 3] == 0.5

        assert pos_map[2, 4] == 0.25
        assert pos_map[3, 4] == 0.25
        assert pos_map[1, 4] == 0.25

        assert pos_map[0, 3] == 0.25
        assert pos_map[0, 2] == 0.25
        assert pos_map[0, 1] == 0.25

        assert pos_map[1, 1] == 0.25
        assert pos_map[2, 0] == 0.25
        assert pos_map[3, 1] == 0.25

        assert pos_map[4, 3] == 0.25
        assert pos_map[4, 2] == 0.25
        assert pos_map[4, 1] == 0.25

    def test_position_single_corner_unit(self):
        unit_A = UNITS['Dummy']("A")
        unit_A.switch_state()
        summon.send(None, unit=unit_A, cell=self.grid[(4, 0)])
        for unit in self.units:
            unit.clear_presumed()
            unit.update_position()

        pos_map = compute_position_map(self.grid, "A")
        assert pos_map[4, 0] == 1.0

        assert pos_map[4, 1] == 0.5
        assert pos_map[3, 1] == 0.5
        assert pos_map[3, 0] == 0.5

        assert pos_map[4, 2] == 0.25
        assert pos_map[3, 2] == 0.25
        assert pos_map[2, 1] == 0.25
        assert pos_map[2, 0] == 0.25

    def test_threat_signal(self):
        # signal = UNITS['Dummy'].signal
        signal = threat_signal(**{'melee': 1, "ranged":[1, 3]})
        # melee 1, ranged 1, 3
        test_signal = {
            0: 1.0,
            1: 1.0,
            2: 0.66666,
            3: 0.99999,
            4: 0.5,
        }
        # print(signal)
        # print([abs(signal[r] - test_signal[r]) for r in test_signal])
        assert all(
            [abs(signal[r] - test_signal[r]) < 0.001 for r in test_signal]
        )

    def test_unit_threat_signal(self):
        signal = UNITS['Dummy']("A").signal
        # melee 1, ranged 1, 3
        test_signal = {
            0: 1.0,
            1: 1.0,
            2: 0.66666,
            3: 0.99999,
            4: 0.5,
        }
        # print(signal)
        # print([abs(signal[r] - test_signal[r]) for r in test_signal])
        assert all(
            [abs(signal[r] - test_signal[r]) < 0.001 for r in test_signal]
        )