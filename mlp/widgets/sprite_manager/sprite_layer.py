import numpy as np
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty
from kivy.animation import Animation
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
        w.update_pos(self)

    def disconnect(self, w):
        self.connected.remove(w)

    def on_pos(self, inst, value):
        for con in self.connected:
            con.update_pos(self)


class Link(Anchor):

    progress = NumericProperty(0.0)

    def __init__(self, from_anchor, to_anchor, **kwargs):
        super().__init__(**kwargs)
        self.from_anchor = from_anchor
        self.to_anchor = to_anchor
        self.v = None
        from_anchor.connect(self)
        to_anchor.connect(self)

    def update_pos(self, _):
        self.update_vector()
        self.pos = np.array(self.from_anchor.pos) + self.v * self.progress

    def update_vector(self):
        self.v = np.array(self.to_anchor.pos) - np.array(self.from_anchor.pos)