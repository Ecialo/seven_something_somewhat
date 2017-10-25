from tornado import (
    tcpserver,
)

from ..loader import load


class GameServer(tcpserver.TCPServer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game = None

    async def handle_stream(self, stream, address):
        pass


def start_game_server(host):
    load()
    server = GameServer()
    server.listen(1488, "/{}".format(host))
    server.start()
