from functools import partial

import yaml
import blinker

from ..mlp.grid import HexGrid
from ..mlp.replication_manager import MetaRegistry
from ..mlp.loader import load
from ..mlp.actions.property.property import Property

summon = blinker.signal("summon")
revoke = blinker.signal("revoke")
collect_garbage = blinker.signal('collect')

load()

ACTIONS = MetaRegistry()["Action"]
UNITS = MetaRegistry()["Unit"]


class TestAction:

    tests_path = "./tests/action_tests.yaml"
    grid = HexGrid((5, 5))

    def setUp(self):
        self.A = None
        self.B = None
        self.units = []
        summon.connect(self.track_units)

    def tearDown(self):
        summon.disconnect(self.track_units)
        for unit in self.units:
            unit.kill()
        collect_garbage.send()
            # revoke.send(unit=unit, cell=unit.cell)

    def track_units(self, _, unit, cell):
        self.units.append(unit)

    def start_phase(self):
        for unit in self.units:
            unit.launch_triggers(["phase", "start"], unit, unit.context)

    def end_phase(self):
        for unit in self.units:
            unit.launch_triggers(["phase", "end"], unit, unit.context)

    def start_turn(self):
        for unit in self.units:
            unit.refill_action_points()
            unit.launch_triggers(["turn", "start"], unit, unit.context)

    def end_turn(self):
        for unit in self.units:
            unit.launch_triggers(["turn", "end"], unit, unit.context)

    def update(self):
        for unit in self.units:
            unit.clear_presumed()
            unit.update_position()

    def run_phase(self, phase):
        unit_A = self.A
        unit_B = self.B

        for actions_struct in phase['actions_A']:
            action_class = ACTIONS[actions_struct['action_name']]
            action = action_class(unit_A, **actions_struct['args'])
            if action.pre_check():
                action.apply()
        for actions_struct in phase['actions_B']:
            action_class = ACTIONS[actions_struct['action_name']]
            action = action_class(unit_B, **actions_struct['args'])
            action.apply()

    def test_actions(self):
        with open(self.tests_path) as tests_file:
            tests = yaml.load(tests_file)
        for test in tests:
            name = test.get('name')
            f = partial(self.check, test)
            f.description = name
            yield f,

    def check(self, test):
        self.setUp()
        unit_A = UNITS[test['A']['unit']]("A")
        unit_A.switch_state()
        summon.send(None, unit=unit_A, cell=test['A']['cell'])

        unit_B = UNITS[test['B']['unit']]("B")
        unit_B.switch_state()
        summon.send(None, unit=unit_B, cell=test['B']['cell'])

        self.A = unit_A
        self.B = unit_B

        self.update()

        if 'turns' in test:
            for turn in test['turns']:
                self.start_turn()
                for phase in turn:
                    self.start_phase()
                    self.run_phase(phase)
                    self.end_phase()
                    self.update()
                self.end_turn()
                self.update()
        else:

            self.start_turn()
            self.start_phase()

            self.run_phase(test)

            self.end_phase()
            self.end_turn()

            self.update()

        context = {
            'A': unit_A,
            'B': unit_B,
            'units': self.units,
        }
        for check in test['checks']:
            check_context = context.copy()
            check_context['cell'] = check['cell']
            expression = check['check']
            result = check['result']
            expression_result = expression.get(check_context)
            result = result.get(context) if isinstance(result, Property) else result
            assert expression_result == result, "{} != {}".format(expression_result, result)
        self.tearDown()
