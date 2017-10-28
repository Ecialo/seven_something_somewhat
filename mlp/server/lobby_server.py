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
from .game_session import GameSession

process = blinker.signal("process")
disconnect = blinker.signal("disconnect")


class LobbyServer(tcpserver.TCPServer):

    def __init__(self, *args):
        super().__init__(*args)
        self._users = {}
        self._free_session = GameSession()
        self._full_sessions = {}
        self.queue = queues.Queue()

        self.handlers = {
            (mt.LOBBY, lm.FIND_SESSION): self.find_session,
        }

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
        message_type = tuple(message["message_type"])
        ioloop.IOLoop.current().spawn_callback(self.handlers[message_type], user, message['payload'])

    def remove_user(self, user):
        print("Remove", user)
        self._users.pop(user.name)
        ioloop.IOLoop.current().spawn_callback(self.update_userlist)

    async def update_userlist(self):
        await self.queue.put(
            (ALL, ((mt.LOBBY, lm.ONLINE), list(self._users)))
        )

    async def find_session(self, user, _):
        session = self._free_session
        session.add_user(user)
        if session.is_full():
            self._full_sessions[session.uid] = session
            self._free_session = GameSession()
            session.start()
            for user in session.users:
                await self.queue.put((
                    user,
                    ((mt.LOBBY, lm.JOIN), session.uid)
                ))

    async def send_message(self):
        while True:
            destination, message = await self.queue.get()
            if destination is ALL:
                await gen.multi([self._users[user].queue.put(make_message(*message)) for user in self._users])
            else:
                await self._users[destination].queue.put(make_message(*message))
