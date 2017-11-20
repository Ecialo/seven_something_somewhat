from typing import (
    Dict,
    Any,
    Deque,
)

from tornado import (
    tcpserver,
    queues,
)

from .game_session import GameSession
from .user import User
from ..protocol import (
    Message,
    Handler,
)

class LobbyServer(tcpserver.TCPServer):
    _full_sessions: Dict[str, GameSession]
    queue: queues.Queue
    port_pool: Deque[int]
    handlers: Handler
    _users: Dict[str, User]

    def __init__(self, *args) -> None: ...
    def get_port(self) -> int: ...
    async def find_session(self, user: User, opponent: str) -> None: ...
    async def terminate_session(self, session: GameSession, _: Any) -> None: ...
    def return_port(self, port: int) -> None: ...
    def process_message(self, user: User, mesage: Message) -> None: ...
    def remove_user(self, user: User) -> None: ...
    async def update_userlist(self) -> None: ...
    async def send_message(self) -> None: ...