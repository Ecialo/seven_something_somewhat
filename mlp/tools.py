import re
import operator as op
from functools import reduce

import numpy as np

first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def convert(name):
    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()


def dict_merge(a, b):
    d = {}
    d.update(a)
    d.update(b)
    return d


class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    # __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError("dot dict has not attribute {}".format(item))


def rsum(iterable):
    return reduce(op.add, iterable)


def centred(center, layout, R, default=0.0):
    x, y = center
    view = np.ones((2*R + 1, 2*R + 1), dtype='float64')*default

    h, w = layout.shape

    # R = 1
    #    l   x   r
    # t 0,0 0,1 0,2
    # y 1,0 1,1 1,2
    # b 2,0 2,1 2,2

    l = max(0, x - R)
    lv = -min(0, x - R)

    r = min(w, x + R) + 1
    #   [R   c   R)
    rv = 2*R - max(0, x + R + 1 - w) + 1

    print(lv, rv, x + R - w)

    t = max(0, y - R)
    tv = -min(0, y - R)

    b = min(h, y + R) + 1
    bv = 2*R - max(0, y + R + 1 - h) + 1

    view[tv:bv, lv:rv] = layout[t:b, l:r]
    return view
