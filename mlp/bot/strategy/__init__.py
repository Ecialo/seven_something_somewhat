from .fixed_tactic_strategy import FixedTacticStrategy
from .random_tactic_strategy import RandomTacticStrategy
ALL_STRATEGIES = {
    FixedTacticStrategy.__name__: FixedTacticStrategy,
    RandomTacticStrategy.__name__: RandomTacticStrategy,
}