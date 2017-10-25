import uuid
import multiprocessing as mlp

from .game_server import start_game_server


class GameSession:

    def __init__(self):
        self._users = {}
        self.uid = uuid.uuid1()
        self._game_process = None

    def add_user(self, user):
        self._users[user.name] = user

    def is_full(self):
        return len(self._users) == 2

    def start(self):
        self._game_process = mlp.Process(
            target=start_game_server,
            args=(self.uid, )
        )
        self._game_process.start()
