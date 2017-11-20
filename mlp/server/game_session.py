import uuid
import multiprocessing as mlp
import socket

import blinker
from tornado import (
    ioloop,
    iostream
)

from .game_server import start_game_server
from ..protocol import (
    SEPARATOR,
    message_type as mt,
    context_message as cm,
)
from ..serialization import (
    mlp_loads,
    make_message,
)
from ..bot import (
    run_bot,
)

mlp.set_start_method('spawn')

process = blinker.signal("process")


class GameSession:

    def __init__(self, port):
        self.users = {}
        self.port = port
        self.uid = str(uuid.uuid1())
        self._game_process = None
        self._lock = None
        self._stream = None
        self.is_alive = True

    def __contains__(self, item):
        return item.name in self.users

    def add_user(self, user):
        self.users[user.name] = user

    def remove_user(self, user):
        self.users.pop(user.name)
        if self.is_empty() and self._game_process and self._game_process.is_alive():
            ioloop.IOLoop.current().spawn_callback(self.send_terminate_signal)

    def is_full(self):
        # return len(self.users) == 2
        return len(self.users) == 1

    def is_empty(self):
        return len(self.users) == 0

    def start(self):
        ssock, csock = socket.socketpair()
        self._stream = iostream.IOStream(ssock)

        players = [
            {
                'name': name,
                'unit': 'Muzik',
            }
            for name in self.users
        ]
        self._game_process = mlp.Process(
            target=start_game_server,
            name="GameServer {}".format(self.uid),
            args=(
                self.uid,
                self.port,
                csock,
                players,
                self._lock,
            ),
            # daemon=True
        )
        self._game_process.start()
        ioloop.IOLoop.current().spawn_callback(self.await_message)

    async def await_message(self):
        while self.is_alive:
            try:
                msg = await self._stream.read_until(SEPARATOR)
                # print("FROM GAME SERVER")
                # print(msg)
                msg = msg.rstrip(SEPARATOR)
            except iostream.StreamClosedError:
                await self.shutdown()
            else:
                # pass
                message_struct = mlp_loads(msg)
                process.send(self, message=message_struct)

    async def shutdown(self):
        self.users.clear()
        self.is_alive = False
        # await self._stream.write()
        if self._game_process.is_alive():
            self._game_process.terminate()

    async def send_terminate_signal(self):
        await self._stream.write(make_message(
            (mt.CONTEXT, cm.TERMINATE)
        ))


class UserGameSession(GameSession):

    def is_full(self):
        return len(self.users) == 2


class AIGameSession(GameSession):

    def __init__(self, port):
        super().__init__(port)
        self._bot_process = None
        self._lock = mlp.Semaphore(0)

    def start(self):
        # Добавить бота
        self.users['bot'] = None
        super().start()
        # Запустить бота
        self._bot_process = mlp.Process(
            target=run_bot,
            name="Bot {}".format(self.uid),
            args=(self.port, self._lock),
        )
        self._bot_process.start()
        self.users.pop('bot')

    async def shutdown(self):
        await super().shutdown()
        if self._bot_process.is_alive():
            self._bot_process.terminate()
