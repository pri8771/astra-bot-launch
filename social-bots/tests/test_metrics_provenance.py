"""SB-V13-002 provenance validation and legacy fail-closed regressions."""
import os
import tempfile
import unittest
from dataclasses import replace

from runtime import metrics
from runtime.jsonstore import append_jsonl


START = "2026-09-22T10:00:00+00:00"
END = "2026-09-22T11:00:00+00:00"


class MetricsProvenanceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="bots-metrics-provenance-")
        self.old_home = os.environ.get("SBOTS_HOME")
        os.environ["SBOTS_HOME"] = self.tmp.name

    def tearDown(self):
        if self.old_home is None:
            os.environ.pop("SBOTS_HOME", None)
        else:
            os.environ["SBOTS_HOME"] = self.old_home
        self.tmp.cleanup()

    def observation(self, *, source="capture:receipt-1", content="content-1", value=10):
        return metrics.normalize(
            platform="x", source=source, account_alias="account-a",
            persona="persona-a", content_id=content, experiment_id="experiment-a",
            window_start=START, window_end=END, collected_at=END,
            raw_metrics={"impressions": value, "url_clicks": 2},
        )

    def test_normalize_rejects_empty_whitespace_and_nonstring_source(self):
        for source in ("", "   ", 17, None, False):
            with self.subTest(source=source):
                with self.assertRaises(ValueError):
                    self.observation(source=source)

    def test_record_defends_direct_dataclass_construction(self):
        valid = self.observation()
        for source in ("", "   ", 17, None):
            with self.subTest(source=source):
                with self.assertRaises(ValueError):
                    metrics.record("bot-a", replace(valid, source=source))
        self.assertEqual(metrics.observations_for("bot-a"), [])

    def test_valid_provenance_and_all_identity_fields_survive_record_and_trace(self):
        obs = self.observation()
        metrics.record("bot-a", obs)

        trace = metrics.trace_content("bot-a", "content-1")

        self.assertEqual(trace["observation_count"], 1)
        self.assertEqual(trace.get("excluded_observations", []), [])
        [saved] = trace["observations"]
        expected = {
            "source": "capture:receipt-1", "platform": "x",
            "account_alias": "account-a", "persona": "persona-a",
            "content_id": "content-1", "experiment_id": "experiment-a",
            "window_start": START, "window_end": END, "collected_at": END,
        }
        self.assertEqual({key: saved[key] for key in expected}, expected)

    def test_legacy_bad_source_is_retained_but_excluded_from_trace_and_aggregate(self):
        valid = self.observation(content="shared", value=10).as_dict()
        malformed = dict(valid)
        malformed.update(observation_id="legacy-invalid", source="   ")
        append_jsonl(metrics._store("bot-a"), malformed)
        metrics.record("bot-a", self.observation(content="shared", value=7))

        stored = metrics.observations_for("bot-a")
        trace = metrics.trace_content("bot-a", "shared")
        aggregate = metrics.aggregate_semantic("bot-a", metrics.REACH)

        self.assertEqual([row["source"] for row in stored], ["   ", "capture:receipt-1"])
        self.assertEqual(trace["observation_count"], 1)
        self.assertEqual(len(trace["observations"]), 1)
        [excluded] = trace["excluded_observations"]
        self.assertIn("source", excluded["reason"])
        self.assertEqual(excluded["observation"]["observation_id"], "legacy-invalid")
        platform = aggregate["by_platform"]["x"]
        self.assertEqual(platform["invalid"], 1)
        self.assertEqual(platform["present"], 1)
        self.assertEqual(platform["kinds"][metrics.CUMULATIVE_SNAPSHOT]["value"], 7.0)

    def test_derived_ratio_and_snapshot_delta_are_unavailable_for_bad_source(self):
        previous = self.observation(content="series", value=10)
        current = replace(
            self.observation(content="series", value=15),
            observation_id="current", window_start=END,
            window_end="2026-09-22T12:00:00+00:00",
            collected_at="2026-09-22T12:00:00+00:00",
        )

        bad_ratio = metrics.click_through_rate(replace(current, source=""))
        bad_delta = metrics.derive_delta_from_snapshots(previous, replace(current, source=None),
                                                         metrics.REACH)

        self.assertEqual(bad_ratio.availability, metrics.MISSING)
        self.assertIsNone(bad_ratio.value)
        self.assertEqual(bad_delta.availability, metrics.MISSING)
        self.assertIsNone(bad_delta.value)
        self.assertIn("source", bad_delta.derivation["reason"])


if __name__ == "__main__":
    unittest.main()
