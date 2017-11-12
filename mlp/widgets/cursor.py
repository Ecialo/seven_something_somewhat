from kivy.uix import button
from kivy.event import EventDispatcher

from ..actions.property.area import FixedArea

class Cursor(EventDispatcher):

    def __init__(self, game_widget):
        self.game = game_widget
        # self.selected_cells = []

    def select(self, cell):
        pass

    def activate(self):
        pass

    def deactivate(self):
        pass

    def update(self):
        pass


class MainCursor(Cursor):

    def __init__(self, game_widget):
        super().__init__(game_widget)
        self.selected_cell = None

    def deactivate(self):
        try:
            self.selected_cell.is_selected = False
        except AttributeError:
            pass
        if self.game.stats:
            self.game.remove_widget(self.game.stats)
        if self.game.action_bar:
            self.game.remove_widget(self.game.action_bar)
        if self.game.current_action_bar:
            self.game.remove_widget(self.game.current_action_bar)

    def update(self):
        self.deactivate()
        self.activate()

    def activate(self):
        if self.selected_cell:
            self.selected_cell.is_selected = True
            selected_object = self.selected_cell.cell.object
            if selected_object:
                selected_object.make_widget().on_select(self.game)

    def select(self, cell):
        self.deactivate()
        self.selected_cell = cell
        self.activate()


class RequestCursor(Cursor):

    def __init__(self, game_widget, requester):
        super().__init__(game_widget)
        self.requester = requester
        self.send_button = button.Button(
            text="OK",
            pos_hint={'x': 0.8, "y": 0.2},
            size_hint=(None, None),
        )
        self.send_button.bind(on_press=self.send)
        self._context = {}

    @property
    def context(self):
        context = self.requester.action.context.copy()
        context.update(self._context)
        return context

    def activate(self):
        self.game.add_widget(self.send_button)

    def deactivate(self):
        self.game.remove_widget(self.send_button)

    def send(self, _):
        self.game.remove_cursor()


class MultiSelectCursor(RequestCursor):

    def __init__(self, game_widget, requester, max_cells):
        super().__init__(game_widget, requester)
        self.selected_cells = []
        self.max_cells = max_cells

    def select(self, cell):
        if len(self.selected_cells) < self.max_cells and cell not in self.selected_cells:
            cell.is_selected = True
            self.selected_cells.append(cell)
        elif cell in self.selected_cells:
            cell.is_selected = False
            self.selected_cells.remove(cell)

    def activate(self):
        super().activate()
        for cell in self.selected_cells:
            cell.is_selected = True

    def deactivate(self):
        super().deactivate()
        for cell in self.selected_cells:
            cell.is_selected = False

    def send(self, _):
        super().send(_)
        self.requester.select_result = [c.cell for c in self.selected_cells]
        # TODO по примеру в adjacent не отдавать ничего селектору при пустом выборе


class AdjacentSelectCursor(RequestCursor):

    def __init__(self, game_widget, requester, source_cell):
        super().__init__(game_widget, requester)
        self.available_cells = source_cell.get(self.context).adjacent
        self.selected_cell = None

    def select(self, cell):
        if cell.cell in self.available_cells:
            try:
                self.selected_cell.is_selected = False
            except AttributeError:
                pass
            cell.is_selected = True
            self.selected_cell = cell

    def activate(self):
        super().activate()
        if self.selected_cell:
            self.selected_cell.is_selected = True
        for cell in self.available_cells:
            cell.make_widget().is_highlighted = True

    def deactivate(self):
        super().deactivate()
        if self.selected_cell:
            self.selected_cell.is_selected = False
        for cell in self.available_cells:
            cell.make_widget().is_highlighted = False

    def send(self, _):
        super().send(_)
        try:
            self.requester.select_result = self.selected_cell.cell
        except AttributeError:
            pass


