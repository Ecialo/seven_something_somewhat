class Namespace:

    def __init__(self, **consts):
        for const_name, const_val in consts.items():
            setattr(self, const_name, const_val)

    def __repr__(self):
        return "\n".join(map(lambda name_val: "{0} = {1}".format(name_val[0], name_val[1]), self.items()))

    def values(self):
        return self.__dict__.itervalues()

    def names(self):
        return self.__dict__.iterkeys()

    def items(self):
        return self.__dict__.items()


class Enum(Namespace):
    def __init__(self, *consts):
        for const_name, const_val in zip(consts, range(len(consts))):
            setattr(self, const_name, const_val)

ALL = 0

message_type = Enum(
    "CHAT",
    "GAME",
    "LOBBY",
)

game_message = Enum(
    # "CREATE",
    "UPDATE",
    "CALL",
    "ACTION_APPEND",
    "ACTION_REMOVE",
    "READY",
    "COMMAND",
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

SEPARATOR = b"|||"
