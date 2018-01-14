import sys
import argparse

from tornado import (
    ioloop
)

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


# main()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit1", default=DEFAULT_UNIT)
    parser.add_argument("--unit2", default=DEFAULT_UNIT)
    parser.add_argument("--strategy1", default=DEFAULT_STRATEGY)
    parser.add_argument("--strategy2", default=DEFAULT_STRATEGY)
    parser.add_argument("--times", type=int, default=1)
    args = parser.parse_args()

    run_episode_logger()
    loop = ioloop.IOLoop.current()
    for i in range(args.times):
        print("Launch {} tournament".format(i))
        tour = TournamentGameSession(
            (args.strategy1, args.unit1),
            (args.strategy2, args.unit2),
        )
        loop.spawn_callback(tour.start)
        loop.start()
    print("DONE")

main()
