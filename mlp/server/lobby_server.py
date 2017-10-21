from tornado import (
    tcpserver,
    ioloop,
    queues,
    gen,
)

from ..protocol import (
    SEPARATOR,
    message_type as mt,
    lobby_message as lm,
    ALL,
)
from ..serialization import make_message
from .user import User


class LobbyServer(tcpserver.TCPServer):

    def __init__(self, *args):
        super().__init__(*args)
        self._users = {}
        self.queue = queues.Queue()

    async def handle_stream(self, stream, address):
        ioloop.IOLoop.current().spawn_callback(self.handshake, stream)

    async def handshake(self, stream):
        username = await stream.read_until(SEPARATOR)
        if username in self._users:
            await self.refuse_connection(stream)
        else:
            await self.add_user(username, stream)

    @staticmethod
    async def refuse_connection(stream):
        await stream.write(make_message(
            (mt.LOBBY, lm.REFUSE)
        ))
        stream.close()

    async def add_user(self, username, stream):
        await stream.write(make_message(
            (mt.LOBBY, lm.ACCEPT)
        ))
        await self.queue.put(
            (ALL, make_message((mt.LOBBY, lm.JOIN), username))
        )
        self._users[username] = User(username, stream)
        await self.queue.put(
            (username, make_message((mt.LOBBY, lm.ONLINE), list(self._users)))
        )

    async def remove_user(self, user):
        pass

    async def create_game_node(self):
        pass

    async def deconstruct_game_node(self):
        pass

    async def connect_user_to_game_node(self):
        pass

    async def disconnect_user_fom_game_node(self):
        pass

    async def send_message(self):
        while True:
            destination, message = await self.queue.get()
            if destination is ALL:
                await gen.multi([self._users[user].queue.put(message) for user in self._users])
            else:
                await self._users[destination].queue.put(message)
