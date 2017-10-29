from .replication_manager import GameObject
from .tools import dict_merge
from .unit import UnitsRegistry


class Player(GameObject):

    load_priority = -1

    def __init__(self, name=None, main_unit=None, id_=None):
        super().__init__(id_)
        self.name = name
        self.main_unit = main_unit
        self.is_ready = False
        # self.units = []

    def dump(self):
        # return {
        #     **super().dump(),
        #     'name': self.name,
        #     # 'main_unit': RefTag(self.main_unit),
        #     'main_unit': self.main_unit.dump(),
        #     # 'units': [RefTag(unit) for unit in self.units]
        # }
        return dict_merge(
            super().dump(),
            {
                'name': self.name,
                'main_unit': self.main_unit.dump(),
            }
        )

    def load(self, struct):
        self.name = struct['name']
        self.main_unit = self.registry.load_obj(struct['main_unit'])
        # self.units = struct['units']

    @classmethod
    def make_from_skel(cls, skel):
        return cls(
            name=skel['name'],
            main_unit=UnitsRegistry()[skel['unit']](skel['name'])
        )
