from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty
from kivy.lang import Builder

Builder.load_file('./mlp/widgets/sprite_manager/sprite_layer.kv')


class SpriteLayer(RelativeLayout):

    scale = NumericProperty(1.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # def update_pos(self):
    #     for child in self.children:
    #         child.update_pos()

    def rescale(self, scale):
        for child in self.children:
            child.scale = scale * child.default_scale
        # self.update_pos()


class Anchor(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connected = []

    def connect(self, w):
        self.connected.append(w)
        w.center_x = self.center_x
        w.y = self.center_y

    def disconnect(self, w):
        self.connected.remove(w)

    def on_pos(self, inst, value):
        for con in self.connected:
            con.center_x = self.center_x
            con.y = self.center_y