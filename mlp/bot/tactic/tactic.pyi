from typing import List

from ...protocol import Message
from ...unit import Unit


class Tactic:

    def realize(self, unit: Unit) -> List[Message]: ...
