from collections import deque
from kivy.uix import (
    floatlayout,
    button,
)
from ..grid import CompositeArena
from ..general import camera
from ...serialization import (
    remote_action_append,
)
from ...protocol import *
from ..cursor import MainCursor
import blinker

commands = blinker.signal("commands")


class RemoteGame(floatlayout.FloatLayout):

    def __init__(self, game, **kwargs):
        self.network_manager = kwargs.pop('network_manager')
        self._cursor = deque([MainCursor(self)])
        super().__init__(**kwargs)
        self.is_loaded = False
        self.grid = None
        self.camera = None
        self.turn_order_indicator = None
        self.game = game
        self.stats = None
        self.action_bar = None
        self.current_action_bar = None
        commands.connect(self.process_commands)

    @property
    def cursor(self):
        return self._cursor[0]

    def add_cursor(self, cursor):
        self.cursor.deactivate()
        self._cursor.appendleft(cursor)
        self.cursor.activate()

    def remove_cursor(self):
        cursor = self._cursor.popleft()
        cursor.deactivate()
        self.cursor.activate()

    def run_game(self, _):
        for unit in self.game.units:
            for action in unit.current_action_bar:
                self.network_manager.send(remote_action_append(action))
        self.network_manager.send(
            {
                'message_type': (message_type.GAME, game_message.READY),
                'payload': {}
            }
                self.network_manager.send('game', remote_action_append(action))
        self.network_manager.send('game', (
                (message_type.GAME, game_message.READY),
                # 'payload': {'player': self.parent.app.player_name}
                {}
            )
        )

    @property
    def selected_cell(self):
        return self.game.grid.make_widget().selected_cell.cell

    def on_receive_message(self, struct):
        # print(struct)
        # print("LOAD GAME", self.is_loaded)
        if not self.is_loaded:
            self.grid = self.game.grid.make_widget(pos_hint={'center_x': 0.5, 'center_y': 0.5})
            arena = CompositeArena(self.grid)
            self.camera = camera.Camera(arena)
            self.turn_order_indicator = self.game.turn_order_manager.make_widget()
            self.add_widget(self.camera, index=-1)
            self.add_widget(self.turn_order_indicator)
            self.is_loaded = True
            run_button = button.Button(
                text="RUN",
                pos_hint={'x': 0.73, 'y': 0.8},
                size_hint=(0.1, 0.1)
            )
            run_button.bind(on_press=self.run_game)  # TODO внести эту кнопку в главный курсор
            self.camera.normed_camera_pos = (0.25, 0.25)
            self.add_widget(run_button, index=1)
        self.cursor.update()

    def receive_message(self, message_struct):
        print(message_struct)
        self.game.receive_message(message_struct)

    def watcher(self, _):
        for message in self.network_manager.dump():
            message_struct = self.network_manager.decode(message)
            self.receive_message(message_struct)

    def process_commands(self, _, commands):
        print(commands)
        try:
            command = commands.popleft()
        except IndexError:
            print("FAIL")
        else:
            print("SUCCESS")
            command.execute(commands)

