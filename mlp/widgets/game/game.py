from collections import deque
from kivy.uix import (
    floatlayout,
    button,
)
from ..grid import CompositeArena
from ..general import camera
# from mlp.actions.action import (
#     RandomMove,
#     Attack,
# )
from ...network_manager import NetworkManager
from mlp.serialization import (
    remote_action_append,
    remote_action_remove,
)
from mlp.protocol import *
from ..cursor import MainCursor
import blinker
from kivy.lang import Builder
from kivy.core.window import Window
commands = blinker.signal("commands")
# Builder.load_file('/home/alessandro/PycharmProjects/mlp/mlp/widgets/game/game.kv')


class Game(floatlayout.FloatLayout):

    def __init__(self, game, **kwargs):
        self.network_manager = kwargs.pop('network_manager')
        super().__init__(**kwargs)
        # self.network_manager = NetworkManager('localhost', 1488)
        self.game = game
        self.add_widget(game.grid.make_widget(pos_hint={'x': 0.5, 'y': 0.5}))
        button_ = button.Button(
            text="MOVE",
            pos_hint={'x': 0.5, 'y': 0.2},
            size_hint=(0.1, 0.1)
        )
        # button_.bind(on_press=lambda _: self.move_muzik)
        self.add_widget(button_)
        # Clock.schedule_interval(self.watcher, 0)
        # self.network_manager.start()

    # def move_muzik(self, _):
    #     for cell in self.game.grid:
    #         if cell.object is not None:
    #             self.network_manager.send(remote_call(cell.object.move))

    def on_receive_message(self, struct):
        pass

    # def watcher(self, _):
    #     # messages = self.network_manager.dump()
    #     for message in self.network_manager.dump():
    #         message_struct = self.network_manager.decode(message)
    #         print(message_struct)
    #         self.game.receive_message(message_struct)


class RemoteGame(floatlayout.FloatLayout):

    def __init__(self, game, **kwargs):
        self.network_manager = kwargs.pop('network_manager')
        self._cursor = deque([MainCursor(self)])
        super().__init__(**kwargs)
        self.is_loaded = False
        # self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        # self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.grid = None
        self.camera = None
        self.turn_order_indicator = None
        # self.network_manager = NetworkManager('localhost', 1488)
        self.game = game
        self.stats = None
        self.action_bar = None
        self.current_action_bar = None
        # self.size = self.ids.background.size
        # self.add_widget(attack_button)
        # Clock.schedule_interval(self.watcher, 0)
        # self.network_manager.start()
        commands.connect(self.process_commands)

    # def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
    #     return False

    # def _keyboard_closed(self):
    #     self._keyboard.unbind(on_key_down=self._on_keyboard_down)
    #     self._keyboard = None

    # def move_muzik(self, _):
    #     for cell in self.game.grid:
    #         print(cell.pos, cell.object)
    #         if cell.object is not None:
    #             # print("\n\n\n!!!!\n", cell.object)
    #             self.network_manager.send(remote_call(cell.object.move))

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

    # def attack(self, _):
    #     o = self.selected_cell.object
    #     if o is not None:
    #         self.network_manager.send(
    #             remote_action_setup(Attack(o))
    #         )

    def run_game(self, _):
        # self.network_manager.send(
        #     remote_action_remove()
        # )
        for unit in self.game.units:
            for action in unit.current_action_bar:
                self.network_manager.send('game', remote_action_append(action))
        self.network_manager.send('game',
            {
                'message_type': (message_type.GAME, game_message.READY),
                # 'payload': {'player': self.parent.app.player_name}
                'payload': {}
            }
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
            # self.add_widget(self.grid)
            self.add_widget(self.camera, index=-1)
            self.add_widget(self.turn_order_indicator)
            # self.grid.update_children()
            # self.grid.bind(selected_cell=self.show_stats)
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

    # def loopback_message(self, message_struct):
    #     message_struct['author'] =
    #     self.receive_message(message_struct)

    def receive_message(self, message_struct):
        print(message_struct)
        self.game.receive_message(message_struct)

    def watcher(self, _):
        # messages = self.network_manager.dump()
        for message in self.network_manager.dump():
            message_struct = self.network_manager.decode(message)
            # print(message_struct)
            self.receive_message(message_struct)

    def process_commands(self, _, commands):
        print(commands)
        for command in commands:
            command.execute()

    # def show_stats(self, _, selected_cell):
    #     if self.stats:
    #         self.remove_widget(self.stats)
    #     if self.action_bar:
    #         self.remove_widget(self.action_bar)
    #     selected_object = selected_cell.cell.object
    #     if selected_object:
    #         # self.stats = selected_object.stats.make_widget(pos_hint={'x': 0.2, 'y': 0.5})
    #         selected_object.make_widget().on_select(self)
    #         # self.add_widget(self.stats)
    #     # else:
    #     #     self.stats = None
