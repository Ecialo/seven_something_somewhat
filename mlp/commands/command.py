from ..replication_manager import MetaRegistry
from ..grid import Grid
from ..tools import rsum

EFFECTS = MetaRegistry()['Command']
CommandMeta = MetaRegistry().make_registered_metaclass("Command")


def save_pop(deque):
    try:
        return deque.popleft()
    except IndexError:
        return None


class Command(metaclass=CommandMeta):

    name = ""

    def execute(self, rest_commands):
        pass

    def _execute(self):
        pass

    def dump(self):
        pass


class Place(Command):

    name = "place"

    def __init__(self, unit=None, place=None, old_place=None):
        self.unit = unit
        self.place = place
        self.old_place = old_place

    def execute(self, rest_commands):
        self._execute()
        c = save_pop(rest_commands)
        if c:
            c.execute(rest_commands)

    def _execute(self):
        grid_w = Grid.locate().make_widget()
        s_l = grid_w.parent.sprite_layer
        unit = self.unit
        uw = unit.make_widget()
        cw = self.place.make_widget().anchor
        uw.connect(cw)
        if not self.old_place:
            s_l.add_widget(uw)

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

    def execute(self, rest_commands):
        self._execute()
        c = save_pop(rest_commands)
        if c:
            c.execute(rest_commands)

    def _execute(self):
        self.cell.make_widget().remove_widget(self.unit.make_widget())

    def dump(self):
        return {
            "name": self.name,
            "unit": self.unit,
            "cell": self.cell,
        }


class Move(Command):

    name = "move"

    def __init__(self, unit=None, path=None):
        self.unit = unit
        self.path = path
        self._rest_commands = None

    def execute(self, rest_commands):
        self._rest_commands = rest_commands
        self._execute()

    def _execute(self):
        anchors = [cell.make_widget().anchor for cell in self.path]
        animation = rsum(
            (from_anchor.link(to_anchor) for from_anchor, to_anchor in zip(anchors, anchors[1::]))
        ).make_run_along_animation(callback=self.execute_next)
        uw = self.unit.make_widget()
        animation.start(uw)

    def execute_next(self):
        c = save_pop(self._rest_commands)
        if c:
            c.execute(self._rest_commands)

    def dump(self):
        return {
            "name": self.name,
            "unit": self.unit,
            "path": self.path,
        }
