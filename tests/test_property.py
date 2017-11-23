import yaml
import io

from ..mlp.loader import load

load()


class TestProperty:

    def setUp(self):
        self.context = {
            'iterable': [1, 2, 3]
        }

    def test_index(self):
        prop = yaml.load(io.StringIO("!prop iterable[0]"))
        # print(prop)
        assert prop.get(self.context) == 1

    def test_negative_index(self):
        prop = yaml.load(io.StringIO("!prop iterable[-1]"))
        # print(prop)
        assert prop.get(self.context) == 3
