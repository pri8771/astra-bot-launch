"""SB-V15-001 — autonomous experiment lifecycle acceptance tests."""
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import experiment_engine as ee  # noqa: E402


def _design(metric="save", **kw):
    return ee.design("social-a", "social-a", hypothesis="H",
                     baseline={metric: 10.0}, intervention="new-hook",
                     primary_metric=metric, min_observation_hours=24.0,
                     stop_criteria={"min_effect": 1.0, "direction": "increase"}, **kw)


class ExperimentEngineTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp

    def test_cannot_close_before_window(self):
        exp = ee.start(_design(), now=datetime(2026, 1, 1, tzinfo=timezone.utc))
        early = datetime(2026, 1, 1, 5, tzinfo=timezone.utc)  # 5h < 24h
        self.assertFalse(ee.can_close(exp, now=early))
        with self.assertRaises(ValueError):
            ee.close(exp, {"save": 20.0}, now=early)

    def test_can_close_after_window(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        exp = ee.start(_design(), now=start)
        later = start + timedelta(hours=25)
        exp = ee.close(exp, {"save": 20.0}, now=later)
        self.assertEqual(exp.status, ee.CLOSED)
        self.assertEqual(exp.outcome, ee.SUCCESS)
        self.assertEqual(exp.result["effect_size"], 10.0)

    def test_safety_stop_closes_early(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        exp = ee.start(_design(), now=start)
        early = start + timedelta(hours=2)
        exp = ee.close(exp, {"save": 5.0}, now=early,
                       safety_triggered=True, safety_reason="harm signal")
        self.assertEqual(exp.outcome, ee.STOPPED_SAFETY)

    def test_missing_metric_is_inconclusive_not_success(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        exp = ee.start(_design(), now=start)
        later = start + timedelta(hours=25)
        exp = ee.close(exp, {"reach": 999.0}, now=later)  # no 'save' metric
        self.assertEqual(exp.outcome, ee.INCONCLUSIVE)
        self.assertNotEqual(exp.outcome, ee.SUCCESS)

    def test_missing_is_not_treated_as_zero(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        exp = ee.start(_design(), now=start)
        later = start + timedelta(hours=25)
        # 'save' present but None -> missing, not 0-effect FAILURE.
        exp = ee.close(exp, {"save": None}, now=later)
        self.assertEqual(exp.outcome, ee.INCONCLUSIVE)

    def test_failure_when_below_min_effect(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        exp = ee.start(_design(), now=start)
        later = start + timedelta(hours=25)
        exp = ee.close(exp, {"save": 10.2}, now=later)  # +0.2 < min_effect 1.0
        self.assertEqual(exp.outcome, ee.FAILURE)

    def test_duplicate_overlap_detected(self):
        e1 = ee.register("social-a", ee.start(_design()))
        e2 = _design()  # same persona/metric/intervention, still active
        with self.assertRaises(ValueError):
            ee.register("social-a", e2)
        self.assertTrue(ee.find_overlaps("social-a", e2))

    def test_learning_ref_only_for_real_effect(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        # SUCCESS -> ref
        good = ee.close(ee.start(_design(), now=start), {"save": 20.0},
                        now=start + timedelta(hours=25))
        self.assertIsNotNone(ee.to_learning_ref(good))
        self.assertEqual(good.learning_refs[0]["experiment_id"], good.id)
        # INCONCLUSIVE -> no ref (no fake learning)
        incon = ee.close(ee.start(_design(), now=start), {"reach": 1.0},
                         now=start + timedelta(hours=25))
        self.assertIsNone(ee.to_learning_ref(incon))
        # safety stop -> no ref
        stopped = ee.close(ee.start(_design(), now=start), {"save": 1.0},
                           now=start + timedelta(hours=1), safety_triggered=True)
        self.assertIsNone(ee.to_learning_ref(stopped))

    def test_persist_roundtrip(self):
        exp = ee.register("social-a", ee.start(_design()))
        back = ee.load("social-a", exp.id)
        self.assertIsNotNone(back)
        self.assertEqual(back.primary_metric, "save")
        self.assertEqual(back.status, ee.RUNNING)


if __name__ == "__main__":
    unittest.main()
