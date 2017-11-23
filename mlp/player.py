import blinker

from .replication_manager import GameObject
from .tools import dict_merge
from .unit import UnitsRegistry

death = blinker.signal("death")
game_over = blinker.signal("game_over")
summon = blinker.signal("summon")
revoke = blinker.signal("revoke")


class Player(GameObject):

    load_priority = -1

    def __init__(self, name=None, main_unit=None, id_=None):
        super().__init__(id_)
        self.name = name
        self.main_unit = main_unit
        self.units = []
        self.is_ready = False
        self.is_alive = True
        death.connect(self.on_death)
        summon.connect(self.on_summon)
        revoke.connect(self.on_revoke)

    def dump(self):
        return dict_merge(
            super().dump(),
            {
                'name': self.name,
                'main_unit': self.main_unit.dump(),
                'units': self.units,
            }
        )

    def load(self, struct):
        self.name = struct['name']
        self.main_unit = self.registry.load_obj(struct['main_unit'])
        self.units = struct['units']

    @classmethod
    def make_from_skel(cls, skel):
        return cls(
            name=skel['name'],
            main_unit=UnitsRegistry()[skel['unit']](skel['name'])
        )

    def on_death(self, _, unit):
        if unit is self.main_unit:
            self.is_alive = False

    def on_summon(self, _, unit, cell=None):
        if unit.stats.owner == self.name:
            self.units.append(unit)

    def on_revoke(self, _, unit, cell=None):
        if unit.stats.owner == self.name:
            self.units.remove(unit)
