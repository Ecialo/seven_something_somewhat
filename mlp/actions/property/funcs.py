from .property import Property


class Func(Property):

    def __init__(self, seq):
        self.obj = seq[0]
        self.func_name = seq[1]
        self.args = seq[2::]

    def get(self, context):
        print(self, self.obj.get(context))
        args = [(arg.get(context) if isinstance(arg, Property) else arg) for arg in self.args]
        return getattr(self.obj.get(context), self.func_name)(*args)

    def __repr__(self):
        return "Call {}.{} with {}".format(self.obj, self.func_name, self.args)


def func_constructor(loader, node):
    seq = loader.construct_sequence(node)
    return Func(seq)


FUNC_TAG = "!call"
