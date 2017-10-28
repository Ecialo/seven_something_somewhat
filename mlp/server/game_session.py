import uuid
import multiprocessing as mlp

from .game_server import start_game_server


class GameSession:

    def __init__(self):
        self.users = {}
        self.uid = uuid.uuid1()
        self._game_process = None

    def add_user(self, user):
        self.users[user.name] = user

    def is_full(self):
        # return len(self.users) == 2
        return len(self.users) == 1

    def start(self):
        self._game_process = mlp.Process(
            target=start_game_server,
            args=(
                self.uid,
                list(self.users)
            )
        )
        self._game_process.start()
