import blinker

presume = blinker.signal("presume")
forget = blinker.signal("forget")


class Tactic:

    def realize(self, unit):
        pass

    def search_in_aoe(self, action, unit):
        pass

    def presume(self, actions):
        pass

    def forget(self):
        pass
