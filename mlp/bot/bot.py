from tornado import (
    tcpclient,
    ioloop,
    iostream,
)

from ..game import Game
from ..protocol import (
    message_type as mt,
    game_message as gm,
    lobby_message as lm,
    SEPARATOR,
)
from ..serialization import (
    mlp_loads,
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
        stream = await self.client.connect(self.host, self.port)

    async def receiver(self, stream):
        while True:
            try:
                text = await stream.read_until(SEPARATOR)
                msg = text.rstrip(SEPARATOR)
            except iostream.StreamClosedError:
                break
            else:
                message_struct = mlp_loads(msg)
                ioloop.IOLoop.current().spawn_callback(message_struct)

    def run(self):
        loop = ioloop.IOLoop.current()
        loop.spawn_callback(self.connect)
        loop.start()

    async def process_message(self, message_struct):
        if message_struct['message_type'][0] == mt.GAME:
            self.game.receive_message(message_struct)
        else:
            self.handlers


def run_bot():
    pass
