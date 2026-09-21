"""SB-V13-001 — normalized analytics brain acceptance tests.

Uses explicit engineering fixtures. These are NOT real social metrics.
"""
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import metrics  # noqa: E402


class MetricsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp

    # --- MISSING != ZERO -------------------------------------------------- #
    def test_missing_is_not_zero(self):
        # instagram supports SAVE; here save is not reported -> MISSING, not 0.
        obs = metrics.normalize(platform="instagram", source="fixture",
                                raw_metrics={"reach": 100, "plays": 50})
        save = obs.metric(metrics.SAVE)
        self.assertEqual(save.availability, metrics.MISSING)
        self.assertIsNone(save.value)
        self.assertTrue(save.is_missing())

    def test_explicit_zero_is_present(self):
        obs = metrics.normalize(platform="instagram", source="fixture",
                                raw_metrics={"reach": 0, "saved": 0})
        reach = obs.metric(metrics.REACH)
        self.assertEqual(reach.availability, metrics.PRESENT)
        self.assertEqual(reach.value, 0.0)
        self.assertFalse(reach.is_missing())

    def test_not_supported_distinct_from_missing(self):
        # reddit has no reach/view equivalent -> NOT_SUPPORTED (not MISSING, not 0).
        obs = metrics.normalize(platform="reddit", source="fixture",
                                raw_metrics={"num_comments": 3})
        self.assertEqual(obs.metric(metrics.REACH).availability, metrics.NOT_SUPPORTED)
        self.assertEqual(obs.metric(metrics.VIEW).availability, metrics.NOT_SUPPORTED)
        self.assertEqual(obs.metric(metrics.REPLY).availability, metrics.PRESENT)
        self.assertEqual(obs.metric(metrics.REPLY).value, 3.0)

    # --- no false equivalence -------------------------------------------- #
    def test_no_false_equivalence_across_platforms(self):
        # X impressions -> REACH; TikTok has no reach mapping -> NOT_SUPPORTED.
        x = metrics.normalize(platform="x", source="fixture",
                              raw_metrics={"impressions": 1000})
        tt = metrics.normalize(platform="tiktok", source="fixture",
                               raw_metrics={"video_views": 1000})
        self.assertEqual(x.metric(metrics.REACH).availability, metrics.PRESENT)
        self.assertEqual(tt.metric(metrics.REACH).availability, metrics.NOT_SUPPORTED)
        # Each retains its own raw name -> no silent cross-platform blend.
        self.assertEqual(x.metric(metrics.REACH).raw_name, "impressions")

    def test_unmapped_raw_retained_not_blended(self):
        obs = metrics.normalize(platform="x", source="fixture",
                                raw_metrics={"impressions": 10, "likes": 7})
        self.assertIn("likes", obs.raw_metrics)       # full raw retention
        self.assertIn("likes", obs.unmapped_raw)      # kept, not mapped to a semantic
        self.assertEqual(obs.raw_metrics["likes"], 7)

    # --- provenance / identifiers / normalization version ---------------- #
    def test_identifiers_and_provenance_retained(self):
        obs = metrics.normalize(
            platform="x", source="capture:cap-123", account_alias="acct-a",
            persona="social-a", content_id="c-1", experiment_id="e-1",
            window_start="2026-09-20T00:00:00+00:00",
            window_end="2026-09-21T00:00:00+00:00",
            raw_metrics={"impressions": 5})
        d = obs.as_dict()
        for key in ("platform", "source", "account_alias", "persona", "content_id",
                    "experiment_id", "window_start", "window_end", "collected_at",
                    "normalization_version", "raw_metrics"):
            self.assertIn(key, d)
        self.assertEqual(obs.normalization_version, metrics.NORMALIZATION_VERSION)

    # --- derived metrics: formula/version + MISSING propagation ---------- #
    def test_derived_records_formula_and_version(self):
        obs = metrics.normalize(platform="tiktok", source="fixture",
                                raw_metrics={"video_views": 200, "completion_views": 50})
        d = metrics.completion_rate(obs)
        self.assertEqual(d.availability, metrics.PRESENT)
        self.assertAlmostEqual(d.value, 0.25)
        self.assertEqual(d.formula, "completion / view")
        self.assertEqual(d.formula_version, metrics.DERIVED_FORMULA_VERSION)

    def test_derived_missing_when_input_missing(self):
        obs = metrics.normalize(platform="tiktok", source="fixture",
                                raw_metrics={"video_views": 200})  # no completion
        d = metrics.completion_rate(obs)
        self.assertEqual(d.availability, metrics.MISSING)
        self.assertIsNone(d.value)  # not fabricated as 0

    def test_derived_missing_on_zero_denominator(self):
        obs = metrics.normalize(platform="instagram", source="fixture",
                                raw_metrics={"reach": 0, "saved": 5})
        d = metrics.save_rate(obs)
        self.assertEqual(d.availability, metrics.MISSING)  # divide-by-zero -> missing
        self.assertIsNone(d.value)

    # --- traceability ---------------------------------------------------- #
    def test_trace_content_to_persona_and_experiment(self):
        obs = metrics.normalize(platform="x", source="fixture", persona="social-b",
                                content_id="c-42", experiment_id="e-9",
                                raw_metrics={"impressions": 3})
        metrics.record("social-b", obs)
        trace = metrics.trace_content("social-b", "c-42")
        self.assertEqual(trace["observation_count"], 1)
        self.assertEqual(trace["personas"], ["social-b"])
        self.assertEqual(trace["experiments"], ["e-9"])
        self.assertEqual(trace["observations"][0]["raw_metrics"]["impressions"], 3)

    # --- staleness ------------------------------------------------------- #
    def test_stale_window_marked(self):
        old_end = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
        fresh_end = datetime.now(timezone.utc).isoformat()
        stale = metrics.normalize(platform="x", source="fixture",
                                  window_end=old_end, raw_metrics={"impressions": 1})
        fresh = metrics.normalize(platform="x", source="fixture",
                                  window_end=fresh_end, raw_metrics={"impressions": 1})
        self.assertTrue(metrics.is_stale(stale, max_age_hours=24))
        self.assertFalse(metrics.is_stale(fresh, max_age_hours=24))

    def test_no_window_treated_as_stale(self):
        obs = metrics.normalize(platform="x", source="fixture",
                                raw_metrics={"impressions": 1})
        object.__setattr__(obs, "window_end", None)
        object.__setattr__(obs, "collected_at", None)
        self.assertTrue(metrics.is_stale(obs, max_age_hours=24))

    # --- honest, kind-aware aggregation ---------------------------------- #
    def test_aggregate_excludes_missing_and_groups_by_platform(self):
        # Two different content items -> two series; latest-per-series summed.
        metrics.record("social-a", metrics.normalize(
            platform="instagram", source="fixture", content_id="c1",
            raw_metrics={"saved": 4}))
        metrics.record("social-a", metrics.normalize(
            platform="instagram", source="fixture", content_id="c2",
            raw_metrics={"reach": 10}))  # save MISSING here
        agg = metrics.aggregate_semantic("social-a", metrics.SAVE)
        ig = agg["by_platform"]["instagram"]
        snap = ig["kinds"][metrics.CUMULATIVE_SNAPSHOT]
        self.assertEqual(snap["value"], 4.0)     # missing not counted as 0
        self.assertEqual(snap["series_count"], 1)
        self.assertEqual(ig["present"], 1)
        self.assertEqual(ig["missing"], 1)

    def test_metric_declares_semantic_kind(self):
        obs = metrics.normalize(platform="instagram", source="fixture",
                                raw_metrics={"reach": 100})
        self.assertEqual(obs.metric(metrics.REACH).metric_kind,
                         metrics.CUMULATIVE_SNAPSHOT)
        obs2 = metrics.normalize(platform="tiktok", source="fixture",
                                 raw_metrics={"new_followers": 20})
        self.assertEqual(obs2.metric(metrics.FOLLOW).metric_kind, metrics.DELTA)

    def test_cumulative_snapshots_not_summed_over_time(self):
        """snapshots 100 then 150 views must NOT aggregate to 250."""
        for v, end in ((100, "2026-09-20T00:00:00+00:00"),
                       (150, "2026-09-21T00:00:00+00:00")):
            metrics.record("social-a", metrics.normalize(
                platform="tiktok", source="fixture", content_id="same-c",
                window_end=end, raw_metrics={"video_views": v}))
        agg = metrics.aggregate_semantic("social-a", metrics.VIEW)
        snap = agg["by_platform"]["tiktok"]["kinds"][metrics.CUMULATIVE_SNAPSHOT]
        self.assertEqual(snap["value"], 150.0)      # latest, not 250
        self.assertEqual(snap["series_count"], 1)
        self.assertEqual(snap["count"], 2)

    def test_deltas_may_sum_over_non_overlapping_windows(self):
        """valid non-overlapping deltas 100 + 50 may aggregate to 150."""
        for v, w in ((100, ("2026-09-20T00:00:00+00:00", "2026-09-21T00:00:00+00:00")),
                     (50, ("2026-09-21T00:00:00+00:00", "2026-09-22T00:00:00+00:00"))):
            metrics.record("social-a", metrics.normalize(
                platform="tiktok", source="fixture", content_id="same-c",
                window_start=w[0], window_end=w[1], raw_metrics={"new_followers": v}))
        agg = metrics.aggregate_semantic("social-a", metrics.FOLLOW)
        delta = agg["by_platform"]["tiktok"]["kinds"][metrics.DELTA]
        self.assertEqual(delta["value"], 150.0)
        self.assertEqual(delta["excluded_overlapping"], 0)

    def test_overlapping_delta_windows_not_double_counted(self):
        # Two deltas over the SAME (duplicate) window must not double-count.
        w = ("2026-09-20T00:00:00+00:00", "2026-09-21T00:00:00+00:00")
        for v in (100, 100):
            metrics.record("social-a", metrics.normalize(
                platform="tiktok", source="fixture", content_id="same-c",
                window_start=w[0], window_end=w[1], raw_metrics={"new_followers": v}))
        # And an overlapping (not identical) window.
        metrics.record("social-a", metrics.normalize(
            platform="tiktok", source="fixture", content_id="same-c",
            window_start="2026-09-20T12:00:00+00:00",
            window_end="2026-09-21T12:00:00+00:00", raw_metrics={"new_followers": 100}))
        agg = metrics.aggregate_semantic("social-a", metrics.FOLLOW)
        delta = agg["by_platform"]["tiktok"]["kinds"][metrics.DELTA]
        self.assertEqual(delta["value"], 100.0)      # only one counted
        self.assertEqual(delta["count"], 1)
        self.assertEqual(delta["excluded_overlapping"], 2)

    def test_supported_but_missing_metric_retains_expected_kind(self):
        # instagram supports SAVE (a cumulative snapshot) but does not report it.
        obs = metrics.normalize(platform="instagram", source="fixture",
                                raw_metrics={"reach": 100})
        save = obs.metric(metrics.SAVE)
        self.assertEqual(save.availability, metrics.MISSING)
        self.assertEqual(save.metric_kind, metrics.CUMULATIVE_SNAPSHOT)
        # A genuinely not-supported semantic stays kind-unknown.
        rd = metrics.normalize(platform="reddit", source="fixture",
                               raw_metrics={"num_comments": 1})
        self.assertIsNone(rd.metric(metrics.VIEW).metric_kind)

    def test_snapshot_to_delta_derivation_records_derivation(self):
        prev = metrics.normalize(
            platform="tiktok", source="fixture", content_id="c-d",
            window_end="2026-09-20T00:00:00+00:00",
            raw_metrics={"video_views": 100})
        curr = metrics.normalize(
            platform="tiktok", source="fixture", content_id="c-d",
            window_end="2026-09-21T00:00:00+00:00",
            raw_metrics={"video_views": 150})
        d = metrics.derive_delta_from_snapshots(prev, curr, metrics.VIEW)
        self.assertEqual(d.availability, metrics.PRESENT)
        self.assertEqual(d.value, 50.0)
        self.assertEqual(d.metric_kind, metrics.DELTA)
        self.assertTrue(d.derivation["ok"])
        self.assertEqual(d.derivation["previous_observation_id"], prev.observation_id)

    def test_snapshot_delta_requires_comparable_series(self):
        prev = metrics.normalize(
            platform="tiktok", source="fixture", content_id="c-a",
            window_end="2026-09-20T00:00:00+00:00",
            raw_metrics={"video_views": 100})
        other = metrics.normalize(
            platform="tiktok", source="fixture", content_id="c-b",  # different item
            window_end="2026-09-21T00:00:00+00:00",
            raw_metrics={"video_views": 150})
        d = metrics.derive_delta_from_snapshots(prev, other, metrics.VIEW)
        self.assertEqual(d.availability, metrics.MISSING)
        self.assertIsNone(d.value)
        self.assertFalse(d.derivation["ok"])

    def test_snapshot_delta_rejects_decrease(self):
        prev = metrics.normalize(
            platform="tiktok", source="fixture", content_id="c-x",
            window_end="2026-09-20T00:00:00+00:00",
            raw_metrics={"video_views": 200})
        curr = metrics.normalize(
            platform="tiktok", source="fixture", content_id="c-x",
            window_end="2026-09-21T00:00:00+00:00",
            raw_metrics={"video_views": 150})  # cumulative decreased -> invalid
        d = metrics.derive_delta_from_snapshots(prev, curr, metrics.VIEW)
        self.assertEqual(d.availability, metrics.MISSING)
        self.assertEqual(d.derivation["reason"],
                         "cumulative snapshot decreased; not a valid delta")


if __name__ == "__main__":
    unittest.main()
