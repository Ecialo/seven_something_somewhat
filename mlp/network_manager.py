from threading import Thread
import queue
from collections import (
    deque,
    defaultdict,
)

from tornado import (
    ioloop,
    gen,
    queues as tq,
    tcpclient,
    iostream
)

from .serialization import (
    mlp_dumps,
    mlp_loads,
)
from .protocol import SEPARATOR
from .serialization import make_message


class NetworkManager(Thread):

    def __init__(self, encoder=mlp_dumps, decoder=mlp_loads):
        super().__init__(name="NetworkManager")
        self.loop = ioloop.IOLoop.current()
        self.client = tcpclient.TCPClient()
        self.connections = {}
        self.queues = defaultdict(tq.Queue)
        self.inqueue = tq.Queue()
        self.outqueue = queue.Queue()
        self.encode = encoder
        self.decode = decoder

    def connect(self, host, port, name):
        self.loop.spawn_callback(self._connect, host, port, name)

    @gen.coroutine
    def _connect(self, host, port, name):
        print("Connect", name)
        stream = yield self.client.connect(host, port)
        print("Success")
        self.connections[name] = stream
        print(self.connections)
        self.loop.spawn_callback(self.receiver, stream)
        self.loop.spawn_callback(self.named_consumer(name))

    @gen.coroutine
    def consumer(self):
        while True:
            address, text = yield self.inqueue.get()
            yield self.queues[address].put(text)
            self.inqueue.task_done()

    def named_consumer(self, name):
        @gen.coroutine
        def consumer():
            while True:
                text = yield self.queues[name].get()
                stream = self.connections[name]
                try:
                    yield stream.write(text)
                except iostream.StreamClosedError:
                    break
                self.queues[name].task_done()

        return consumer

    @gen.coroutine
    def receiver(self, stream):
        while True:
            try:
                text = yield stream.read_until(SEPARATOR)
                text = text.rstrip(SEPARATOR)
            except iostream.StreamClosedError:
                break
            else:
                self.outqueue.put_nowait(text)

    def send(self, address, message):
        self.inqueue.put_nowait((address, make_message(*message)))

    def dump(self):
        data = deque()
        while not self.outqueue.empty():
            data.append(self.outqueue.get_nowait())
        return data

    def run(self):
        self.loop.spawn_callback(self.consumer)
        self.loop.start()
