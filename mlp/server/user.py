from tornado import (
    queues,
    iostream,
    ioloop,
)
import blinker

from ..protocol import SEPARATOR
from ..serialization import mlp_loads

process = blinker.signal("process")
disconnect = blinker.signal("disconnect")


class User:

    def __init__(self, username, stream):
        self.name = username
        self._stream = stream
        self.queue = queues.Queue()
        self.is_alive = True

        ioloop.IOLoop.current().spawn_callback(self.send_message)
        ioloop.IOLoop.current().spawn_callback(self.await_message)

    async def await_message(self):
        while self.is_alive:
            try:
                msg = await self._stream.read_until(SEPARATOR)
                msg = msg.rstrip(SEPARATOR)
            except iostream.StreamClosedError:
                await self.disconnect()
            else:
                message_struct = mlp_loads(msg)
                if isinstance(message_struct['payload'], dict):
                    message_struct['payload']['author'] = self.name
                process.send(self, message=message_struct)

    async def disconnect(self):
        print("Disconnect", self)
        self.is_alive = False
        disconnect.send(self)

    async def send_message(self):
        while self.is_alive:
            msg = await self.queue.get()
            try:
                self._stream.write(msg)
            except iostream.StreamClosedError:
                await self.disconnect()
