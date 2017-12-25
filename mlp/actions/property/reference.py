from .property import Property


class Reference(Property):

    def __init__(self, name, struct, registry):
        self.name = name
        self.struct = struct
        self.registry = registry

    def get(self, context=None):
        return self.registry[self.name](**self.struct)


class ReferenceList(Property):

    def __init__(self, references):
        if isinstance(references, ReferenceList):
            self.references = references.references
        else:
            self.references = references if isinstance(references, list) else [references]

    def get(self, context=None):
        print("GET LIST")
        v = [(a.get() if isinstance(a, Reference) else a) for a in self.references]
        print(v)
        return v
