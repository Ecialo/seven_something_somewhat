from ..replication_manager import MetaRegistry

EFFECTS = MetaRegistry()['Command']
CommandMeta = MetaRegistry().make_registered_metaclass("Command")


class Command(metaclass=CommandMeta):

    name = ""

    def execute(self):
        pass

    def dump(self):
        pass


class Place(Command):

    name = "place"

    def __init__(self, unit=None, place=None, old_place=None):
        self.unit = unit
        self.place = place
        self.old_place = old_place

    def execute(self):
        unit = self.unit
        uw = unit.make_widget(pos_hint={'center_x': 0.5, 'y': 0.3})
        # print("\nUNIT {} \n PLACE{} \nOLD PLACE{}\n".format(self.unit, self.place, self.old_place))
        if self.old_place:
            self.old_place.make_widget().remove_widget(uw)
        self.place.make_widget().add_widget(uw)

    def dump(self):
        return {
            "name": self.name,
            "unit": self.unit,
            "old_place": self.old_place,
            "place": self.place,
        }


class Revoke(Command):

    name = "revoke"

    def __init__(self, unit, cell):
        self.unit = unit
        self.cell = cell

    def execute(self):
        self.cell.make_widget().remove_widget(self.unit.make_widget())

    def dump(self):
        return {
            "name": self.name,
            "unit": self.unit,
            "cell": self.cell,
        }
