import multiprocessing as mlp

import blinker

from ..server.game_session import GameSession
from ..bot.bot import run_bot


process = blinker.signal('process')


@process.connect
def print_content(_, content):
    print(content)


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
        self.users[USTAS] = [bot1]
        # self.users.update(bot1)
        self.users[VITALINE] = [bot2]
        # self.users.update(bot2)

    def start(self):
        super().start()
        self._bot1_process = mlp.Process(
            target=run_bot,
            name='Bot Vitaline',
            args=(self.port, VITALINE, self._lock)
        )
        self._bot2_process = mlp.Process(
            target=run_bot,
            name='Bot Ustas',
            args=(self.port, USTAS, self._lock)
        )
        self._bot1_process.start()
        self._bot2_process.start()

    async def shutdown(self):
        await super().shutdown()
        if self._bot1_process.is_alive():
            self._bot1_process.terminate()
        if self._bot2_process.is_alive():
            self._bot2_process.terminate()
