from tornado import (
    iostream,
    queues,
)

class User:
    def __init__(self, username: str, stream: iostream.IOStream) -> None: ...
    name: str
    _stream: iostream.IOStream
    queue: queues.Queue()
    is_alive: bool = True
    async def await_message(self) -> None: ...
    async def disconnect(self) -> None: ...
    async def send_message(self) -> None: ...
