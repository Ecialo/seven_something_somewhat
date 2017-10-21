from tornado import (
    queues
)


class User:

    def __init__(self, username, stream):
        self._name = username
        self._stream = stream
        self.queue = queues.Queue()
