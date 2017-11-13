from tornado import ioloop

from .lobby_server import LobbyServer

server = LobbyServer()
server.bind(1488)
server.start()
ioloop.IOLoop.current().start()
