import io

import cbor2
from cbor2.types import CBORTag

from .commands.command import Command
from .actions.base.status import (
    Status,
    STATUSES,
)
from .actions.new_action import Action
from .grid import Cell
from .protocol import *
from .replication_manager import (
    GameObjectRegistry,
    # ActionsRegistry,
    GameObject,
    MetaRegistry,
)


class RefTag(CBORTag):

    def __init__(self, obj):
        super().__init__(40, obj.id_)


class RefDecoder:

    registry = GameObjectRegistry()

    def __call__(self, decoder, id_, fp, shareable_index=None):
        return self.registry[id_]


def encode_game_object(encoder, game_object, fp):
    encoder.encode_custom_tag(RefTag(game_object), fp)


class RemoteCallTag(CBORTag):
    def __init__(self, method):
        rem_call_struct = {
            'obj': RefTag(method.__self__),
            'name': method.__name__,
        }
        super().__init__(41, rem_call_struct)


def remote_call_decoder(decoder, rem_call_struct, fp, shareable_index=None):
    return getattr(rem_call_struct['obj'], rem_call_struct['name'])


def remote_call(method, *args, **kwargs):
    struct = {
        'message_type': (message_type.GAME, game_message.CALL),
        'payload': {
            'method': RemoteCallTag(method),
            'args': args,
            'kwargs': kwargs,
        }
    }
    return struct


class ActionTag(CBORTag):

    def __init__(self, action):
        super().__init__(42, action.dump())


class ActionDecoder:

    registry = MetaRegistry()["Action"]

    def __call__(self, decoder, action_struct, fp, shareable_index=None):
        print("\n\nACTION STRUCT")
        # print(action_struct, self.registry.actions)
        # action = action_struct['action']
        action_name = action_struct.pop('name')
        return self.registry[action_name](**action_struct)


def encode_action(encoder, action, fp):
    encoder.encode_custom_tag(ActionTag(action), fp)


class CreateOrUpdateTag(CBORTag):

    def __init__(self, obj):
        super().__init__(43, obj.dump())


class CreateOrUpdateDecoder:

    registry = GameObjectRegistry()

    def __call__(self, decoder, obj_struct, fp, shareable_index=None):
        return self.registry.load_obj(obj_struct)


def remote_action_append(action):
    msg_struct = {
        "message_type": (message_type.GAME, game_message.ACTION_APPEND),
        "payload": {
            'action': action
        }
    }
    return msg_struct


def remote_action_remove(action):
    unit = action.owner
    # action_index = unit.current_action_bar.actions.index(action)
    msg_struct = {
        "message_type": (message_type.GAME, game_message.ACTION_REMOVE),
        "payload": {
            # 'action_index': action_index,
            'unit': unit,
        }
    }
    return msg_struct


def encode_cell(encoder, cell, fp):
    encoder.encode_custom_tag(CellTag(cell), fp)


class CellTag(CBORTag):

    def __init__(self, obj):
        super().__init__(44, obj.pos)


class CellDecoder:

    registry = GameObjectRegistry()

    def __call__(self, decoder, cell_pos, fp, shareable_index=None):
        return self.grid[tuple(cell_pos)]

    @property
    def grid(self):
        return self.registry.categories['Grid'][0]


class StatusTag(CBORTag):

    def __init__(self, obj):
        super().__init__(45, obj.dump())


def status_decoder(decoder, status_struct, fp, shareable_index=None):
    s_name = status_struct.pop("name")
    return STATUSES[s_name](**status_struct['params'])


# @cbor2.shareable_encoder
def encode_status(encoder, status, fp):
    encoder.encode_custom_tag(StatusTag(status), fp)


class CommandTag(CBORTag):

    def __init__(self, obj):
        super().__init__(46, obj.dump())


def encode_command(encoder, command, fp):
    encoder.encode_custom_tag(CommandTag(command), fp)


class CommandDecoder:

    registry = MetaRegistry()["Command"]

    def __call__(self, decoder, command_struct, fp, shareable_index=None):
        print("\n\nACTION STRUCT")
        # print(action_struct, self.registry.actions)
        # action = action_struct['action']
        command_name = command_struct.pop('name')
        return self.registry[command_name](**command_struct)


class PurgeableCBOREncoder(cbor2.CBOREncoder):

    def purge(self):
        self.shared_containers.clear()

mlp_decoder = cbor2.CBORDecoder(semantic_decoders={
    40: RefDecoder(),
    41: remote_call_decoder,
    42: ActionDecoder(),
    43: CreateOrUpdateDecoder(),
    44: CellDecoder(),
    45: status_decoder,
    46: CommandDecoder(),
})
mlp_encoder = PurgeableCBOREncoder(
    value_sharing=True,
    encoders={
        Cell: encode_cell,
        Action: encode_action,
        GameObject: encode_game_object,
        Status: encode_status,
        Command: encode_command,
    }
)


def mlp_dump(obj, fp):
    mlp_encoder.encode(obj, fp)


def mlp_load(fp):
    return mlp_decoder.decode(fp)


def mlp_dumps(obj):
    buf = io.BytesIO()
    mlp_encoder.encode(obj, buf)
    return buf.getvalue()


def mlp_loads(payload):
    buf = io.BytesIO(payload)
    return mlp_decoder.decode(buf)
