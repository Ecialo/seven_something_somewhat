from itertools import islice
from collections import deque

import numpy as np
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty
from kivy.animation import Animation
from kivy.lang import Builder


from ...tools import rsum
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

    def link(self, anchor):
        return Link(self, anchor)


class Link(Anchor):

    progress = NumericProperty(0.0)

    def __init__(self, from_anchor, to_anchor, **kwargs):
        super().__init__(**kwargs)
        self.from_anchor = from_anchor
        self.to_anchor = to_anchor
        self.v = None
        from_anchor.connect(self)
        to_anchor.connect(self)

    def __add__(self, other):
        if isinstance(other, Link):
            return Chain([self, other])
        elif isinstance(other, Chain):
            other.links.appendleft(self)
            return other
        else:
            raise TypeError("Not a Link or Chain")

    def update_pos(self, _):
        self.update_vector()
        point = tuple(np.array(self.from_anchor.pos) + self.v * self.progress)
        # print("FANCY POS")
        # print(point, (type(int(point[0])), type(int(point[1]))))
        self.pos = (float(point[0]), float(point[1]))

    def update_vector(self):
        self.v = np.array(self.to_anchor.pos) - np.array(self.from_anchor.pos)

    def make_run_along_animation(self):
        return MoveAnimation([self])


class Chain:

    def __init__(self, links):
        self.links = deque(links)

    def __add__(self, other):
        if isinstance(other, Link):
            self.links.append(other)
            return self
        elif isinstance(other, Chain):
            self.links += other.links
            return self

    def make_run_along_animation(self):
        return MoveAnimation(self.links)


class MoveAnimation:

    def __init__(self, path):
        # super().__init__(**kwargs)
        self.path = path

    def start(self, widget):
        anim_sequence = [
            Animation(progres=1.0) for _ in self.path
        ]
        anim_sequence[0].bind(on_start=self.on_start)
        anim_sequence[-1].bind(on_complete=self.on_complete)
        for i, anim in islice(enumerate(anim_sequence), 0, len(anim_sequence) - 1):
            anim.bind(on_complete=self.transfer_widget(i))
        long_animation = rsum(anim_sequence)
        long_animation.start(widget)

    def on_start(self, widget):
        widget.disconnect()
        self.path[0].connect(widget)

    def on_complete(self, widget):
        widget.disconnect()
        self.path[-1].to_anchor.connect(widget)

    def transfer_widget(self, part_i):

        def on_complete(widget):
            widget.disconnect()
            self.path[part_i + 1].connect(widget)

        return on_complete
