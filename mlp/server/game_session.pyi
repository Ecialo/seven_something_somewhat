from typing import (
    Optional,
    Dict,
)
import multiprocessing as mlp

from tornado import (
    iostream,
)

from .user import User


class GameSession:

    _stream: iostream.IOStream
    uid: str
    session_name: str
    users: Dict[str, Optional[User]]
    port: int
    _game_process: mlp.Process
    is_alive: bool
    _lock: mlp.Semaphore

    def __init__(self, port: int) -> None: ...
    def __contains__(self, item: User) -> bool: ...
    def is_full(self) -> bool: ...
    def is_empty(self) -> bool: ...
    def add_user(self, user: User, character: str) -> None: ...
    def remove_user(self, user: User) -> None: ...
    def start(self) -> None: ...
    async def shutdown(self) -> None: ...
    async def await_message(self) -> None: ...
    async def send_terminate_signal(self) -> None: ...

class UserGameSession(GameSession):
    pass

class AIGameSession(GameSession):
    pass