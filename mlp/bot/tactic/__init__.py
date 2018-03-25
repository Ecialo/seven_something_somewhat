from .approach_and_attack import AttackNearest
from .flee import Flee

ALL_MAJOR_TACTIC = {
    AttackNearest.__name__: AttackNearest,
    Flee.__name__: Flee,
}