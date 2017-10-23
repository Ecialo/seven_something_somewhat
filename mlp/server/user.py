from tornado import (
    queues,
    iostream,
    ioloop,
)
import blinker

from ..protocol import SEPARATOR
from ..serialization import mlp_loads

process = blinker.signal("process")


class User:

    def __init__(self, username, stream):
        self._name = username
        self._stream = stream
        self.queue = queues.Queue()
        self.is_alive = True

        ioloop.IOLoop.current().spawn_callback(self.send_message)

    async def await_message(self):
        while self.is_alive:
            try:
                msg = await self._stream.read_until(SEPARATOR)
                msg = msg.rstrip(SEPARATOR)
            except iostream.StreamClosedError:
                await self.disconnect()
            else:
                message_struct = mlp_loads(msg)
                process.send(self, message=message_struct)

    async def disconnect(self):
        pass

    async def send_message(self):
        while self.is_alive:
            msg = await self.queue.get()
            try:
                self._stream.write(msg)
            except iostream.StreamClosedError:
                await self.disconnect()
