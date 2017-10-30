from tornado import (
    tcpserver,
    ioloop,
    iostream,
    queues,
    gen,
)
import blinker

from ..loader import load
from ..protocol import (
    SEPARATOR,
    ALL,
    message_type as mt,
    lobby_message as lm,
    game_message as gm,
)
from ..serialization import (
    mlp_loads,
    make_message,
    CreateOrUpdateTag,
)
from .user import User
from ..player import Player
from ..grid import HexGrid
from ..game import (
    Game,
    TurnOrderManager,
)

process = blinker.signal("process")
disconnect = blinker.signal("disconnect")


class GameServer(tcpserver.TCPServer):

    def __init__(self, players, stream, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.players = players
        self._users = {}
        self.queue = queues.Queue()
        self.lobby_stream = stream
        self.game = None

        self.handlers = {

        }

        self.is_started = False
        self.is_alive = True
        process.connect(self.process_message)
        ioloop.IOLoop.current().spawn_callback(self.send_message)

    async def handle_stream(self, stream, address):
        print("From game with love")
        await self.lobby_stream.write(b"OLOLO"+SEPARATOR)
        ioloop.IOLoop.current().spawn_callback(self.handshake, stream)

    async def handshake(self, stream):
        raw_message = await stream.read_until(SEPARATOR)
        message_struct = mlp_loads(raw_message)
        username = message_struct['payload']
        # await self.refuse_connection(stream)
        if username in self._users:
            await self.refuse_connection(stream)
        else:
            await self.add_user(username, stream)
        print(len(self._users), len(self.players))
        if len(self._users) == len(self.players):
            await self.start_game()

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
        self._users[username] = User(username, stream)

    async def start_game(self):
        print("start_game")
        grid = HexGrid((5, 5))
        turn_order_manager = TurnOrderManager()
        players = [Player.make_from_skel(player) for player in self.players]
        self.game = Game(grid=grid, players=players, turn_order_manager=turn_order_manager)
        self.game.turn_order_manager.rearrange()
        await self.send_update()

    async def send_message(self):
        while self.is_alive:
            destination, message = await self.queue.get()
            if destination is ALL:
                await gen.multi([self._users[user].queue.put(make_message(*message)) for user in self._users])
            else:
                await self._users[destination].queue.put(make_message(*message))

    async def send_update(self):
        print("send_update")
        payload = [CreateOrUpdateTag(o) for o in self.game.registry.dump()]
        await self.queue.put((
            ALL,
            ((mt.GAME, gm.UPDATE), payload)
        ))
        payload = self.game.commands[::]
        await self.queue.put((
            ALL,
            ((mt.GAME, gm.COMMAND), payload)
        ))
        self.game.commands.clear()
        self.game.registry.collect()

    def process_message(self, user, message):
        message_type = tuple(message["message_type"])
        ioloop.IOLoop.current().spawn_callback(self.handlers[message_type], user, message['payload'])

    def remove_user(self, user):
        self._users.pop(user.name)

    async def check_status(self):
        if len(self._users) == 0:
            pass


def start_game_server(port, socket, players):
    load()
    print("START SERVER AT PORT {}".format(port))
    server = GameServer(players, iostream.IOStream(socket))
    server.bind(port)
    server.start()
    ioloop.IOLoop.current().start()
