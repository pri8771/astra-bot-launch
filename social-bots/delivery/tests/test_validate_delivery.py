"""Offline tests of the planning validator, not Social Bots runtime acceptance."""
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("validate_delivery", ROOT / "validate_delivery.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

class DeliveryValidationTests(unittest.TestCase):
    def setUp(self):
        self.t = v.read_object(ROOT / "TASKS.json")
        self.g = v.read_object(ROOT / "GATES.json")
        self.r = v.read_object(ROOT / "RECONCILIATION.json")
    def check(self):
        return v.validate_data(self.t, self.g, self.r, ROOT)
    def invalid(self, contains):
        self.assertTrue(any(contains in e for e in self.check()["errors"]), self.check())
    def test_valid_package(self):
        r = v.validate_package(ROOT)
        self.assertTrue(r["passed"])
        self.assertEqual((r["task_count"], r["milestone_count"], r["reconciliation_count"]), (31, 27, 10))
    def test_validation_does_not_claim_runtime_or_live_execution(self):
        r = v.validate_package(ROOT)
        self.assertFalse(r["production_tests_run"])
        self.assertFalse(r["live_tests_run"])
        self.assertFalse(r["artifact_acceptance_changed"])
        self.assertFalse(r["repo_checks_run"])
    def test_duplicate_task(self):
        self.t["tasks"].append(copy.deepcopy(self.t["tasks"][0])); self.invalid("duplicate IDs")
    def test_missing_dependency(self):
        self.t["tasks"][0]["build_requires"] = ["C99"]; self.invalid("missing dependency")
    def test_self_cycle(self):
        self.t["tasks"][0]["build_requires"] = ["C01"]; self.invalid("cycle")
    def test_two_node_cycle(self):
        self.t["tasks"][0]["build_requires"] = ["C02"]; self.invalid("cycle")
    def test_duplicate_dependency(self):
        self.t["tasks"][1]["build_requires"] = ["C01", "C01"]; self.invalid("duplicate dependency")
    def test_invalid_dependency_type(self):
        self.t["tasks"][0]["build_requires"] = "C02"; self.invalid("invalid dependency")
    def test_invalid_task_id(self):
        self.t["tasks"][0]["id"] = "garbage"; self.invalid("invalid task ID")
    def test_work_must_remain_planning_only(self):
        self.t["tasks"][0]["status"] = "ACCEPTED"; self.invalid("planning-only")
    def test_large_task_requires_split(self):
        self.t["tasks"][0]["story_points"] = 5; self.invalid("SP2")
    def test_bool_not_story_point(self):
        self.t["tasks"][0]["story_points"] = True; self.invalid("SP2")
    def test_missing_input(self):
        self.t["tasks"][0]["inputs"] = []; self.invalid("inputs")
    def test_missing_output(self):
        self.t["tasks"][0]["outputs"] = []; self.invalid("outputs")
    def test_missing_tests(self):
        self.t["tasks"][0]["test_cases"] = ["one"]; self.invalid("three concrete tests")
    def test_unknown_gate(self):
        self.t["tasks"][0]["external_gates"] = ["AUTO_APPROVED"]; self.invalid("unknown external gate")
    def test_unknown_scope(self):
        self.t["tasks"][0]["evidence_scopes"] = ["ALL_DONE"]; self.invalid("unknown evidence scope")
    def test_missing_contract_file(self):
        self.t["tasks"][0]["contract_sections"] = ["missing.md"]; self.invalid("missing/escaping")
    def test_contract_path_traversal(self):
        self.t["tasks"][0]["contract_sections"] = ["../../secret.txt"]; self.invalid("missing/escaping")
    def test_missing_milestone(self):
        self.g["milestones"].pop(); self.invalid("V0.4 through V3.0")
    def test_missing_predecessor(self):
        self.g["milestones"][3]["previous_version"] = "V0.3"; self.invalid("sequential product predecessor")
    def test_fixture_cannot_satisfy_operational_gate(self):
        self.g["milestones"][0]["live_scopes"] = ["OFFLINE_FIXTURE"]; self.invalid("fixture cannot")
    def test_v07_requires_native_scheduler(self):
        self.g["milestones"][3]["live_scopes"] = ["REAL_PROCESS"]; self.invalid("native scheduler")
    def test_v09_requires_public_authorization(self):
        self.g["milestones"][5]["external_gates"] = ["G-MEASURE"]; self.invalid("public authorization")
    def test_no_auto_apply_reconciliation(self):
        self.r["apply_automatically"] = True; self.invalid("not apply automatically")
    def test_read_object_rejects_non_object(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "x.json"; p.write_text("[]")
            with self.assertRaises(ValueError): v.read_object(p)
    def test_read_object_rejects_malformed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "x.json"; p.write_text("{bad")
            with self.assertRaises(ValueError): v.read_object(p)
    def test_optional_repository_check_detects_missing_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); sb=root/"social-bots"; sb.mkdir()
            (sb/"ARTIFACT_INDEX.json").write_text(json.dumps({"artifacts":[]}))
            r=v.check_repository(root,self.t,self.g)
            self.assertTrue(any("missing referenced artifact" in e for e in r["errors"]))
    def test_registry_graph_cycle_is_reported(self):
        rows=[{"id":"A","depends_on":["B"]},{"id":"B","depends_on":["A"]}]
        self.assertTrue(any("cycle" in e for e in v.graph_errors(rows,"depends_on")))
    def test_gate_document_is_not_authorization(self):
        self.g["status"]="AUTHORIZED"; self.invalid("must not imply authorization")

if __name__ == "__main__":
    unittest.main()
