import os
from os import path
os.environ['KIVY_HOME'] = path.abspath(os.curdir)
os.environ['KIVY_IMAGE'] = 'pil,sdl2'
import json

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import (
    ScreenManager,
    FadeTransition,
)

from mlp import network_manager
from mlp import screens
from mlp.protocol import (
    game_message as gm,
    message_type as mt,
    lobby_message as lm,
    context_message as cm,
)
from mlp import game
from mlp import player
from mlp.replication_manager import MetaRegistry
# from mlp.unit import Muzik
from mlp.loader import load
from ..serialization import mlp_loads, mlp_load, make_struct
load()
# grid = GrassGrid((5, 3))


class InstagameApp(App):

    def __init__(self, replay, **kwargs):
        super().__init__(**kwargs)
        self.player_name = "viewer"

        sm = ScreenManager()
        sm.transition = FadeTransition()
        sm.add_widget(screens.GameScreen(self, game.Game(), None, "viewer", name="game"))
        sm.add_widget(screens.GameOverScreen(self, name="game_over"))
        self.screen_manager = sm
        with open(replay, 'rb') as replay_file:
            self.replay = mlp_load(replay_file)
        self.step = 0

    def build(self):
        root = Builder.load_file('./mlp/replay/replay_viewer.kv')

        sm = root.ids.screen_mgr
        sm.transition = FadeTransition()
        #
        # sm.add_widget(screens.ConnectionScreen(app=self, name='connection'))
        # sm.add_widget(screens.LobbyScreen(app=self, name='lobby'))
        sm.add_widget(screens.GameScreen(self, game.Game(), None, name="game"))
        sm.add_widget(screens.GameOverScreen(self, name="game_over"))
        # self.screen_manager.current = 'game'
        self.screen_manager = sm

        root.ids.next_step.bind(on_press=self.next_step)
        return root

    def receive_game_message(self, message_struct):
        self.screen_manager.get_screen("game").game.receive_message(message_struct)

    def game_over(self, winner_name):
        print(winner_name)
        self.screen_manager.get_screen("game_over").winner_name = winner_name
        self.screen_manager.current = "game_over"

    def next_step(self, button):
        try:
            # print(self.screen_manager.current)
            state = self.replay[self.step]['state']
            commands = self.replay[self.step]['commands']
            st = mlp_loads(state)
            st = make_struct(
                (mt.GAME, gm.UPDATE), st
            )
            self.receive_game_message(st)
            com = mlp_loads(commands)
            com = make_struct(
                (mt.GAME, gm.COMMAND), com
            )
            self.receive_game_message(com)
            print(st)
            # self.screen_manager.current_screen.game.registry.load(st)
            # self.screen_manager.current_screen.game.envoke_commands(com)
            # print(st, com)
            self.step += 1
            # state = self.replay.readline()
            # command = self.replay.readline()
            # mlp_loads(state)
            # mlp_loads(command)
        except EOFError:
            pass


if __name__ == '__main__':
    import sys
    InstagameApp(sys.argv[1]).run()
