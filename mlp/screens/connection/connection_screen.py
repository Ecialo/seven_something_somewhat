# -*- coding: utf-8 -*-

import io, sys
import json
import re

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
import kivy.properties as prop


Builder.load_file('./mlp/screens/connection/connection_screen.kv')


class ConnectionScreen(Screen):
    app = prop.ObjectProperty()

    def __init__(self, app, **kwargs):
        super(ConnectionScreen, self).__init__(**kwargs)
        self.app = app

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
        nm.host = host
        nm.port = int(port)
        nm.start()
        # self.app.connect_to_server(host=host, port=int(port))

    def receive(self, message_struct):
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