class LineSelectCursor(RequestCursor):

    def __init__(self, game_widget, requester, source_cell, length=None):
        super().__init__(game_widget, requester)
        self.source_cell = source_cell.get(self.context)
        self.selected_cells = []
        self.length = length
        print("LENGTH")
        print(self.length)

    def select(self, cell):
        self.deactivate()
        line_cells = cell.cell.grid.get_line(self.source_cell, cell.cell, self.length)
        self.selected_cells = [c.make_widget() for c in line_cells]
        self.activate()

    def activate(self):
        super().activate()
        for cell in self.selected_cells:
            cell.is_highlighted = True

    def deactivate(self):
        super().deactivate()
        for cell in self.selected_cells:
            cell.is_highlighted = False

    def send(self, _):
        super().send(_)
        self.requester.select_result = self.selected_cells[-1].cell
        # TODO Смотри multiselectcursor     
        
#
# class GeometryLastSelectCursor(RequestCursor):
#
#     def __init__(self, game_widget, requester, available_cells, shape):
#         super().__init__(game_widget, requester)
#         # self.context = requester.action.context
#         self.available_cells = available_cells
#         print("\n\n\n", available_cells)
#         self.shape = shape
#         self.selected_cells = []
#         # self.selected = None
#         self.highlighted_cells = None
#
#     def activate(self):
#         super().activate()
#         self.highlighted_cells = [c.make_widget() for c in self.available_cells.get(self.context)]
#         for cell in self.highlighted_cells:
#             cell.is_highlighted = True
#         for cell in self.selected_cells:
#             cell.is_selected = True
#
#     def deactivate(self):
#         super().deactivate()
#         for cell in self.highlighted_cells:
#             cell.is_highlighted = False
#         for cell in self.selected_cells:
#             cell.is_selected = False
#
#     def select(self, cell):
#         self.deactivate()
#         self._context['selected'] = cell.cell
#         self.selected_cells = [c.make_widget() for c in self.shape.get(self.context)]
#         self.activate()
#
#     def send(self, _):
#         super().send(_)
#         # self.requester.select_result = [c.cell for c in self.selected_cells]
#         self.requester.select_result = self.selected_cells[-1].cell
        
        
class GeometrySelectCursor(RequestCursor):

    def __init__(self, game_widget, requester, available_cells, shape):
        super().__init__(game_widget, requester)
        self.available_cells = available_cells
        self.shape = shape
        self.selected_cells = FixedArea()
        self.highlighted_cells = FixedArea()

    def activate(self):
        super().activate()
        # self.highlighted_cells = [c.make_widget() for c in self.available_cells.get(self.context)]
        self.highlighted_cells = self.available_cells.get(self.context)
        self.highlighted_cells.highlight()
        self.selected_cells.select()

    def deactivate(self):
        super().deactivate()
        self.highlighted_cells.playdown()
        # for cell in self.highlighted_cells:
        #     cell.is_highlighted = False
        self.selected_cells.unselect()
        # for cell in self.selected_cells:
        #     cell.is_selected = False

    def select(self, cell):
        # print(cell)
        if cell.cell in self.highlighted_cells:
            # print(cell)
            self.deactivate()
            self._context['selected'] = cell.cell
            # self.selected_cells = [c.make_widget() for c in self.shape.get(self.context)]
            self.selected_cells = self.shape.get(self.context)
            self.activate()

    def send(self, _):
        super().send(_)
        # self.requester.select_result = [c.cell for c in self.selected_cells]
        self.requester.select_result = self._context['selected']


class GeometryLastSelectCursor(GeometrySelectCursor):

    def send(self, _):
        super().send(_)
        self.requester.select_result = self.selected_cells[-1].cell

CURSOR_TABLE = {
    'any_cell': MultiSelectCursor,
    'adjacent_cell': AdjacentSelectCursor,
    'line': LineSelectCursor,
    'geometry': GeometrySelectCursor,
    'geometry_last': GeometryLastSelectCursor,
}
