from collections import defaultdict

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
import kivy.properties as prop

from ...protocol import (
    message_type as mt,
    game_message as gm,
    lobby_message as lm,
)
from ...loader import load


class GameScreen(Screen):

    app = prop.ObjectProperty()

    def __init__(self, app, game, network_manager, username="", **kwargs):
        super().__init__(**kwargs)
        load()
        self.app = app
        self.game = game
        self.username = username

        self.handlers = {
            (mt.GAME, gm.UPDATE): self.game_update,
            (mt.GAME, gm.COMMAND): self.game_commands,
        }

        self.add_widget(self.game.make_widget(network_manager=network_manager))
        # self.add_widget(Button)

    def game_update(self, payload):
        print("KEK")
        self.game.handlers[(mt.GAME, gm.UPDATE)](payload)

    def game_commands(self, payload):
        print("HOHO")
        self.game.handlers[(mt.GAME, gm.COMMAND)](payload)

    def receive(self, message_struct):
        # print(message_struct)
        if message_struct['message_type'][0] == mt.GAME:
            self.game.receive_message(message_struct)
        # self.handlers[message_struct["message_type"]](message_struct["payload"])