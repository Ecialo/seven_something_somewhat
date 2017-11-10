# -*- coding: utf-8 -*-
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
import kivy.properties as prop

from ...protocol import (
    message_type as mt,
    lobby_message as lm,
)

Builder.load_file('./mlp/screens/lobby/lobby_screen.kv')


class LobbyScreen(Screen):
    app = prop.ObjectProperty()

    def __init__(self, app, host, port, **kwargs):
        super(LobbyScreen, self).__init__(**kwargs)
        self.app = app
        self.host = host
        self.port = port
        self.nm = self.app.network_manager

        self.handlers = {
            (mt.LOBBY, lm.ONLINE): self.update_users,
            (mt.LOBBY, lm.JOIN): self.join_session,
            (mt.LOBBY, lm.REFUSE): self.refuse,
            (mt.LOBBY, lm.ACCEPT): self.accept,
        }

    def receive(self, message_struct):
        # print(message_struct)
        self.handlers[message_struct["message_type"]](message_struct["payload"])

    def update_users(self, users):
        self.ids.online_users.data = [{'text': user} for user in sorted(users)]

    def update_sessions(self, sessions):
        pass

    def find_session(self, opponent):
        nm = self.nm
        nm.send(
            "lobby",
            (
                (mt.LOBBY, lm.FIND_SESSION),
                opponent,
            )
        )

    def join_session(self, port):
        print("Connect to {} {}".format(self.host, port))
        self.nm.connect(self.host, int(port), "game")
        self.nm.send("game", (
            (mt.LOBBY, lm.JOIN),
            self.app.player_name
        ))

    def refuse(self, _):
        self.app.notify("FUCK YOU")

    def accept(self, _):
        self.app.screen_manager.current = 'game'
