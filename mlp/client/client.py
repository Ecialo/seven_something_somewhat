from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.screenmanager import (
    # ScreenManager,
    # Screen,
    FadeTransition,
)

from ..widgets.notifications import NotificationsManager
from ..serialization import mlp_loads
from .. import network_manager
from .. import screens
from .. import protocol as pr
from ..widgets.chat.chat_widget import ChatWidget
from ..game import Game


class MLPClientApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.network_manager = network_manager.NetworkManager()
        self.screen_manager = None
        self.notification_manager = None
        self.chat = None
        self.network_watcher = Clock.schedule_interval(self.watch_network, 0)
        self.handlers = {}
        self.player_name = None
        self.users_in_lobby = []

    def build(self):
        # self.set_message_handlers()

        root = Builder.load_file('./mlp/screens/client.kv')

        nm = NotificationsManager()
        root.ids.notifications_container.add_widget(nm)

        cw = ChatWidget(app=self)
        root.ids.chat_container.add_widget(cw)

        sm = root.ids.screen_mgr
        sm.transition = FadeTransition()
        #
        sm.add_widget(screens.ConnectionScreen(app=self, name='connection'))
        # sm.add_widget(screens.LobbyScreen(app=self, name='lobby'))
        sm.add_widget(screens.GameScreen(self, Game(), self.network_manager, name="game"))
        sm.add_widget(screens.GameOverScreen(self, name="game_over"))
        self.screen_manager = sm
        self.notifications_mgr = nm
        self.chat = cw

        root.ids.chat_button.bind(on_press=self.toggle_chat)
        self.network_manager.start()
        return root

    def watch_network(self, _):
        for message in self.network_manager.dump():
            message_struct = mlp_loads(message)
            print(message_struct)
            message_struct['message_type'] = tuple(message_struct['message_type'])
            self.screen_manager.current_screen.receive(message_struct)

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


    def on_stop(self):
        self.network_manager.loop.stop()

    def toggle_chat(self, button):
        self.chat.toggle()

    def notify(self, text):
        """
        Показывает уведомление вверху экрана.
        """

        self.notifications_mgr.notify(text)


if __name__ == '__main__':
    MLPClientApp().run()
