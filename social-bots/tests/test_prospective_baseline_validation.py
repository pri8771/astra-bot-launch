"""Red regressions for C07 measured-baseline validation.

Standalone mechanical tests for the existing pipeline schema. They deliberately
do not require a NormalizedObservation id because the current measured-baseline
contract accepts metric/value/status/measured_at/source only.
"""
import math
import os
import tempfile
import unittest

from runtime import pipeline


def _experiment(baseline):
    return pipeline.Experiment(
        experiment_id="exp-regression",
        bot="social-a",
        persona="social-a",
        platform="x",
        hypothesis="h",
        baseline=baseline,
        intervention="i",
        success_metric="saves",
        stop_criteria="s",
        observation_window_hours=48,
    )


def _measured(**overrides):
    baseline = {
        "metric": "saves",
        "value": 12.0,
        "status": pipeline.MEASURED,
        "measured_at": "2026-09-21T00:00:00Z",
        "source": "analytics:fixture-window",
    }
    baseline.update(overrides)
    return baseline


class MeasuredBaselineValidationRegression(unittest.TestCase):
    def setUp(self):
        self.previous_home = os.environ.get("SBOTS_HOME")
        os.environ["SBOTS_HOME"] = tempfile.mkdtemp()

    def tearDown(self):
        if self.previous_home is None:
            os.environ.pop("SBOTS_HOME", None)
        else:
            os.environ["SBOTS_HOME"] = self.previous_home

    def assert_rejected(self, baseline, expected_fragment):
        errors = pipeline.validate_prospective(_experiment(baseline))
        self.assertTrue(any(expected_fragment in error for error in errors), errors)
        with self.assertRaises(pipeline.ExperimentRegistrationError):
            pipeline.register_experiment(_experiment(baseline))

    def test_measured_baseline_metric_must_match_success_metric(self):
        self.assert_rejected(_measured(metric="likes"), "success_metric")

    def test_measured_baseline_value_must_be_finite_numeric_not_bool(self):
        for value in ("12", True, math.nan, math.inf, -math.inf):
            with self.subTest(value=value):
                self.assert_rejected(_measured(value=value), "finite number")

    def test_measured_at_must_be_a_parseable_timestamp(self):
        for measured_at in ("not-a-date", 123, ""):
            with self.subTest(measured_at=measured_at):
                self.assert_rejected(_measured(measured_at=measured_at), "measured_at")

    def test_source_must_be_a_nonempty_string(self):
        for source in ("", "   ", 123, None):
            with self.subTest(source=source):
                self.assert_rejected(_measured(source=source), "source")

    def test_current_valid_measured_baseline_shape_remains_accepted(self):
        exp = _experiment(_measured())
        self.assertEqual(pipeline.validate_prospective(exp), [])
        self.assertTrue(pipeline.register_experiment(exp).is_file())


if __name__ == "__main__":
    unittest.main()
