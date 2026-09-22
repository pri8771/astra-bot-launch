"""V1.7 C07 — unpublished experiments are registered PROSPECTIVE.

Registration happens before any publication, so there is no baseline
measurement, no outcome, no decision and no confidence at that moment. A number
that was never measured is a fabricated performance record: the registry
refuses it, the decision loop never writes one, and the hypothesis is stored
with UNKNOWN (None) confidence until real post-window evidence exists.
ENGINEERING-ONLY: temp homes, deterministic provider, no model call.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import decision, paths, pipeline, research  # noqa: E402
from runtime.jsonstore import read_json  # noqa: E402
from runtime.state import PersonaState  # noqa: E402


def seed(bot):
    research.capture(bot, research.Signal.make(
        "Water tension demo", "A leaf floats because of surface tension.", "unit-test",
        "https://example.org/leaf", "fixture", ["nature"]))


def _exp(**over):
    base = dict(experiment_id="exp-fixture", bot="social-a", persona="social-a", platform="x",
                hypothesis="h", baseline=pipeline.prospective_baseline("saves"),
                intervention="i", success_metric="saves", stop_criteria="s",
                observation_window_hours=48)
    base.update(over)
    return pipeline.Experiment(**base)


class ProspectiveRegistrationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.prior = os.environ.get("SBOTS_HOME")
        os.environ["SBOTS_HOME"] = self.tmp

    def tearDown(self):
        if self.prior is None:
            os.environ.pop("SBOTS_HOME", None)
        else:
            os.environ["SBOTS_HOME"] = self.prior

    def test_cycle_registers_a_prospective_experiment_with_no_fabricated_fields(self):
        seed("social-a")
        rec = decision.run_cycle("social-a", "social-a")
        self.assertEqual(rec["outcome"], "candidate_created")
        exp_id = rec["execute"]["experiment_id"]
        data = read_json(paths.experiments_dir("social-a") / f"{exp_id}.json")
        self.assertEqual(data["status"], pipeline.PROSPECTIVE)
        self.assertIsNone(data["baseline"]["value"])
        self.assertEqual(data["baseline"]["status"], pipeline.NOT_MEASURED)
        self.assertEqual(data["baseline"]["metric"], data["success_metric"])
        self.assertIsNone(data["result"])
        self.assertIsNone(data["decision"])
        self.assertIsNone(data["confidence"])
        self.assertIsNone(data["window"]["opens_at"])
        self.assertEqual(pipeline.validate_prospective(data), [])
        # LEARN records no number and says so.
        self.assertIsNone(rec["learn"]["confidence"])
        self.assertEqual(rec["learn"]["status"], pipeline.PROSPECTIVE)
        hyp = PersonaState.load("social-a", "social-a").get_hypothesis(rec["learn"]["hypothesis_id"])
        self.assertIsNone(hyp["confidence"])
        self.assertEqual(hyp["status"], "PROSPECTIVE")
        self.assertTrue(any("PROSPECTIVE" in e for e in hyp["evidence"]))

    def test_register_refuses_fabricated_baseline_outcome_or_confidence(self):
        cases = {
            "baseline value without provenance": {"baseline": {"metric": "saves", "value": 12}},
            "legacy placeholder baseline": {"baseline": {"metric": "saves",
                                                         "value": "unknown-pre-post"}},
            "result before publication": {"result": {"lift": 1.0}},
            "confidence before evidence": {"confidence": 0.5},
            "decision before evidence": {"decision": "continue"},
            "non-prospective status": {"status": "CLOSED"},
            "window already open": {"window": {"opens_at": "2026-09-22T00:00:00Z",
                                               "closes_at": None}},
            "zero-hour window": {"observation_window_hours": 0},
        }
        for name, over in cases.items():
            with self.subTest(case=name):
                with self.assertRaises(pipeline.ExperimentRegistrationError):
                    pipeline.register_experiment(_exp(**over))
        self.assertEqual(list(paths.experiments_dir("social-a").glob("*.json")), [])

    def test_a_measured_baseline_needs_provenance(self):
        measured = {"metric": "saves", "value": 12, "status": pipeline.MEASURED,
                    "measured_at": "2026-09-21T00:00:00Z", "source": "analytics:fixture-window"}
        path = pipeline.register_experiment(_exp(baseline=measured))
        self.assertTrue(path.is_file())
        self.assertEqual(read_json(path)["baseline"]["value"], 12)

    def test_empty_or_unmeasured_baseline_is_accepted(self):
        pipeline.register_experiment(_exp(experiment_id="exp-a", baseline={}))
        pipeline.register_experiment(_exp(experiment_id="exp-b"))
        self.assertEqual(len(list(paths.experiments_dir("social-a").glob("exp-*.json"))), 2)

    def test_hypothesis_confidence_is_unknown_until_evidenced(self):
        ps = PersonaState.load("social-a", "social-a")
        ps.upsert_hypothesis("h1", "statement", None, ["registered prospective"])
        h = ps.get_hypothesis("h1")
        self.assertIsNone(h["confidence"])
        self.assertEqual(h["status"], "PROSPECTIVE")
        ps.upsert_hypothesis("h1", "statement", 0.7, ["window closed: observed lift"])
        h = ps.get_hypothesis("h1")
        self.assertEqual((h["confidence"], h["status"]), (0.7, "EVIDENCED"))
        self.assertEqual(h["evidence"], ["registered prospective", "window closed: observed lift"])


if __name__ == "__main__":
    unittest.main()
