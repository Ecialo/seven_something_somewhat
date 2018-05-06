import yaml
import io
from textwrap import dedent

from ..mlp.loader import load
from ..mlp.grid import (
    HexGrid,
    HexCell,
)

load()


class TestProperty:

    def setUp(self):
        self.grid = HexGrid((5, 5))
        self.context = {
            'iterable': [1, 2, 3],
        }

    def test_index(self):
        prop = yaml.load(io.StringIO("!prop iterable[0]"))
        # print(prop)
        assert prop.get(self.context) == 1

    def test_negative_index(self):
        prop = yaml.load(io.StringIO("!prop iterable[-1]"))
        # print(prop)
        assert prop.get(self.context) == 3

    def test_area_func(self):
        Y = dedent("""
        !call
        - !area
            name: Line
            source: !cell [0, 0]
            target: !cell [1, 1]
            length: 2
        - is_empty
        """)
        res = yaml.load(io.StringIO(Y))
        assert res.get(self.context)
