from random import choice

from .tactic import Tactic
from ...serialization import remote_action_append


class RandomWalkTactic(Tactic):

    def realize(self, unit):
        req_action = None
        for action in unit.action_bar:
            if action.name == "Move":
                req_action = action
                break
        if not req_action.check():
            return []
        setup = req_action.setup_fields
        av_cells = None
        for setup_struct in setup:
            if setup_struct['name'] == 'path':
                av_cells = setup_struct['cursor_params'][0]
                # path = setup_struct['cursor_params'][1]
                break
        context = req_action.context
        if av_cells:
            cells = av_cells.get(context)
            targ_cell = choice(cells)
            action_to_append = req_action.copy()
            try:
                next(action_to_append.setup({'path': targ_cell}))
            except StopIteration:
                pass
            # action_to_append.clear()
            return [remote_action_append(action_to_append)]
        else:
            return []

