from tornado import (
    queues,
    ioloop,
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

        ioloop.IOLoop.current().spawn_callback(self.write_step)

    async def write_step(self):
        print("start logger")
        while self.is_alive:
            res = await self.queue.get()
            state_payload, command_payload = res
            print("WORK")
            self.replay.append({
                'state': state_payload,
                'commands': command_payload,
            })
            self.queue.task_done()

    async def dump_replay(self):
        print("AWAIT queue")
        print(self.queue)
        await self.queue.join()
        print("DONE")
        with open(self.replay_path, 'wb') as replay:
            mlp_dump(self.replay, replay)
        self.is_alive = False

    @staticmethod
    def make_replay_path(session_name):
        return REPLAY_ROOT + session_name + ".re"
