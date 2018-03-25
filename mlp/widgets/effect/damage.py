from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.properties import NumericProperty

HEIGHT = 100


class Damage(Label):

    progress = NumericProperty(0.0)

    def __init__(self, amount, **kwargs):
        super().__init__(
            text='[color=ff3333]{}[/color]'.format(amount),
            markup=True,
            font_size='35',
            # size_hint=(None, None),
            **kwargs
        )
        self._pos = self.pos
        self.bind(progress=self.on_progress_update)

    def update(self, pos):
        x, y = pos
        self._pos = pos
        self.center = x, y + self.progress * HEIGHT

    def on_progress_update(self, _, progress):
        x, y = self._pos
        self.center = x, y + progress * HEIGHT

    def disappear(self, _):
        self.parent.remove_effect(self)
        # self.parent.remove_widget(self)

    def run(self):
        animation = Animation(progress=1.0, duration=3.0)
        animation.on_complete = self.disappear
        animation.start(self)
