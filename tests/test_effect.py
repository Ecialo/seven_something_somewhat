from collections import ChainMap
from functools import partial

import yaml
import blinker

from ..mlp.grid import Cell
from ..mlp.unit import UNITS
from ..mlp.loader import load
from ..mlp.grid import HexGrid

collect_garbage = blinker.signal('collect')
DUMMY = 'Dummy'
A = 'A'
B = 'B'

load()


class TestEffect:

    tests_path = "./tests/effect_tests.yaml"

    def setUp(self):
        self.grid = HexGrid((5, 5))
        self.source = self.grid[0, 0]
        self.author = UNITS[DUMMY](A)
        self.author.place_in(self.source)
        self.author.switch_state()
        self.target = self.grid[1, 1]
        self.victim = UNITS[DUMMY](B)
        self.victim.place_in(self.target)
        self.victim.switch_state()
        self.context = ChainMap({
            'owner': self.author,
            'source': self.source,
            'victim': self.victim,
        })

    def tearDown(self):
        self.author.kill()
        self.victim.kill()
        collect_garbage.send()

    def test_effects(self):
        with open(self.tests_path) as tests_file:
            tests = yaml.load(tests_file)
        for test in tests:
            name = test.get('name')
            f = partial(self.check, [effect.get() for effect in test['effects']], test['check'], test.get('result'))
            f.description = name
            yield f,

    def check(self, effects, expression, result=None):
        self.setUp()
        for effect in effects:
            effect.apply([self.target], self.context)
        if result:
            assert expression.get(self.context) == result, "{} != {}".format(
                expression.get(self.context),
                result,
            )
        else:
            assert expression.get(self.context)
        self.tearDown()