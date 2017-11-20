from tornado import (
    queues
)

from ..serialization import (
    mlp_dump,
)

REPLAY_ROOT = './replays/'


class ReplayHandler:

    def __init__(self, session_name):
        self.is_alive = True

        self.queue = queues.Queue()
        self.replay = []
        self.replay_path = self.make_replay_path(session_name)

    async def write_step(self):
        while self.is_alive:
            state_payload, command_payload = self.queue.get()
            self.replay.append({
                'state': state_payload,
                'commands': command_payload,
            })
            self.queue.task_done()

    async def dump_replay(self):
        await self.queue.join()
        with open(self.replay_path, 'wb') as replay:
            mlp_dump(self.replay, replay)
        self.is_alive = False

    @staticmethod
    def make_replay_path(session_name):
        return REPLAY_ROOT + session_name + ".re"
