import uuid
import multiprocessing as mlp

from .game_server import start_game_server

mlp.set_start_method('spawn')


class GameSession:

    def __init__(self, port):
        self.users = {}
        self.port = port
        self.uid = uuid.uuid1()
        self._game_process = None

    def add_user(self, user):
        self.users[user.name] = user

    def is_full(self):
        # return len(self.users) == 2
        return len(self.users) == 1

    def start(self):
        players = [
            {
                'name': name,
                'unit': 'Muzik',
            }
            for name in self.users
        ]
        self._game_process = mlp.Process(
            target=start_game_server,
            name="GameServer {}".format(self.uid),
            args=(
                self.port,
                players,
            ),
            # daemon=True
        )
        self._game_process.start()
