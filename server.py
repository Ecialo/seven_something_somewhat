from tornado import (
    ioloop,
    tcpserver,
    gen,
    queues,
    iostream,
    locks,
)
from mlp.serialization import (
    mlp_loads,
    mlp_dumps,
    CreateOrUpdateTag,
)
from mlp.replication_manager import (
    GameObjectRegistry,
)
from mlp.protocol import (
    message_type,
    lobby_message,
    chat_message,
    game_message,
    SEPARATOR,
)
from mlp.game import (
    Game,
    TurnOrderManager,
)
from mlp.bind_widget import bind_widget
from mlp.grid import (
    HexCell,
    HexGrid,
)


ALL = "all"


class User:

    def __init__(self, stream, server):
        self.name = None
        self.is_alive = True
        self.is_ready = False

        self.stream = stream
        self.message_queue = queues.Queue()
        self.server = server

        self.inital_data = None
        self.inital_data_loaded = locks.Condition()

        self.handlers = {
            (message_type.CHAT, chat_message.BROADCAST): self.broadcast_chat,
            (message_type.LOBBY, lobby_message.READY): self.ready,
            (message_type.LOBBY, lobby_message.START_GAME): self.load_inital_data,
            (message_type.LOBBY, lobby_message.UNREADY): self.unready,
            (message_type.GAME, game_message.READY): self.game_ready,
            (message_type.GAME, game_message.UPDATE): self.send_to_game((message_type.GAME, game_message.UPDATE)),
            (message_type.GAME, game_message.CALL): self.send_to_game((message_type.GAME, game_message.CALL)),
            (message_type.GAME, game_message.ACTION_APPEND): self.send_to_game(
                (message_type.GAME, game_message.ACTION_APPEND)
            ),
            (message_type.GAME, game_message.ACTION_REMOVE): self.send_to_game(
                (message_type.GAME, game_message.ACTION_REMOVE)
            ),
        }

    async def await_handshake(self):
        try:
            msg = await self.stream.read_until(SEPARATOR)
            msg = msg.rstrip(SEPARATOR)
            # msg = yield self.stream.read_until(pycard_protocol.message_delimiter)
        except iostream.StreamClosedError:
            pass
        else:
            struct = mlp_loads(msg)
            self.name = struct['payload']['name']
            # event_type, params = event[pp.message_struct.TYPE_KEY], event[pp.message_struct.PARAMS_KEY]
            # await self.handle_chat_register(event)

    async def await_messages(self):
        # print("await", self.name)
        while self.is_alive:
            # print "ololo"
            try:
                msg = await self.stream.read_until(SEPARATOR)
                msg = msg.rstrip(SEPARATOR)
                # print(self.name, "rec bytes", msg)
                # msg = yield self.stream.read_until(pycard_protocol.message_delimiter)
            except iostream.StreamClosedError:
                await self.disconnect()
            else:
                message_struct = mlp_loads(msg)

                print(self.name)
                print("get")
                print(message_struct)
                print("")

                type_pair = tuple(message_struct['message_type'])
                # print(self.name, "rec", message_struct)
                ioloop.IOLoop.current().spawn_callback(self.handlers[type_pair], message_struct['payload'])

    async def emmit_message(self, message):
        await self.server.enqueue_messages(message)

    async def enqueue_message(self, message):
        await self.message_queue.put(message)

    async def send_message(self):
        while self.is_alive:
            message = await self.message_queue.get()
            print(self.name)
            print("send")
            print(mlp_loads(message))
            print("")
            # print(self.name, message)
            # print message, isinstance(message, bytes), type(message)
            await self.stream.write(message + SEPARATOR)
            status = self.stream.get_fd_error()
            if status:
                print(str(status))
            self.message_queue.task_done()

    async def disconnect(self):
        self.is_alive = False
        await self.server.remove_user(self)

    async def broadcast_chat(self, msg_struct):
        print("broadcast", msg_struct)
        msg_struct["user"] = self.name
        await self.emmit_message(
            {ALL: {
                "message_type": (message_type.CHAT, chat_message.BROADCAST),
                "payload": msg_struct,
            }}
        )

    async def ready(self, _):
        self.is_ready = True
        await self.server.start_preparations()

    async def unready(self, _):
        self.is_ready = False
        # await self.server.break_preparations()

    async def load_inital_data(self, msg_struct):
        print(self.name)
        print("load inital data")
        print(msg_struct)
        print("")
        self.inital_data = msg_struct
        self.inital_data_loaded.notify_all()

    async def game_ready(self, _):
        await self.server.game_ready(self.name)
        await self.server.send_game_update()

    def send_to_game(self, code):

        async def game_process(msg_struct):
            msg_struct['author'] = self.name
            self.server.game.handlers[code](msg_struct)
            await self.server.send_game_update()

        return game_process


