from collections import defaultdict

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
import kivy.properties as prop
import blinker

from ...protocol import (
    message_type as mt,
    game_message as gm,
    lobby_message as lm,
    context_message as cm,
)
from ...loader import load

game_over = blinker.signal("game_over")


class GameScreen(Screen):

    app = prop.ObjectProperty()

    def __init__(self, app, game, network_manager, username="", **kwargs):
        super().__init__(**kwargs)
        load()
        self.app = app
        self.game = game
        self.username = username

        self.handlers = {
            # (mt.GAME, gm.UPDATE): self.game_update,
            # (mt.GAME, gm.COMMAND): self.game_commands,
            (mt.CONTEXT, cm.READY): lambda _: None
        }

        self.add_widget(self.game.make_widget(network_manager=network_manager))
        game_over.connect(self.on_game_over)
        # self.add_widget(Button)

    def on_enter(self, *args):
        self.username = self.app.player_name

    # def game_update(self, payload):
    #     print("KEK")
    #     self.game.handlers[(mt.GAME, gm.UPDATE)](payload)
    #
    # def game_commands(self, payload):
    #     print("HOHO")
    #     self.game.handlers[(mt.GAME, gm.COMMAND)](payload)

    def receive(self, message_struct):
        # print(message_struct)
        if message_struct['message_type'][0] == mt.GAME:
            self.game.receive_message(message_struct)

    def on_game_over(self, _, winner):
        sm = self.app.screen_manager
        sm.get_screen("game_over").winner_name = winner
        sm.current = "game_over"
