from ..general.camera.camera import FullImage
from kivy.properties import NumericProperty


class Unit(FullImage):

    # default_scale = 0.33
    scale = NumericProperty(0.33)

    def __init__(self, unit, **kwargs):
        self.unit = unit
        super().__init__(source=unit.widget['sprite'], **kwargs)
        self.default_scale = unit.widget.get('scale', 1.0)
        self.scale = self.default_scale

    def on_select(self, game_widget):
        game_widget.stats = self.unit._stats.make_widget(pos_hint={'x': 0.0, 'y': 0.5})
        game_widget.add_widget(game_widget.stats)
        if game_widget.parent.username == self.unit.stats.owner or game_widget.parent.username == 'overlord':
            game_widget.action_bar = self.unit.stats.action_bar.make_widget(
                pos_hint={'x': 0.0, 'bottom': 0.0},
            )
            game_widget.current_action_bar = self.unit.current_action_bar.make_widget(
                pos_hint={'x': 0.0, 'y': 0.1}
            )
            game_widget.add_widget(game_widget.action_bar)
            game_widget.add_widget(game_widget.current_action_bar)

    # def update_pos(self):
    #     cw = self.unit.real_cell.make_widget().ids.anchor
    #     self.y = cw.center_y
    #     self.center_x = cw.center_x