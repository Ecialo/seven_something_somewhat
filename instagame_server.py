import os
import sys

os.environ["IS_SERVER"] = "1"
sys.path.insert(0, '/home/alessandro/PycharmProjects/mlp')
from tornado import (
    ioloop,
    tcpserver,
    gen,
    # queues,
    iostream,
)

from mlp.serialization import (
    mlp_dumps as encode,
    mlp_loads as decode,
    CreateOrUpdateTag,
    mlp_encoder,
)
from mlp.replication_manager import (
    GameObjectRegistry
)
from mlp.game import (
    Game,
    TurnOrderManager,
)
from mlp.grid import HexGrid
from mlp.protocol import *
from mlp.player import Player
# from mlp.unit import Muzik
from mlp.loader import load
import logging
logger = logging.getLogger(__name__)
handler = logging.FileHandler(
    './game_logs/instagame_server.log',
    'w',
)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
load()
"""
Клиенты отсылают начальные данные (персонажей например)
"""


class TestServer(tcpserver.TCPServer):

    def __init__(self, *args):
        self.game = None
        super().__init__(*args)

    @gen.coroutine
    def handle_stream(self, stream, address):
        ioloop.IOLoop.current().spawn_callback(self.work_with, stream)

    async def send_update(self, stream):
        payload = [CreateOrUpdateTag(o) for o in self.game.registry.dump()]
        message = {
            'message_type': (message_type.GAME, game_message.UPDATE),
            'payload': payload
        }
        await stream.write(encode(message) + SEPARATOR)
        payload = self.game.commands[::]
        message = {
            'message_type': (message_type.GAME, game_message.COMMAND),
            'payload': payload
        }
        await stream.write(encode(message) + SEPARATOR)
        self.game.commands.clear()
        self.game.registry.collect()

    async def work_with(self, stream):
        try:
            inital_message = await stream.read_until(SEPARATOR)
        except iostream.StreamClosedError:
            print("Wait, what?")
        else:
            registry = GameObjectRegistry()
            registry.purge()
            inital_data = decode(inital_message)
            inital_data = inital_data['payload']
            print(inital_data['players'])
            inital_data['players'] = [registry.load_obj(pl_struct) for pl_struct in inital_data['players']]
            print(inital_data['players'])
            grid = HexGrid((5, 5))
            self.game = Game(grid=grid, turn_order_manager=TurnOrderManager(), **inital_data)
            self.game.turn_order_manager.rearrange()
        await self.send_update(stream)
        while True:
            try:
                msg = await stream.read_until(SEPARATOR)
            except iostream.StreamClosedError:
                break
            else:
                message_struct = decode(msg)
                print("\n\n", message_struct)
                message_struct['payload']['author'] = 'overlord'
                message_struct['message_type'] = tuple(message_struct['message_type'])
                if message_struct['message_type'] == (message_type.GAME, game_message.READY):
                    for player in self.game.players:
                        # if player.name == player_name:
                        player.is_ready = True
                    self.game.run()
                    logger.debug("RUN")
                else:
                    logger.debug("RECEIVE")
                    self.game.receive_message(message_struct)
                if self.game.winner is not None:
                    print("WINNER")
                    message = {
                        'message_type': (message_type.LOBBY, lobby_message.GAME_OVER),
                        'payload': self.game.winner.name
                    }
                    await stream.write(encode(message))
                else:
                    await self.send_update(stream)

server = TestServer()
server.listen(1488)
print("Start server on port 1488")
ioloop.IOLoop.current().start()
