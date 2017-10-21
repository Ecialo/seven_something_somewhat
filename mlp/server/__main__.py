from tornado import ioloop

from .lobby_server import LobbyServer

server = LobbyServer()
server.listen(1488)
ioloop.IOLoop.current().start()
