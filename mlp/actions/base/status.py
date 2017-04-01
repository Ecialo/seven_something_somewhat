class Status:

    name = None

    def __init__(self, source=None, **kwargs):
        # pass
        self.source = source

    def configure(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    def on_add(self, target):
        pass

    def on_remove(self, target):
        pass

    def dump(self):
        return {
            "name": self.name,
            "source": self.source,
        }

    def __repr__(self):
        return "Status {}".format(self.name)

    def copy(self):
        return self.__class__(**vars(self))

STATUSES = {}