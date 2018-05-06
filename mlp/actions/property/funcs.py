from .property import Property


class Func(Property):

    def __init__(self, seq):
        self.obj = seq[0]
        self.func_name = seq[1]
        self.args = seq[2::]

    def get(self, context):
        args = [(arg.get(context) if isinstance(arg, Property) else arg) for arg in self.args]
        return getattr(self, self.func_name)(*args)


def func_constructor(loader, node):
    pass


FUNC_TAG = "!call"