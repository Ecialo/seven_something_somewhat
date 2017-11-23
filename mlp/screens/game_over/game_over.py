from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
import kivy.properties as prop

Builder.load_file('./mlp/screens/game_over/game_over.kv')


class GameOverScreen(Screen):

    app = prop.ObjectProperty()
    winner_name = prop.StringProperty()

    def __init__(self, app, winner_name=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.winner_name = winner_name or ""

    def receive(self, _):
        pass
