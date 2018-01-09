import sys

from tornado import (
    ioloop
)

from .tournament import TournamentGameSession


def main():
    bot1, bot2 = sys.argv[1], sys.argv[2]
    loop = ioloop.IOLoop.current()
    tour = TournamentGameSession(bot1, bot2)
    loop.spawn_callback(tour.start)
    loop.start()
    print("END")


main()
