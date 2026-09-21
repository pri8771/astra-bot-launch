import copy
import json
from pathlib import Path
import unittest
from validate_plan import validate

BASE = json.loads(Path(__file__).with_name('NEXT_ROUND_TASKS.json').read_text())
class PlanTests(unittest.TestCase):
    def setUp(self):
        self.plan = copy.deepcopy(BASE)
    def bad(self):
        self.assertTrue(validate(self.plan))
    def test_valid_graph(self):
        self.assertEqual(validate(self.plan), [])
    def test_duplicate(self):
        self.plan['tasks'].append(copy.deepcopy(self.plan['tasks'][0])); self.bad()
    def test_missing_dependency(self):
        self.plan['tasks'][0]['build_after'] = ['NR-99']; self.bad()
    def test_cycle(self):
        self.plan['tasks'][0]['build_after'] = ['NR-32']; self.bad()
    def test_self_cycle(self):
        self.plan['tasks'][0]['build_after'] = ['NR-01']; self.bad()
    def test_invalid_points(self):
        self.plan['tasks'][0]['points'] = 9; self.bad()
    def test_boolean_points(self):
        self.plan['tasks'][0]['points'] = True; self.bad()
    def test_no_automatic_activation(self):
        self.plan['stage'] = 'ACTIVE'; self.bad()
    def test_no_assignment_override(self):
        self.plan['active_assignment_change'] = True; self.bad()
    def test_no_self_acceptance(self):
        self.plan['tasks'][0]['status'] = 'ACCEPTED'; self.bad()
    def test_full_sha_required(self):
        self.plan['canonical_baseline'] = 'eeb4a39'; self.bad()
    def test_strict_unknown_artifact(self):
        self.assertTrue(validate(self.plan, set()))
    def test_card_missing(self):
        self.assertTrue(validate(self.plan, cards=''))
    def test_card_route_escape(self):
        self.plan['tasks'][0]['card'] = '../outside.md'; self.bad()
    def test_bad_dependency_type(self):
        self.plan['tasks'][0]['build_after'] = [None]; self.bad()
    def test_duplicate_dependency(self):
        self.plan['tasks'][1]['build_after'] = ['NR-01', 'NR-01']; self.bad()
    def test_bad_document_shape(self):
        self.assertTrue(validate([]))
    def test_fixture_reference_universe_only(self):
        # Isolated positive validator test, not an audit of the actual repo registry.
        ids = {x for t in self.plan['tasks'] for x in t['artifact_refs']}
        cards = '\n'.join('## '+t['id']+'\n' for t in self.plan['tasks'])
        self.assertEqual(validate(self.plan, ids, cards), [])

if __name__ == '__main__':
    unittest.main()
