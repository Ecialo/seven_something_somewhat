from tornado import (
    tcpclient,
    ioloop,
)

from ..game import Game
from ..protocol import (
    message_type as mt,
    game_message as gm,
    lobby_message as lm,
)


class Bot:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = tcpclient.TCPClient()

        self.game = Game()

        self.handlers = {

        }

    async def connect(self):
        pass

    def run(self):
        loop = ioloop.IOLoop.current()
        loop.spawn_callback(self.connect)
        loop.start()
