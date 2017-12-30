from typing import (
    Optional,
    Dict,
    List,
    Any,
    Tuple,
    Callable,
)
from socket import socket as soc
from multiprocessing import Barrier

from tornado import (
    tcpserver,
    iostream,
    queues,
)


from ..game import Game
from .user import User
from ..replay.replay_handler import ReplayHandler
from ..protocol import (
    Message,
    Handler,
)


class GameServer(tcpserver.TCPServer):

    game: Optional[Game]
    _users: Dict[str, User]
    players: List[Dict[str, str]]
    replay_handler: ReplayHandler
    queue: queues.Queue
    is_alive: bool
    lobby_stream: iostream.IOStream
    handlers: Handler

    def __init__(
            self,
            session_name: str,
            players: List[Dict[str, str]],
            lobby_stream: iostream.IOStream,
            *args,
            **kwargs
    ) -> None: ...
    async def handle_stream(self, stream: iostream.IOStream, address: str) -> None: ...
    async def handshake(self, stream: iostream.IOStream) -> None: ...
    async def refuse_connection(self, stream: iostream.IOStream) -> None: ...
    async def add_user(self, username: str, stream: iostream.IOStream) -> None: ...
    async def start_game(self) -> None: ...
    async def send_update(self) -> None: ...
    def process_message(self, user: User, message: Message) -> None: ...
    def process_game_over(self, _: Any, winner: str) -> None: ...
    async def _process_game_over(self, winner: str) -> None: ...
    async def shutdown(self) -> None: ...
    def remove_user(self, user: User) -> None: ...
    def next_phase(self, _: Any) -> None: ...
    async def send_message(self) -> None: ...
    async def process_with_game(self, message: Message) -> None: ...
    async def check_status(self) -> None: ...
    async def await_from_session(self) -> None: ...

def start_game_server(
        session_name: str,
        port: int,
        socket: soc,
        players: List[Dict[str, str]],
        lock: Optional[Barrier],
) -> None: ...

async def unlock(lock: Barrier) -> None: ...