class MLPServer(tcpserver.TCPServer):

    def __init__(self, *args):
        super().__init__(*args)
        self.users = {}
        self.is_ready = False

        self.queue = queues.Queue()

        # self.player_num = players_per_game
        self.game = None
        ioloop.IOLoop.current().spawn_callback(self.send_message)

    @gen.coroutine
    def handle_stream(self, stream, address):
        # stream.set_nodelay(True)
        user = User(stream, self)
        yield user.await_handshake()
        yield self.add_user(user)

    async def add_user(self, user):
        print(user.name)
        self.users[user.name] = user
        loop = ioloop.IOLoop.current()
        loop.spawn_callback(user.await_messages)
        loop.spawn_callback(user.send_message)
        online_msg = {
            "message_type": (message_type.LOBBY, lobby_message.ONLINE),
            "payload": {
                "users": [username for username in self.users.keys()]
            }
        }
        await self.enqueue_messages({user.name: online_msg})
        chat_join_message = {
            "message_type": (message_type.LOBBY, lobby_message.JOIN),
            "payload": {
                "name": user.name
            }
        }
        await self.enqueue_messages(
            {username: chat_join_message for username in self.users if username != user.name}
        )

    async def enqueue_messages(self, messages):
            await self.queue.put(messages)

    async def send_message(self):
        while True:
            rec_messages = await self.queue.get()
            if ALL in rec_messages:
                message = rec_messages[ALL]
                print("SEND TO ALL")
                print("ALL users")
                print([user.name for user in self.users.values()])
                print("message")
                print(message)
                print()
                await gen.multi([user.enqueue_message(mlp_dumps(message)) for user in self.users.values()])
            else:
                # print(rec_messages)
                # tasks = [self.users[user].enqueue_message(mlp_dumps(message)) for user, message in rec_messages.items()]
                # tasks = [self.users["Tester"].enqueue_message()
                await gen.multi(
                    [self.users[user].enqueue_message(mlp_dumps(message)) for user, message in rec_messages.items()])
                # await gen.multi(tasks)
            self.queue.task_done()

    async def remove_user(self, user):
        self.users.pop(user.name)
        part_message = {
            "message_type": (message_type.LOBBY, lobby_message.LEAVE),
            "payload": {
                "name": user.name,
            }
        }
        await self.enqueue_messages({ALL: part_message})

    async def start_preparations(self):
        # ready_users = [u for u in self.users if u.is_ready]
        if await self.countdown(1):
            await self.start_game()

    async def send_game_update(self):
        if self.game:
            payload = [CreateOrUpdateTag(o) for o in self.game.registry.dump()]
            message = {
                'message_type': (message_type.GAME, game_message.UPDATE),
                'payload': payload
            }
            await self.enqueue_messages({ALL: message})

    async def start_game(self):
        # Скинуть первый дамп
        # ПОХНАЛИ
        start_game = {
            "message_type": (message_type.LOBBY, lobby_message.START_GAME),
            "payload": {}
        }
        # Оповестить о начале
        print("notify")
        await self.enqueue_messages({ALL: start_game})
        print("wait data")
        # Получить стартовые даннные
        await gen.multi([u.inital_data_loaded.wait() for u in self.users.values() if u.is_ready])
        # Создать игру
        print("MAKE GAME")
        registry = GameObjectRegistry()
        registry.purge()
        grid = GrassGrid((5, 5))
        inital_data = {
            "players": [
                registry.load_obj(pl_struct)
                for pl_struct in
                (u.inital_data for u in self.users.values() if u.is_ready)
            ]
        }
        self.game = Game(grid=grid, turn_order_manager=TurnOrderManager(), **inital_data)
        self.game.turn_order_manager.rearrange()
        await self.send_game_update()

    async def countdown(self, times):
        for i in range(times, 0, -1):
            ready_users = [u for u in self.users.values() if u.is_ready]
            if len(ready_users) != 2:
                return False
            else:
                countdown_message = {
                    "message_type": (message_type.CHAT, chat_message.BROADCAST),
                    "payload": {
                        "user": "system",
                        "text": "{}...".format(i)
                    }
                }
                await self.enqueue_messages({ALL: countdown_message})
                gen.sleep(1)
        else:
            return True

    async def game_ready(self, player_name):
        for player in self.game.players:
            if player.name == player_name:
                player.is_ready = True
                break
        await self.run_game()

    async def run_game(self):
        if self.game.run():
            for m in self.game.action_log[-1]:
                print(m)
                message = {
                    "message_type": (message_type.CHAT, chat_message.BROADCAST),
                    "payload": {
                        "user": "system",
                        "text": m
                    }
                }
                await self.enqueue_messages({ALL: message})
        if self.game.winner is not None:
            message = {
                'message_type': (message_type.LOBBY, lobby_message.GAME_OVER),
                'payload': self.game.winner.name
            }
            await self.enqueue_messages({ALL: message})


if __name__ == '__main__':
    server = MLPServer()
    # address = socket.gethostbyname("claymore.hopto.org")
    # address = socket.gethostname()
    # address = "192.168.1.65"
    # print(address)
    server.listen(1488)
    # server.listen(8000, address)
    ioloop.IOLoop.current().start()
