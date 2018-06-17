from itertools import islice
from collections import deque

import numpy as np
import blinker
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty,
    # ObjectProperty,
)
from kivy.animation import Animation
from kivy.lang import Builder
from kivy.graphics import (
    Line,
    Rectangle,
    Color,
)

Builder.load_file('./mlp/widgets/sprite_manager/sprite_layer.kv')

MOVE_DURATION = 0.5

rearrange = blinker.signal('rearrange')


class SpriteLayer(RelativeLayout):

    scale = NumericProperty(1.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        rearrange.connect(self.rearrange)

    def rescale(self, scale):
        for child in self.children:
            child.scale = scale * child.default_scale

    def rearrange(self, _):
        children = [child for child in self.children]
        children.sort(key=lambda ch: ch.unit.cell.pos[1], reverse=True)
        self.clear_widgets()
        for ch in children:
            self.add_widget(ch)


class Anchor(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connected = []

    def __repr__(self):
        return "Anchor at {}".format(self.pos)

    def connect(self, w):
        self.connected.append(w)
        w.update_pos(self)

    def disconnect(self, w):
        self.connected.remove(w)
        print(self, self.connected)

    def on_pos(self, inst, value):
        for con in self.connected:
            con.update_pos(self)

    def link(self, anchor):
        return Link(self, anchor)


class Link(Anchor):

    progress = NumericProperty(0.0)
    # from_anchor = ObjectProperty()
    # to_anchor = ObjectProperty()

    def __init__(self, from_anchor, to_anchor, **kwargs):
        self.from_anchor = from_anchor
        self.to_anchor = to_anchor
        super().__init__(**kwargs)
        self.v = None
        from_anchor.connect(self)
        to_anchor.connect(self)
        self.bind(progress=self.on_progress)
        with self.canvas:
            Color(rgba=(0.0, 1.0, 0.0, 1.0))
            self.point = Rectangle(pos=self.pos, size=(15, 15))
            self.link = Line(points=[*self.from_anchor.center, *self.to_anchor.center], width=1)
        self.bind(pos=self.redraw)
        # self.bind(pos=self.pos_printer)

    def __add__(self, other):
        if isinstance(other, Link):
            return Chain([self, other])
        elif isinstance(other, Chain):
            other.links.appendleft(self)
            return other
        else:
            raise TypeError("Not a Link or Chain")

    def __repr__(self):
        return "Link from {} to {}".format(self.from_anchor, self.to_anchor)

    def update_pos(self, _):
        self.update_vector()
        point = tuple(np.array(self.from_anchor.center) + self.v * self.progress)
        # print(point)
        # print("FANCY POS")
        # print(point, (type(int(point[0])), type(int(point[1]))))
        self.pos = (float(point[0]), float(point[1]))
        # self.redraw()

    def update_vector(self):
        self.v = np.array(self.to_anchor.center) - np.array(self.from_anchor.center)

    def make_run_along_animation(self, callback):
        return MoveAnimation([self], callback)

    def on_progress(self, inst, value):
        inst.update_pos(None)

    def redraw(self, *args):
        # print(self.pos, self.from_anchor.center, self.to_anchor.center)
        point = tuple(np.array(self.from_anchor.center) + self.v)
        self.point.pos = self.pos
        # self.link.points = [*self.from_anchor.center, *self.to_anchor.center]
        self.link.points = [*self.from_anchor.center, *point]

    def pos_printer(self, inst, value):
        print(inst, value)


class Chain:

    def __init__(self, links):
        self.links = deque(links)

    # def __repr__(self):
    #     return ""

    def __add__(self, other):
        if isinstance(other, Link):
            self.links.append(other)
            return self
        elif isinstance(other, Chain):
            self.links += other.links
            return self

    def make_run_along_animation(self, callback):
        return MoveAnimation(self.links, callback)


class MoveAnimation:

    def __init__(self, path, callback):
        # super().__init__(**kwargs)
        self.path = path
        self._animations = None
        self._widget = None
        self._callback = callback

    def start(self, widget):
        print("PATH")
        self._widget = widget
        anim_sequence = [
            Animation(progress=1.0, duration=MOVE_DURATION) for _ in self.path
        ]
        print(anim_sequence)
        anim_sequence[0].bind(on_start=self.on_start)
        anim_sequence[-1].on_complete = self.on_complete
        print(anim_sequence[0] is anim_sequence[-1])
        for i, anim in islice(enumerate(anim_sequence), 0, len(anim_sequence) - 1):
            print("OHOHO")
            anim.on_complete = self.transfer_widget(i)
        self._animations = anim_sequence
        self._animations[0].start(self.path[0])

    def on_start(self, _, __=None):
        print("Connect to link")
        widget = self._widget
        widget.disconnect()
        widget.connect(self.path[0])
        # self.path[0].from_anchor.parent.parent.parent.sprite_layer.add_widget(self.path[0])

    def on_complete(self, _):
        print("Connect to endpoint")
        widget = self._widget
        widget.disconnect()
        widget.connect(self.path[-1].to_anchor)
        rearrange.send()
        self._callback()

    def monitor_progress(self, inst, progress):
        print(progress)

    def transfer_widget(self, part_i):

        def on_complete(_, __=None):
            print("COMPLETE")
            self._widget.disconnect()
            self._widget.connect(self.path[part_i + 1])
            self._animations[part_i + 1].start(self.path[part_i + 1])

        return on_complete
