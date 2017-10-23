from tornado import (
    tcpserver,
    ioloop,
    queues,
    gen,
)
import blinker

from ..protocol import (
    SEPARATOR,
    message_type as mt,
    lobby_message as lm,
    ALL,
)
from ..serialization import (
    make_message,
    mlp_loads,
)
from .user import User

process = blinker.signal("process")
disconnect = blinker.signal("disconnect")


class LobbyServer(tcpserver.TCPServer):

    def __init__(self, *args):
        super().__init__(*args)
        self._users = {}
        self.queue = queues.Queue()

        handlers = {}

        process.connect(self.process_message)
        disconnect.connect(self.remove_user)
        ioloop.IOLoop.current().spawn_callback(self.send_message)

    async def handle_stream(self, stream, address):
        print("Incoming connection")
        ioloop.IOLoop.current().spawn_callback(self.handshake, stream)

    async def handshake(self, stream):
        raw_message = await stream.read_until(SEPARATOR)
        message_struct = mlp_loads(raw_message)
        username = message_struct['payload']
        if username in self._users:
            await self.refuse_connection(stream)
        else:
            await self.add_user(username, stream)

    @staticmethod
    async def refuse_connection(stream):
        print("Refuse")
        await stream.write(make_message(
            (mt.LOBBY, lm.REFUSE)
        ))
        stream.close()

    async def add_user(self, username, stream):
        await stream.write(make_message(
            (mt.LOBBY, lm.ACCEPT)
        ))
        # await self.queue.put(
        #     (ALL, ((mt.LOBBY, lm.JOIN), username))
        # )
        self._users[username] = User(username, stream)
        await self.update_userlist()

    def process_message(self, user, message):
        pass

    def remove_user(self, user):
        print("Remove", user)
        self._users.pop(user.name)
        ioloop.IOLoop.current().spawn_callback(self.update_userlist)

    async def update_userlist(self):
        await self.queue.put(
            (ALL, ((mt.LOBBY, lm.ONLINE), list(self._users)))
        )

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
                await gen.multi([self._users[user].queue.put(make_message(*message)) for user in self._users])
            else:
                await self._users[destination].queue.put(make_message(*message))
