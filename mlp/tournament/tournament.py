import multiprocessing as mlp

import blinker
from tornado import (
    ioloop
)

from ..protocol import (
    message_type as mt,
    game_message as gm,
)
from ..server.game_session import GameSession
from ..bot.bot import run_bot


process = blinker.signal('process')


@process.connect
def print_content(_, message):
    pass
    # print("PRILETELO", message)


USTAS = 'Ustas'
VITALINE = 'Vitaline'


class TournamentGameSession(GameSession):

    def __init__(
            self,
            bot1,
            bot2,
    ):
        super().__init__(14088)
        self._bot1_process = None
        self._bot2_process = None
        self._lock = mlp.Barrier(3)
        self.users[USTAS] = bot1
        # self.users.update(bot1)
        self.users[VITALINE] = bot2
        # self.users.update(bot2)
        self.handlers = {
            (mt.GAME, gm.GAME_OVER): self.game_over
        }
        process.connect(self.process)

    def start(self):
        super().start()
        self._bot1_process = mlp.Process(
            target=run_bot,
            name='Bot Vitaline',
            args=(self.port, VITALINE, self.session_name, self.users[VITALINE][0], self._lock)
        )
        self._bot2_process = mlp.Process(
            target=run_bot,
            name='Bot Ustas',
            args=(self.port, USTAS, self.session_name, self.users[USTAS][0], self._lock)
        )
        self._bot1_process.start()
        self._bot2_process.start()

    def game_over(self, payload):
        # print('WINNER', payload)
        ioloop.IOLoop.current().spawn_callback(self.shutdown)

    async def shutdown(self):
        await super().shutdown()
        # print("STOP")
        ioloop.IOLoop.current().stop()
        self._bot1_process.join()
        self._bot2_process.join()
        # self._bot1_process
        # if self._bot1_process.is_alive():
        #     self._bot1_process.terminate()
        # if self._bot2_process.is_alive():
        #     self._bot2_process.terminate()

    # @process.connect
    def process(self, _, message):
        ioloop.IOLoop.current().spawn_callback(self.handlers[tuple(message['message_type'])], message['payload'])
