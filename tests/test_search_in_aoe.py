import blinker

from ..mlp.grid import HexGrid
from ..mlp.replication_manager import MetaRegistry
from ..mlp.loader import load
from ..mlp.bot.tactic.approach_and_attack import (
    find_success,
    unit_in_area,
)

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

    def test_find_victim(self):
        unit_A = UNITS['Dummy']("A")
        unit_A.switch_state()
        summon.send(None, unit=unit_A, cell=self.grid[(2, 2)])

        unit_B = UNITS['Dummy']("B")
        unit_B.switch_state()
        summon.send(None, unit=unit_B, cell=self.grid[(1, 3)])

        for unit in self.units:
            unit.clear_presumed()
            unit.update_position()

        action = ACTIONS['Kick'](unit_A)
        extractor = unit_in_area(unit_B)
        params = action.search_in_aoe(find_success, extractor)
        print("FINDED PARAMS", params)
        action.instant_setup(**params)
        action.apply()
        assert unit_B.stats.health == 93
