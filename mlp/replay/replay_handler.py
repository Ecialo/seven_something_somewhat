from tornado import (
    queues,
    ioloop,
)

from ..serialization import (
    mlp_dumps,
    mlp_dump,
)

REPLAY_ROOT = './replays/'


class ReplayHandler:

    def __init__(self, session_name):
        self.is_alive = True

        self.queue = queues.Queue()
        self.replay = []
        self.replay_path = self.make_replay_path(session_name)
        # self.replay = open(self.replay_path, 'wb')
        ioloop.IOLoop.current().spawn_callback(self.write_step)

    async def write_step(self):
        # print("start logger")
        while self.is_alive:
            res = await self.queue.get()
            state_payload, command_payload = res
            # print("WORK")
            # self.replay.writelines([mlp_dumps(state_payload), mlp_dumps(command_payload)])
            # self.replay.writelines([mlp_dumps(state_payload), mlp_dumps(command_payload)])
            # self.replay.write(mlp_dumps(state_payload) + b'\n')
            # self.replay.write(mlp_dumps(command_payload) + b'\n')
            self.replay.append({
                'state': mlp_dumps(state_payload),
                'commands': mlp_dumps(command_payload),
            })
            self.queue.task_done()

    async def dump_replay(self):
        # print("AWAIT queue")
        # print(self.queue)
        await self.queue.join()
        # print("DONE")
        # self.replay.close()
        with open(self.replay_path, 'wb') as replay:
            mlp_dump(self.replay, replay)
        self.is_alive = False

    @staticmethod
    def make_replay_path(session_name):
        return REPLAY_ROOT + session_name + ".re"
