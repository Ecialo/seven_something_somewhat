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

    def test_actions(self):
        with open(self.tests_path) as tests_file:
            tests = yaml.load(tests_file)
        for test in tests:
            yield self.check, test

    def check(self, test):
        unit_A = UNITS[test['A']['unit']]("A")
        unit_A.switch_state()
        summon.send(None, unit=unit_A, cell=test['A']['cell'])

        unit_B = UNITS[test['B']['unit']]("B")
        unit_B.switch_state()
        summon.send(None, unit=unit_B, cell=test['B']['cell'])

        for unit in self.units:
            unit.clear_presumed()
            unit.update_position()

        for actions_struct in test['actions_A']:
            action_class = ACTIONS[actions_struct['action_name']]
            action = action_class(unit_A, **actions_struct['args'])
            if action.pre_check():
                action.apply()
        for actions_struct in test['actions_B']:
            action_class = ACTIONS[actions_struct['action_name']]
            action = action_class(unit_B, **actions_struct['args'])
            if action.pre_check():
                action.apply()
        context = {
            'A': unit_A,
            'B': unit_B,
            'units': self.units,
        }
        for unit in self.units:
            unit.clear_presumed()
            unit.update_position()
        for check in test['checks']:
            check_context = context.copy()
            check_context['cell'] = check['cell']
            expression = check['check']
            result = check['result']
            expression_result = expression.get(check_context)
            result = result.get(context) if isinstance(result, Property) else result
            assert expression_result == result, "{} != {}".format(expression_result, result)