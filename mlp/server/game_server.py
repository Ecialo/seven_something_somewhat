from tornado import (
    tcpserver,
    ioloop,
)

from ..loader import load
from ..protocol import (
    SEPARATOR,
    message_type as mt,
    lobby_message as lm,
)
from ..serialization import (
    mlp_loads,
    make_message,
)


class GameServer(tcpserver.TCPServer):

    def __init__(self, players, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.players = players
        self._users = {}
        self.game = None

    async def handle_stream(self, stream, address):
        ioloop.IOLoop.current().spawn_callback(self.handshake, stream)

    async def handshake(self, stream):
        raw_message = await stream.read_until(SEPARATOR)
        message_struct = mlp_loads(raw_message)
        username = message_struct['payload']
        await self.refuse_connection(stream)
        # if username in self._users:
        #     await self.refuse_connection(stream)
        # else:
        #     await self.add_user(username, stream)
        # if len(self._users) == self.players:
        #     await self.start_game()

    @staticmethod
    async def refuse_connection(stream):
        print("Refuse")
        await stream.write(make_message(
            (mt.LOBBY, lm.REFUSE)
        ))
        stream.close()

    async def add_user(self, username, stream):
        pass

    async def start_game(self):
        pass


def start_game_server(host, players):
    load()
    server = GameServer(players)
    server.listen(1488, "/{}".format(host))
    server.start()
