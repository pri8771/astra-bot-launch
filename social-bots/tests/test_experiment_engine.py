"""SB-V15-001 — autonomous experiment lifecycle acceptance tests.

Baseline/treatment bind to SB-V13-001 normalized metric observations.
"""
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import experiment_engine as ee, metrics  # noqa: E402

# 24h windows so baseline/treatment are window-comparable by default.
W1 = ("2026-01-01T00:00:00+00:00", "2026-01-02T00:00:00+00:00")
W2 = ("2026-01-03T00:00:00+00:00", "2026-01-04T00:00:00+00:00")


def _obs(saved_value, window=W1, raw_kinds=None, raw_name="saved",
         extra=None):
    raw = {raw_name: saved_value} if saved_value is not None else {raw_name: None}
    if extra:
        raw.update(extra)
    return metrics.normalize(platform="instagram", source="fixture",
                             content_id="c-1", persona="social-a",
                             window_start=window[0], window_end=window[1],
                             raw_metrics=raw, raw_kinds=raw_kinds)


def _design(**kw):
    return ee.design("social-a", "social-a", hypothesis="H",
                     baseline_observation=_obs(10.0), intervention="new-hook",
                     primary_metric=metrics.SAVE, min_observation_hours=24.0,
                     stop_criteria={"min_effect": 1.0, "direction": "increase"}, **kw)


class ExperimentEngineTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp

    def test_baseline_binds_to_observation(self):
        exp = _design()
        self.assertTrue(exp.baseline["observation_id"].startswith("obs-"))
        self.assertEqual(exp.baseline["semantic"], metrics.SAVE)
        self.assertEqual(exp.baseline["value"], 10.0)

    def test_design_requires_present_baseline(self):
        with self.assertRaises(ValueError):
            ee.design("social-a", "social-a", hypothesis="H",
                      baseline_observation=_obs(None),  # missing metric
                      intervention="x", primary_metric=metrics.SAVE,
                      min_observation_hours=24.0)

    def test_cannot_close_before_window(self):
        exp = ee.start(_design(), now=datetime(2026, 1, 1, tzinfo=timezone.utc))
        early = datetime(2026, 1, 1, 5, tzinfo=timezone.utc)
        self.assertFalse(ee.can_close(exp, now=early))
        with self.assertRaises(ValueError):
            ee.close(exp, _obs(20.0, window=W2), now=early)

    def test_can_close_after_window(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        exp = ee.start(_design(), now=start)
        later = start + timedelta(hours=25)
        exp = ee.close(exp, _obs(20.0, window=W2), now=later)
        self.assertEqual(exp.status, ee.CLOSED)
        self.assertEqual(exp.outcome, ee.SUCCESS)
        self.assertEqual(exp.result["effect_size"], 10.0)
        # Effect traces back to both measurement observations.
        self.assertIn("baseline_observation_id", exp.result)
        self.assertIn("treatment_observation_id", exp.result)

    def test_safety_stop_closes_early(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        exp = ee.start(_design(), now=start)
        early = start + timedelta(hours=2)
        exp = ee.close(exp, _obs(5.0, window=W2), now=early,
                       safety_triggered=True, safety_reason="harm signal")
        self.assertEqual(exp.outcome, ee.STOPPED_SAFETY)

    def test_missing_metric_is_inconclusive_not_success(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        exp = ee.start(_design(), now=start)
        later = start + timedelta(hours=25)
        # treatment observation reports reach only -> save MISSING.
        treat = metrics.normalize(platform="instagram", source="fixture",
                                  content_id="c-1", persona="social-a",
                                  window_start=W2[0], window_end=W2[1],
                                  raw_metrics={"reach": 999})
        exp = ee.close(exp, treat, now=later)
        self.assertEqual(exp.outcome, ee.INCONCLUSIVE)

    def test_missing_is_not_treated_as_zero(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        exp = ee.start(_design(), now=start)
        later = start + timedelta(hours=25)
        exp = ee.close(exp, _obs(None, window=W2), now=later)  # saved present but null
        self.assertEqual(exp.outcome, ee.INCONCLUSIVE)

    def test_failure_when_below_min_effect(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        exp = ee.start(_design(), now=start)
        later = start + timedelta(hours=25)
        exp = ee.close(exp, _obs(10.2, window=W2), now=later)  # +0.2 < 1.0
        self.assertEqual(exp.outcome, ee.FAILURE)

    # --- semantic/window compatibility validation ------------------------ #
    def test_kind_mismatch_is_inconclusive(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        exp = ee.start(_design(), now=start)  # baseline SAVE snapshot
        later = start + timedelta(hours=25)
        # Treatment SAVE forced to DELTA kind -> incompatible with snapshot.
        treat = _obs(20.0, window=W2, raw_kinds={"saved": metrics.DELTA})
        exp = ee.close(exp, treat, now=later)
        self.assertEqual(exp.outcome, ee.INCONCLUSIVE)
        self.assertIn("metric kind mismatch", exp.result["reason"])

    def test_incomparable_window_is_inconclusive(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        exp = ee.start(_design(), now=start)  # baseline 24h window
        later = start + timedelta(hours=25)
        short = ("2026-01-03T00:00:00+00:00", "2026-01-03T01:00:00+00:00")  # 1h
        treat = _obs(20.0, window=short)
        exp = ee.close(exp, treat, now=later)
        self.assertEqual(exp.outcome, ee.INCONCLUSIVE)
        self.assertIn("windows", exp.result["reason"])

    def test_duplicate_overlap_detected(self):
        ee.register("social-a", ee.start(_design()))
        e2 = _design()
        with self.assertRaises(ValueError):
            ee.register("social-a", e2)
        self.assertTrue(ee.find_overlaps("social-a", e2))

    def test_learning_ref_only_for_real_effect_traces_measurements(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        good = ee.close(ee.start(_design(), now=start), _obs(20.0, window=W2),
                        now=start + timedelta(hours=25))
        ref = ee.to_learning_ref(good)
        self.assertIsNotNone(ref)
        self.assertEqual(ref["experiment_id"], good.id)
        self.assertEqual(ref["baseline_observation_id"], good.baseline["observation_id"])
        self.assertTrue(ref["treatment_observation_id"].startswith("obs-"))
        # INCONCLUSIVE -> no ref.
        incon_treat = metrics.normalize(platform="instagram", source="fixture",
                                        content_id="c-1", persona="social-a",
                                        window_start=W2[0], window_end=W2[1],
                                        raw_metrics={"reach": 1})
        incon = ee.close(ee.start(_design(), now=start), incon_treat,
                         now=start + timedelta(hours=25))
        self.assertIsNone(ee.to_learning_ref(incon))
        # safety stop -> no ref.
        stopped = ee.close(ee.start(_design(), now=start), _obs(1.0, window=W2),
                           now=start + timedelta(hours=1), safety_triggered=True)
        self.assertIsNone(ee.to_learning_ref(stopped))

    def test_persist_roundtrip(self):
        exp = ee.register("social-a", ee.start(_design()))
        back = ee.load("social-a", exp.id)
        self.assertIsNotNone(back)
        self.assertEqual(back.primary_metric, metrics.SAVE)
        self.assertEqual(back.status, ee.RUNNING)
        self.assertEqual(back.baseline_ref().value, 10.0)


if __name__ == "__main__":
    unittest.main()
