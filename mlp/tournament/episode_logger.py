import shelve

from tornado import (
    tcpserver,
    queues,
    ioloop,
    iostream
)
import cbor2

from ..protocol import SEPARATOR


class EpisodeLogger(tcpserver.TCPServer):
    """
    (episode_name, botname): data
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.is_alive = True
        self._queue = queues.Queue()
        self.shelve = shelve.open('./episodes/episodes')
        ioloop.IOLoop.current().spawn_callback(self.write_to_episodes)

    async def handle_stream(self, stream, address):
        ioloop.IOLoop.current().spawn_callback(self.await_message, stream)

    async def await_message(self, stream):
        while self.is_alive:
            try:
                msg = await stream.read_until(SEPARATOR)
                msg = msg.rstrip(SEPARATOR)
            except iostream.StreamClosedError:
                break
            else:
                # print(msg, bool(msg))
                if msg:
                    await self._queue.put(cbor2.loads(msg))
                else:
                    # print("URA")
                    await self._queue.join()
                    # print("KKK")
                    self.is_alive = False
                    ioloop.IOLoop.current().stop()

    async def write_to_episodes(self):
        while self.is_alive:
            episode_key, step = await self._queue.get()
            episode_key = "_".join(episode_key)
            try:
                self.shelve[episode_key].append(step)
            except KeyError:
                self.shelve[episode_key] = [step]
            self._queue.task_done()


def run_episode_logger():
    server = EpisodeLogger()
    server.bind(66613)
    server.start()
    ioloop.IOLoop.current().start()
