# -*- coding: utf-8 -*-
import re

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
import kivy.properties as prop

from ...protocol import (
    lobby_message as lm,
    message_type as mt,
)
from ...serialization import (
    make_message
)

Builder.load_file('./mlp/screens/connection/connection_screen.kv')


class ConnectionScreen(Screen):
    app = prop.ObjectProperty()

    def __init__(self, app, **kwargs):
        super(ConnectionScreen, self).__init__(**kwargs)
        self.app = app
        self.handlers = {
            (mt.LOBBY, lm.REFUSE): self.refuse
        }

    def connect(self, host, port, name):
        if not host or not port or not name:
            l = []
            if not host:
                l.append('host')
            if not port:
                l.append('port')
            if not name:
                l.append('name')

            err = 'The following fields are empty: {fields}'.format(
                fields=', '.join(l))
            self.app.notify(err)
            return
        nm = self.app.network_manager
        self.app.player_name = name
        nm.connect(host, int(port), "lobby")
        # nm.host = host
        # nm.port = int(port)
        # nm.start()
        nm.send("lobby", make_message(
            (mt.LOBBY, lm.JOIN),
            name
        ))
        # self.app.connect_to_server(host=host, port=int(port))

    def receive(self, message_struct):
        print(message_struct)
        self.handlers[message_struct["message_type"]](message_struct["payload"])

    def refuse(self, _):
        self.app.notify("Name {} already taken".format(self.app.player_name))
        # self.app.network_manager.loop.stop()

    def accept(self, _):
        pass

    def cancel(self):
        self.app.stop()


class PlayerNameInput(TextInput):
    pattern = re.compile(r'[^a-zA-Z0-9_\-\.\()[]{}<>]')

    def __init__(self, **kwargs):
        super(PlayerNameInput, self).__init__(**kwargs)

    def insert_text(self, substring, from_undo=False):
        pattern = self.pattern
        s = re.sub(pattern, '', substring)
        return super(PlayerNameInput, self).insert_text(s, from_undo=from_undo)
