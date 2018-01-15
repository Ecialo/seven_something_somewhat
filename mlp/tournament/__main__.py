import argparse
import multiprocessing as mlp

from tornado import (
    ioloop,
    tcpclient,
)

from ..protocol import SEPARATOR
from .tournament import TournamentGameSession
from .episode_logger import run_episode_logger


DEFAULT_UNIT = "Dog"
# DEFAULT_STRATEGY = "Random"
DEFAULT_STRATEGY = "AttackNearest"

# def main():
#     bot1, bot2 = sys.argv[1], sys.argv[2]
#     loop = ioloop.IOLoop.current()
#     tour = TournamentGameSession(bot1, bot2)
#     loop.spawn_callback(tour.start)
#     loop.start()
#     print("END")


async def terminate_logger():
    client = tcpclient.TCPClient()
    io = await client.connect("localhost", 66613)
    await io.write(SEPARATOR)
    ioloop.IOLoop.current().stop()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit1", default=DEFAULT_UNIT)
    parser.add_argument("--unit2", default=DEFAULT_UNIT)
    parser.add_argument("--strategy1", default=DEFAULT_STRATEGY)
    parser.add_argument("--strategy2", default=DEFAULT_STRATEGY)
    parser.add_argument("--times", type=int, default=1)
    args = parser.parse_args()

    logger_process = mlp.Process(
        target=run_episode_logger,
        name="EpisodeLogger"
    )
    logger_process.start()

    loop = ioloop.IOLoop.current()
    for i in range(args.times):
        print("Launch {} tournament".format(i))
        tour = TournamentGameSession(
            (args.strategy1, args.unit1),
            (args.strategy2, args.unit2),
        )
        loop.spawn_callback(tour.start)
        loop.start()
    loop.spawn_callback(terminate_logger)
    loop.start()
    print("DONE")

main()
