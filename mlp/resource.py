from .bind_widget import bind_widget
from .replication_manager import MetaRegistry
from .freezable import Freezable

RESOURCES = MetaRegistry()['Resource']
ResourceMeta = MetaRegistry().make_registered_metaclass("Resource")


class Resource(Freezable, metaclass=ResourceMeta):

    hooks = ['change']

    def dump(self):
        return self.value

    def load(self, v):
        self.value = v

    def copy(self):
        pass

    def change(self):
        """
        Используется для передачи сигнала об обновлении виджетов
        """
        pass


@bind_widget("NumericResource")
class NumericResource(Resource):

    name = "numeric"

    def __init__(self, name, initial, min=0, max=None):
        self.name_ = name
        self._current = initial
        self.min = min
        self.max = max or initial

    @property
    def value(self):
        return self._current

    @value.setter
    def value(self, v):
        self._current = max(self.min, min(v, self.max))
        self.change()

    def copy(self):
        return NumericResource(self.name_, self._current, self.min, self.max)

    def __repr__(self):
        return "{}: {}/{}".format(self.name_, self._current, self.max)

    # def dump(self):
    #     return self.value
    #
    # def load(self, v):
    #     self.value = v


@bind_widget("StringResource")
class OptionResource(Resource):

    name = "option"

    def __init__(self, name, initial, options):
        self.name_ = name
        self._current = initial
        self.options = options

    @property
    def value(self):
        return self._current

    @value.setter
    def value(self, v):
        if v in self.options:
            self._current = v
            self.change()
        else:
            raise AttributeError("value not in {}".format(self.options))

    def copy(self):
        return OptionResource(self.name_, self._current, self.options)


@bind_widget("BooleanResource")
class FlagResource(Resource):

    name = "flag"

    def __init__(self, name, initial):
        self.name_ = name
        self._current = initial

    @property
    def value(self):
        return self._current

    @value.setter
    def value(self, v):
        if isinstance(v, bool):
            self._current = v
            self.change()

    def copy(self):
        return FlagResource(self.name_, self._current)


RESOURCE_TABLE = {
    int: NumericResource,
    bool: FlagResource,
}


def resource_constructor(loader, node):
    r_s = loader.construct_mapping(node)
    name = r_s.pop("type")
    resource = RESOURCES[name](**r_s)
    return resource


RESOURCE_TAG = "!res"
