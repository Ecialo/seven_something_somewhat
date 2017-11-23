from typing import (
    List,
    Dict,
    Union,
    BinaryIO,
)

from tornado import (
    queues,
)

from ..commands.command import Command
from ..serialization import CreateOrUpdateTag

class ReplayHandler:

    replay_path: str
    is_alive: bool
    queue: queues.Queue
    # replay: List[Dict[str, Union[List[CreateOrUpdateTag], List[Command]]]]
    replay: BinaryIO

    def __init__(self, session_name: str) -> None: ...
    async def write_step(self) -> None: ...
    async def dump_replay(self) -> None: ...
    @staticmethod
    def make_replay_path(session_name: str) -> str: ...