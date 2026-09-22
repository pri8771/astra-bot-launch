"""SB-V13-002 legacy metric-kind fail-closed regressions."""
import os
import tempfile
import unittest
from dataclasses import replace

from runtime import metrics
from runtime.jsonstore import append_jsonl


COLLECTED = "2026-09-22T12:00:00+00:00"


class MetricsLegacyKindsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="bots-metrics-legacy-kind-")
        self.old_home = os.environ.get("SBOTS_HOME")
        os.environ["SBOTS_HOME"] = self.tmp.name

    def tearDown(self):
        if self.old_home is None:
            os.environ.pop("SBOTS_HOME", None)
        else:
            os.environ["SBOTS_HOME"] = self.old_home
        self.tmp.cleanup()

    def observation(self):
        return metrics.normalize(
            platform="x", source="capture:receipt-1", persona="persona-a",
            content_id="content-a", collected_at=COLLECTED,
            raw_metrics={"impressions": 9},
        )

    @staticmethod
    def with_unknown_kind(row):
        row = dict(row)
        row["normalized"] = {name: dict(value)
                             for name, value in row["normalized"].items()}
        row["normalized"][metrics.REACH]["metric_kind"] = "invented_kind"
        return row

    def test_record_rejects_direct_observation_with_unknown_present_kind(self):
        obs = self.observation()
        malformed = self.with_unknown_kind(obs.as_dict())
        direct = replace(obs, normalized=malformed["normalized"])

        with self.assertRaises(ValueError):
            metrics.record("bot-a", direct)

        self.assertEqual(metrics.observations_for("bot-a"), [])

    def test_legacy_unknown_kind_is_retained_but_excluded_from_trace_and_aggregate(self):
        malformed = self.with_unknown_kind(self.observation().as_dict())
        malformed["observation_id"] = "legacy-unknown-kind"
        append_jsonl(metrics._store("bot-a"), malformed)

        stored = metrics.observations_for("bot-a")
        trace = metrics.trace_content("bot-a", "content-a")
        aggregate = metrics.aggregate_semantic("bot-a", metrics.REACH)

        self.assertEqual(stored[0]["normalized"][metrics.REACH]["metric_kind"],
                         "invented_kind")
        self.assertEqual(trace["observation_count"], 0)
        self.assertEqual(trace["observations"], [])
        [excluded] = trace["excluded_observations"]
        self.assertIn("metric_kind", excluded["reason"])
        self.assertEqual(excluded["observation"]["observation_id"],
                         "legacy-unknown-kind")
        platform = aggregate["by_platform"]["x"]
        self.assertEqual(platform["invalid"], 1)
        self.assertEqual(platform["present"], 0)
        self.assertEqual(platform["kinds"], {})

    def test_declared_valid_raw_kind_override_remains_supported(self):
        obs = metrics.normalize(
            platform="x", source="capture:receipt-1", persona="persona-a",
            content_id="content-a", collected_at=COLLECTED,
            raw_metrics={"impressions": 9}, raw_kinds={"impressions": metrics.GAUGE},
        )
        metrics.record("bot-a", obs)

        aggregate = metrics.aggregate_semantic("bot-a", metrics.REACH)

        self.assertEqual(obs.metric(metrics.REACH).metric_kind, metrics.GAUGE)
        self.assertEqual(aggregate["by_platform"]["x"]["invalid"], 0)
        self.assertEqual(aggregate["by_platform"]["x"]["kinds"][metrics.GAUGE]["value"],
                         9.0)

    def test_platform_mapping_mismatches_fail_closed_for_record_and_legacy_rows(self):
        cases = (
            ("tiktok", "video_views", "impressions", "tiktok-reach"),
            ("x", "likes", "likes", "x-unmapped-likes"),
        )
        for platform, seed_raw, claimed_raw, bot in cases:
            with self.subTest(platform=platform, claimed_raw=claimed_raw):
                obs = metrics.normalize(
                    platform=platform, source="capture:receipt-1", persona="persona-a",
                    content_id="content-a", collected_at=COLLECTED,
                    raw_metrics={seed_raw: 9},
                )
                malformed = obs.as_dict()
                malformed["normalized"] = {
                    name: dict(value) for name, value in malformed["normalized"].items()
                }
                malformed["normalized"][metrics.REACH] = {
                    "semantic": metrics.REACH, "availability": metrics.PRESENT,
                    "value": 9.0, "raw_name": claimed_raw, "raw_value": 9.0,
                    "metric_kind": metrics.CUMULATIVE_SNAPSHOT,
                }
                malformed["raw_metrics"] = {claimed_raw: 9}
                direct = replace(obs, raw_metrics=malformed["raw_metrics"],
                                 normalized=malformed["normalized"])

                with self.assertRaises(ValueError):
                    metrics.record(bot, direct)

                malformed["observation_id"] = f"legacy-{bot}"
                append_jsonl(metrics._store(bot), malformed)
                stored = metrics.observations_for(bot)
                trace = metrics.trace_content(bot, "content-a")
                aggregate = metrics.aggregate_semantic(bot, metrics.REACH)

                self.assertEqual(stored[0]["normalized"][metrics.REACH]["raw_name"],
                                 claimed_raw)
                self.assertEqual(trace["observation_count"], 0)
                [excluded] = trace["excluded_observations"]
                self.assertIn("mapping", excluded["reason"])
                self.assertEqual(excluded["observation"]["observation_id"],
                                 f"legacy-{bot}")
                bucket = aggregate["by_platform"][platform]
                self.assertEqual(bucket["invalid"], 1)
                self.assertEqual(bucket["present"], 0)
                self.assertEqual(bucket["kinds"], {})


if __name__ == "__main__":
    unittest.main()
