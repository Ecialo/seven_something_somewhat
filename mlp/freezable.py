class Freezable:

    def freeze(self):
        """
        Create checkpoint and start track mutations
        """

    def unfreeze(self):
        """
        Drop all checkpoints and stop track mutations
        """

    def rollback(self):
        """
        Rollback to last checkpoint
        """
