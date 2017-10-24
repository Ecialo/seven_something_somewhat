import uuid


class GameSession:

    def __init__(self):
        self._users = {}
        self.uid = uuid.uuid1()

    def add_user(self, user):
        self._users[user.name] = user

    def is_full(self):
        return len(self._users) == 2

    def start(self):
        pass
