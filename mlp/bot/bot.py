from tornado import (
    tcpclient,
    ioloop,
    iostream,
    queues
)
import blinker

from ..game import Game
from ..loader import load
from ..protocol import (
    message_type as mt,
    game_message as gm,
    context_message as cm,
    lobby_message as lm,
    SEPARATOR,
)
from ..serialization import (
    mlp_loads,
    make_struct,
    make_message,
    remote_action_append,
)
from .strategy.fixed_tactic_strategy import FixedTacticStrategy
from .tactic.random_walk_tactic import RandomWalkTactic
from .tactic.approach_and_attack import AttackNearest
# from .tactic.pass_tactic import PassTactic

presume = blinker.signal("presume")
forget = blinker.signal("forget")
game_over = blinker.signal("game_over")

class Bot:

    def __init__(self, botname, strategy):
        self.is_alive = True
        self.client = tcpclient.TCPClient()
        self.queue = queues.Queue()

        self.strategy = strategy
        self._player = None
        self.botname = botname

        self.game = Game()

        self.handlers = {
            (mt.CONTEXT, cm.READY): self.next_turn,
            (mt.LOBBY, lm.ACCEPT): lambda _: None,
            # (mt.GAME, gm.GAME_OVER): self.game_over,
        }

        presume.connect(self.presume)
        game_over.connect(self.game_over)

    @property
    def player(self):
        if not self._player:
            for pl in self.game.players:
                if pl.name == self.botname:
                    self._player = pl
                    break
        return self._player

    def presume(self, _, actions):
        # print("OLOLO")
        for action in actions:
            msg_struct = remote_action_append(action)
            # print(msg_struct)

            msg_struct[1]["author"] = action.owner.stats.owner
            self.game.receive_message(
                make_struct(*msg_struct)
            )

    async def connect(self, host, port):
        stream = await self.client.connect(host, port)

        loop = ioloop.IOLoop.current()
        loop.spawn_callback(self.receiver, stream)
        loop.spawn_callback(self.consumer, stream)

    async def receiver(self, stream):
        while True:
            try:
                text = await stream.read_until(SEPARATOR)
                msg = text.rstrip(SEPARATOR)
            except iostream.StreamClosedError:
                break
            else:
                message_struct = mlp_loads(msg)
                message_struct["message_type"] = tuple(message_struct["message_type"])
                print(message_struct["message_type"])
                ioloop.IOLoop.current().spawn_callback(self.process_message, message_struct)

    async def consumer(self, stream):
        while True:
            msg_struct = await self.queue.get()
            msg = make_message(*msg_struct)
            try:
                await stream.write(msg)
            except iostream.StreamClosedError:
                break
            self.queue.task_done()

    async def start(self, host, port):
        await self.connect(host, port)
        await self.handshake()

    async def process_message(self, message_struct):
        if message_struct['message_type'][0] == mt.GAME:
            self.game.receive_message(message_struct)
        else:
            cor = self.handlers[message_struct["message_type"]](message_struct["payload"])
            if cor:
                await cor

    async def next_turn(self, _):
        actions = self.strategy.make_decisions(player=self.player)
        print("\n\nACTIONS")
        print(actions)
        for action in actions:
            await self.queue.put(action)

    async def handshake(self):
        self.queue.put(
            ((mt.CONTEXT, cm.JOIN), self.botname)
        )

    def game_over(self, _, winner):
        print("\n\n")
        print(self.botname, winner)
        print("\n\n")
        self.is_alive = False
        ioloop.IOLoop.current().stop()


def run_bot(port, botname='bot', lock=None):
    load()
    # if lock:
    #     lock.acquire()
    lock.wait()
    print("BOTNAME", botname)
    loop = ioloop.IOLoop.current()
    # bot = Bot(FixedTacticStrategy(RandomWalkTactic()))
    bot = Bot(botname, FixedTacticStrategy(AttackNearest()))
    loop.spawn_callback(bot.start, "localhost", port)
    loop.start()
