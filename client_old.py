from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.screenmanager import (
    # ScreenManager,
    # Screen,
    FadeTransition,
)
from mlp import network_manager
from mlp import screens
from mlp import protocol as pr
from mlp.widgets.chat.chat_widget import ChatWidget
from mlp import game
from mlp import player
from mlp.unit import Muzik
from mlp.bind_widget import bind_widget
from mlp.serialization import mlp_loads
# from mlp.actions import action
from mlp.grid import (
    HexGrid,
    HexCell,
)
from mlp.terrain import Grass
import os

os.environ['KIVY_IMAGE'] = 'pil,sdl2'


@bind_widget('HexCellWidget')
class GrassCell(HexCell):

    def __init__(self, pos, grid=None):
        super().__init__(pos, grid=grid, terrain=Grass())


@bind_widget('Hexgrid')
class GrassGrid(HexGrid):

    cell = GrassCell


class MLPClientApp(App):
    # connection = None
    #
    # users = []
    # ready = False
    # msg_handlers = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.network_manager = network_manager.NetworkManager()
        self.screen_manager = None
        self.notification_manager = None
        self.chat = None
        self.network_watcher = Clock.schedule_interval(self.watch_network, 0)
        self.handlers = {
            (pr.message_type.LOBBY, pr.lobby_message.JOIN): self.user_join,
            (pr.message_type.LOBBY, pr.lobby_message.LEAVE): self.user_leave,
            (pr.message_type.LOBBY, pr.lobby_message.ONLINE): self.update_userlist,
            (pr.message_type.CHAT, pr.chat_message.BROADCAST): self.receive_chat_message,
            (pr.message_type.LOBBY, pr.lobby_message.START_GAME): self.start_game,
            (pr.message_type.LOBBY, pr.lobby_message.GAME_OVER): self.game_over,
            # (pr.message_type.GAME, pr.game_message.UPDATE): self.receive_game_message,
            # (pr.message_type.GAME, pr.game_message.CALL): self.receive_game_message,
            # (pr.message_type.GAME, pr.game_message.ACTION_APPEND): self.receive_game_message,
            # (pr.message_type.GAME, pr.game_message.ACTION_REMOVE): self.receive_game_message,
        }

        self.player_name = None
        self.users_in_lobby = []

    def build(self):
        # self.set_message_handlers()

        root = Builder.load_file('./mlp/screens/client.kv')

        # nm = NotificationsManager()
        # root.ids.notifications_container.add_widget(nm)

        cw = ChatWidget(app=self)
        root.ids.chat_container.add_widget(cw)

        sm = root.ids.screen_mgr
        sm.transition = FadeTransition()
        #
        sm.add_widget(screens.ConnectionScreen(app=self, name='connection'))
        sm.add_widget(screens.LobbyScreen(app=self, name='lobby'))
        sm.add_widget(screens.GameScreen(self, game.Game(), self.network_manager, name="game"))
        sm.add_widget(screens.GameOverScreen(self, name="game_over"))

        self.screen_manager = sm
        # self.notifications_mgr = nm
        self.chat = cw

        root.ids.chat_button.bind(on_press=self.toggle_chat)
        return root

    def watch_network(self, _):
        # print("watch")
        for message in self.network_manager.dump():
            message_struct = mlp_loads(message)
            print(message_struct)
            # message_struct = message
            message_struct['message_type'] = type_pair = tuple(message_struct['message_type'])

            print("receive", message_struct)
            if type_pair[0] == pr.message_type.GAME:
                self.screen_manager.get_screen("game").game.receive_message(message_struct)
            else:
                self.handlers[type_pair](message_struct['payload'])

    def connect(self):
        self.network_manager.start()
        self.screen_manager.current = 'lobby'
        self.screen_manager.get_screen('game').username = self.player_name
        join_msg = {
            "message_type": (pr.message_type.LOBBY, pr.lobby_message.JOIN),
            "payload":
                {
                    "name": self.player_name,
                }
        }
        self.network_manager.send(join_msg)

    def user_join(self, struct):
        username = struct['name']
        self.users_in_lobby.append(username)

    def user_leave(self, struct):
        username = struct['name']
        self.users_in_lobby.remove(username)

    def update_userlist(self, struct):
        for user in struct['users']:
            self.users_in_lobby.append(user)

    def send_chat_message(self, text):
        msg_struct = {
            "message_type": (pr.message_type.CHAT, pr.chat_message.BROADCAST),
            "payload": {
                "text": text
            }
        }
        self.network_manager.send(msg_struct)

    def receive_chat_message(self, msg_struct):     # TODO вынести форматирование в виджет чата
        # print(msg_struct["text"])
        name = msg_struct["user"]
        msg = msg_struct["text"]
        self.chat.print_message("<{name}>: {msg}".format(name=name, msg=msg))

    # def receive_game_message(self, msg_struct):
    #     print(msg_struct)
    #     self.screen_manager.get_screen("game").game.receive_message(msg_struct)

    def send_lobby_ready(self):
        message = {
            "message_type": (pr.message_type.LOBBY, pr.lobby_message.READY),
            "payload": None,
        }
        self.network_manager.send(message)

    def send_lobby_not_ready(self):
        message = {
            "message_type": (pr.message_type.LOBBY, pr.lobby_message.UNREADY),
            "payload": None,
        }
        self.network_manager.send(message)

    def start_game(self, msg_struct):
        pl = player.Player(self.player_name, Muzik(self.player_name))
        start_game = {
            "message_type": (pr.message_type.LOBBY, pr.lobby_message.START_GAME),
            "payload": pl.dump()
        }
        print("Start game with")
        print(start_game)
        print()
        self.network_manager.send(start_game)
        self.screen_manager.current = "game"

    def on_stop(self):
        self.network_manager.loop.stop()

    def toggle_chat(self, button):
        self.chat.toggle()

    def game_over(self, winner_name):
        self.screen_manager.get_screen("game_over").winner_name = winner_name
        self.screen_manager.current = "game_over"


if __name__ == '__main__':
    MLPClientApp().run()
