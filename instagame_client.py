import os
from os import path
os.environ['KIVY_HOME'] = path.abspath(os.curdir)
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import (
    ScreenManager,
    FadeTransition,
)
from mlp import network_manager
from mlp import screens
from mlp import protocol as pr
from mlp import game
from mlp import player
from mlp.replication_manager import MetaRegistry
# from mlp.unit import Muzik
from mlp.loader import load
load()
# grid = GrassGrid((5, 3))


class InstagameApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.network_manager = network_manager.NetworkManager(host='localhost', port=1488)
        self.network_watcher = Clock.schedule_interval(self.watch_network, 0)

        sm = ScreenManager()
        sm.transition = FadeTransition()
        sm.add_widget(screens.GameScreen(self, game.Game(), self.network_manager, "overlord", name="game"))
        sm.add_widget(screens.GameOverScreen(self, name="game_over"))
        Muzik = MetaRegistry()['Unit']['Muzik']
        self.players = [player.Player('Ustas', Muzik('Ustas')), player.Player('Vitaline', Muzik('Vitaline'))]
        self.screen_manager = sm
        # self.handlers = {
        #     (pr.message_type.GAME, pr.game_message.UPDATE): self.receive_game_message,
        #     (pr.message_type.GAME, pr.game_message.CALL): self.receive_game_message,
        # }

    def build(self):
        self.network_manager.start()
        self.network_manager.send(
            {"players": [pl.dump() for pl in self.players]}
        )
        return self.screen_manager

    def watch_network(self, _):
        # print("watch")
        for message in self.network_manager.dump():
            message_struct = self.network_manager.decode(message)
            print("INCOMING MESSAGE")
            print(message_struct)
            if message_struct['message_type'][0] == pr.message_type.GAME:
                self.receive_game_message(message_struct)
            elif tuple(message_struct['message_type']) == (pr.message_type.LOBBY, pr.lobby_message.GAME_OVER):
                self.game_over(message_struct['payload'])
            # type_pair = tuple(message_struct['message_type'])
            # print("receive", message_struct)
            # self.handlers[type_pair](message_struct['payload'])

    def on_stop(self):
        self.network_manager.loop.stop()

    def receive_game_message(self, message_struct):
        self.screen_manager.get_screen("game").game.receive_message(message_struct)

    def game_over(self, winner_name):
        print(winner_name)
        self.screen_manager.get_screen("game_over").winner_name = winner_name
        self.screen_manager.current = "game_over"


if __name__ == '__main__':
    InstagameApp().run()