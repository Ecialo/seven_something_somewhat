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

    def __init__(self, app, **kwargs):
        super(LobbyScreen, self).__init__(**kwargs)
        self.app = app

        self.handlers = {
            (mt.LOBBY, lm.ONLINE): self.update_users
        }

    def receive(self, message_struct):
        # print(message_struct)
        self.handlers[message_struct["message_type"]](message_struct["payload"])

    def update_users(self, users):
        self.ids.online_users.data = [{'text': user} for user in sorted(users)]

    def update_sessions(self, sessions):
        pass

    def find_session(self):
        nm = self.app.network_manager
        nm.send(
            "lobby",
            (
                (mt.LOBBY, lm.FIND_SESSION),
                None,
            )
        )
