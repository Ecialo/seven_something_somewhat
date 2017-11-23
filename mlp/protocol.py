from typing import (
    Dict,
    Any,
    Tuple,
    Callable,
)


class Namespace:

    def __init__(self, **consts):
        for const_name, const_val in consts.items():
            setattr(self, const_name, const_val)

    def __repr__(self):
        return "\n".join(map(lambda name_val: "{0} = {1}".format(name_val[0], name_val[1]), self.items()))

    def values(self):
        return self.__dict__.values()

    def names(self):
        return self.__dict__.keys()

    def items(self):
        return self.__dict__.items()


class Enum(Namespace):
    def __init__(self, *consts):
        for const_name, const_val in zip(consts, range(len(consts))):
            setattr(self, const_name, const_val)


Message = Dict[str, Any]
Handler = Dict[Tuple[int, int], Callable]

ALL = 0

message_type = Enum(
    "CHAT",
    "GAME",
    "LOBBY",
    "CONTEXT",
)

game_message = Enum(
    "UPDATE",
    "CALL",
    "ACTION_APPEND",
    "ACTION_REMOVE",
    "READY",
    "COMMAND",
    "GAME_OVER",
)

lobby_message = Enum(
    "ACCEPT",
    "REFUSE",
    "JOIN",
    "LEAVE",
    "CREATE_SESSION",
    "JOIN_SESSION",
    "FIND_SESSION",
    "LEAVE_SESSION",
    "ONLINE",
    "UPDATE_SESSIONS",
)
chat_message = Enum(
    "BROADCAST"
)

context_message = Enum(
    "READY",
    "JOIN",
    "TERMINATE",
)

SEPARATOR = b"|||"
