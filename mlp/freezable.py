from abc import (
    ABC,
    abstractmethod,
)


class Freezable(ABC):

    @abstractmethod
    def freeze(self):
        """
        Create checkpoint and start track mutations
        """

    @abstractmethod
    def unfreeze(self):
        """
        Drop all checkpoints and stop track mutations
        """

    @abstractmethod
    def rollback(self):
        """
        Rollback to last checkpoint
        """
