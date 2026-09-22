"""SB-V13-002 observation timestamp and window trust boundaries."""

import json
import os
import tempfile
import unittest
from datetime import datetime, timezone

from runtime import metrics


START = "2026-09-22T00:00:00+00:00"
END = "2026-09-22T01:00:00+00:00"


class MetricWindowBoundaryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="bots-metric-windows-")
        self.old_home = os.environ.get("SBOTS_HOME")
        os.environ["SBOTS_HOME"] = self.tmp.name

    def tearDown(self):
        if self.old_home is None:
            os.environ.pop("SBOTS_HOME", None)
        else:
            os.environ["SBOTS_HOME"] = self.old_home
        self.tmp.cleanup()

    def _normalize(self, **kwargs):
        args = {
            "platform": "tiktok",
            "source": "fixture:window-boundary",
            "persona": "social-a",
            "content_id": "content-1",
            "raw_metrics": {"new_followers": 7},
        }
        args.update(kwargs)
        return metrics.normalize(**args)

    def _append_legacy(self, row: dict) -> None:
        store = metrics._store("social-a")
        store.parent.mkdir(parents=True, exist_ok=True)
        with store.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")

    def test_normalize_rejects_malformed_nonstring_and_naive_metadata(self):
        bad_values = ("not-a-time", 123, "2026-09-22T01:00:00")
        for field in ("window_start", "window_end", "collected_at"):
            for value in bad_values:
                with self.subTest(field=field, value=value):
                    kwargs = {"window_start": START, "window_end": END, field: value}
                    with self.assertRaises(ValueError):
                        self._normalize(**kwargs)

    def test_normalize_rejects_reversed_and_equal_windows(self):
        for start, end in ((END, START), (START, START)):
            with self.subTest(start=start, end=end):
                with self.assertRaises(ValueError):
                    self._normalize(window_start=start, window_end=end)

    def test_record_revalidates_metadata_before_persisting(self):
        for field, value in (
            ("window_start", "bad"),
            ("window_end", 123),
            ("collected_at", "2026-09-22T01:00:00"),
        ):
            with self.subTest(field=field, value=value):
                obs = self._normalize(window_start=START, window_end=END)
                object.__setattr__(obs, field, value)
                with self.assertRaises(ValueError):
                    metrics.record("social-a", obs)
        self.assertEqual(metrics.observations_for("social-a"), [])

    def test_legacy_invalid_metadata_is_excluded_from_trace_and_aggregate(self):
        row = self._normalize(window_start=START, window_end=END).as_dict()
        row["observation_id"] = "legacy-reversed"
        row["window_start"], row["window_end"] = END, START
        self._append_legacy(row)

        trace = metrics.trace_content("social-a", "content-1")
        self.assertEqual(trace["observation_count"], 0)
        self.assertEqual(trace["observations"], [])
        aggregate = metrics.aggregate_semantic("social-a", metrics.FOLLOW)
        bucket = aggregate["by_platform"]["tiktok"]
        self.assertEqual(bucket["invalid"], 1)
        self.assertEqual(bucket["present"], 0)
        self.assertEqual(bucket["kinds"], {})

    def test_invalid_legacy_metadata_is_stale_and_cannot_derive_delta(self):
        previous = metrics.normalize(
            platform="x", source="fixture:window-boundary", content_id="same",
            window_end=START, raw_metrics={"impressions": 10},
        )
        current = metrics.normalize(
            platform="x", source="fixture:window-boundary", content_id="same",
            window_end=END, raw_metrics={"impressions": 20},
        )
        object.__setattr__(current, "window_end", "not-a-time")
        object.__setattr__(current, "collected_at", "also-not-a-time")

        self.assertTrue(metrics.is_stale(
            current, max_age_hours=24,
            now=datetime(2026, 9, 22, 2, tzinfo=timezone.utc),
        ))
        delta = metrics.derive_delta_from_snapshots(previous, current, metrics.REACH)
        self.assertEqual(delta.availability, metrics.MISSING)
        self.assertFalse(delta.derivation["ok"])

    def test_optional_and_end_only_snapshot_metadata_remain_supported(self):
        no_window = metrics.normalize(
            platform="x", source="fixture:window-boundary", content_id="none",
            raw_metrics={"impressions": 3},
        )
        end_only = metrics.normalize(
            platform="x", source="fixture:window-boundary", content_id="end-only",
            window_end=END, raw_metrics={"impressions": 5},
        )
        metrics.record("social-a", no_window)
        metrics.record("social-a", end_only)
        snap = metrics.aggregate_semantic("social-a", metrics.REACH)["by_platform"]["x"]
        self.assertEqual(snap["kinds"][metrics.CUMULATIVE_SNAPSHOT]["value"], 8.0)

    def test_delta_without_complete_window_is_excluded(self):
        metrics.record("social-a", self._normalize(window_end=END))
        delta = metrics.aggregate_semantic("social-a", metrics.FOLLOW)["by_platform"]["tiktok"]
        result = delta["kinds"][metrics.DELTA]
        self.assertEqual(result["value"], 0.0)
        self.assertEqual(result["count"], 0)
        self.assertEqual(result["excluded_overlapping"], 1)

    def test_snapshot_latest_uses_actual_instant_not_iso_lexical_order(self):
        older = metrics.normalize(
            platform="x", source="fixture:window-boundary", account_alias="acct",
            persona="social-a", content_id="same",
            window_end="2026-09-22T02:00:00+02:00",
            raw_metrics={"impressions": 10},
        )  # 00:00Z; lexically greater than the newer timestamp below.
        newer = metrics.normalize(
            platform="x", source="fixture:window-boundary", account_alias="acct",
            persona="social-a", content_id="same",
            window_end="2026-09-22T01:00:00+00:00",
            raw_metrics={"impressions": 20},
        )
        metrics.record("social-a", older)
        metrics.record("social-a", newer)

        snap = metrics.aggregate_semantic("social-a", metrics.REACH)["by_platform"]["x"]
        self.assertEqual(snap["kinds"][metrics.CUMULATIVE_SNAPSHOT]["value"], 20.0)


if __name__ == "__main__":
    unittest.main()
