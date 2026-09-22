"""Invalid numeric observations and overflow must never become present metrics."""
import json
import os
import tempfile
import unittest

from runtime import metrics


INVALID = (True, False, float("nan"), float("inf"), float("-inf"), 10 ** 1000)


class FiniteMetricBoundaryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="bots-finite-boundary-")
        self.old_home = os.environ.get("SBOTS_HOME")
        os.environ["SBOTS_HOME"] = self.tmp.name

    def tearDown(self):
        if self.old_home is None:
            os.environ.pop("SBOTS_HOME", None)
        else:
            os.environ["SBOTS_HOME"] = self.old_home
        self.tmp.cleanup()

    def test_fresh_invalid_values_are_missing_and_raw_is_retained(self):
        for value in INVALID:
            with self.subTest(value=repr(value)):
                obs = metrics.normalize(platform="x", source="fixture:finite",
                                        raw_metrics={"impressions": value})
                reach = obs.metric(metrics.REACH)
                self.assertEqual(reach.availability, metrics.MISSING)
                self.assertIsNone(reach.value)
                self.assertIsNone(reach.raw_value)
                self.assertEqual(reach.raw_name, "impressions")
                self.assertEqual(reach.metric_kind, metrics.CUMULATIVE_SNAPSHOT)
                self.assertIs(obs.raw_metrics["impressions"], value)

    def test_legacy_invalid_values_count_missing_and_do_not_poison(self):
        base = metrics.normalize(
            platform="x", source="fixture:finite", content_id="valid",
            raw_metrics={"impressions": 7},
        ).as_dict()
        metrics.record("social-a", metrics.NormalizedObservation(**base))
        store = metrics._store("social-a")
        for index, value in enumerate(INVALID):
            legacy = dict(base)
            legacy["observation_id"] = f"legacy-{index}"
            legacy["content_id"] = f"legacy-{index}"
            legacy["normalized"] = dict(base["normalized"])
            legacy["normalized"][metrics.REACH] = dict(base["normalized"][metrics.REACH])
            legacy["normalized"][metrics.REACH]["availability"] = metrics.PRESENT
            legacy["normalized"][metrics.REACH]["value"] = value
            with store.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(legacy, allow_nan=True) + "\n")

        reach = metrics.aggregate_semantic("social-a", metrics.REACH)["by_platform"]["x"]
        snap = reach["kinds"][metrics.CUMULATIVE_SNAPSHOT]
        self.assertEqual(snap["value"], 7.0)
        self.assertEqual(snap["series_count"], 1)
        self.assertEqual(snap["count"], 1)
        self.assertEqual(reach["present"], 1)
        self.assertEqual(reach["missing"], len(INVALID))

    def test_finite_snapshot_sum_overflow_is_unavailable_with_coverage(self):
        for cid in ("a", "b"):
            metrics.record("social-a", metrics.normalize(
                platform="x", source="fixture:finite", content_id=cid,
                raw_metrics={"impressions": 1e308},
            ))
        reach = metrics.aggregate_semantic("social-a", metrics.REACH)["by_platform"]["x"]
        snap = reach["kinds"][metrics.CUMULATIVE_SNAPSHOT]
        self.assertIsNone(snap["value"])
        self.assertEqual(snap["unavailable_reason"], "non_finite_result")
        self.assertEqual(snap["series_count"], 2)
        self.assertEqual(snap["count"], 2)
        self.assertEqual(reach["present"], 2)
        self.assertEqual(reach["missing"], 0)

    def test_ratio_overflow_is_missing(self):
        obs = metrics.normalize(
            platform="x", source="fixture:finite",
            raw_metrics={"url_link_clicks": 1e308, "impressions": 1e-308},
        )
        ctr = metrics.click_through_rate(obs)
        self.assertEqual(ctr.availability, metrics.MISSING)
        self.assertIsNone(ctr.value)

    def test_snapshot_delta_overflow_is_missing_with_reason(self):
        previous = metrics.normalize(
            platform="x", source="fixture:finite", content_id="same",
            window_end="2026-09-21T00:00:00+00:00",
            raw_metrics={"impressions": -1e308},
        )
        current = metrics.normalize(
            platform="x", source="fixture:finite", content_id="same",
            window_end="2026-09-22T00:00:00+00:00",
            raw_metrics={"impressions": 1e308},
        )
        delta = metrics.derive_delta_from_snapshots(previous, current, metrics.REACH)
        self.assertEqual(delta.availability, metrics.MISSING)
        self.assertIsNone(delta.value)
        self.assertEqual(delta.derivation["reason"],
                         "snapshot difference is not a finite number")


if __name__ == "__main__":
    unittest.main()
