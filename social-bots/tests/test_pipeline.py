import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import pipeline, personas, analytics  # noqa: E402


SIGNAL = {"id": "sig-abc", "title": "Water tension demo",
          "summary": "A leaf floats because of surface tension.",
          "source": "test", "url": "https://example.org/leaf", "tags": ["nature"]}


class PipelineTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp

    def test_one_signal_different_candidates_per_persona(self):
        a = pipeline.ideate(personas.load("social-a"), SIGNAL)
        b = pipeline.ideate(personas.load("social-b"), SIGNAL)
        self.assertNotEqual(a["content_id"], b["content_id"])
        self.assertNotEqual(a["angle"], b["angle"])

    def test_cultural_review_withheld_without_reviewer(self):
        p = personas.load("cultural-primandir-atman")
        cand = pipeline.ideate(p, SIGNAL)
        reviewed = pipeline.review(p, cand)
        self.assertFalse(reviewed["review_passed"])
        self.assertEqual(reviewed["review"]["cultural"]["status"], "WITHHELD")

    def test_general_review_passes_with_source(self):
        p = personas.load("social-a")
        reviewed = pipeline.review(p, pipeline.ideate(p, SIGNAL))
        self.assertTrue(reviewed["review_passed"])

    def test_platform_formatting_respects_limit(self):
        p = personas.load("social-a")
        cand = pipeline.ideate(p, SIGNAL)
        payload = pipeline.format_for_platform(cand, "x")
        self.assertLessEqual(len(payload["text"]), 280)

    def test_queue_defaults_unpublished_unauthorized(self):
        p = personas.load("social-a")
        cand = pipeline.review(p, pipeline.ideate(p, SIGNAL))
        payload = pipeline.format_for_platform(cand, "x")
        entry = pipeline.enqueue("social-a", cand, payload, "exp-1")
        self.assertFalse(entry["publish_authorized"])
        self.assertFalse(entry["published"])

    def test_analytics_event_requires_keys(self):
        ev = analytics.make_event("social-a", "social-a", "queued", platform="x")
        self.assertEqual(analytics.validate_event(ev), [])
        with self.assertRaises(ValueError):
            analytics.make_event("social-a", "social-a", "not-a-type")


if __name__ == "__main__":
    unittest.main()
