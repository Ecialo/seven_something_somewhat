from tornado import (
    tcpserver
)


class LobbyServer(tcpserver.TCPServer):

    async def handle_stream(self, stream, address):
        pass

    async def add_user(self, user):
        pass

    async def remove_user(self, user):
        pass

    async def create_game_node(self):
        pass

    async def deconstruct_game_node(self):
        pass

    async def connect_user_to_game_node(self):
        pass

    async def disconnect_user_fom_game_node(self):
        pass