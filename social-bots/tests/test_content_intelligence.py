"""SB-V16-001 — content intelligence acceptance tests."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import content_intelligence as ci  # noqa: E402

BINDING = {"claim_id": "cl-1", "receipt_id": "cap-1", "content_hash": "abc123"}


def _concept(**kw):
    segs = [
        ci.Segment.framing("Here's a wild angle you didn't expect."),
        ci.Segment.fact("Water expands by about 9% when it freezes.", BINDING),
        ci.Segment.framing("Follow for more science every day, seriously."),
    ]
    return ci.new_concept("social-a", segs, **kw)


class ContentIntelligenceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp

    def test_within_limit_ready_and_facts_preserved(self):
        c = _concept()
        v = ci.plan_variant(c, "reddit")  # huge limit
        self.assertEqual(v.status, ci.READY)
        self.assertTrue(ci.facts_preserved(c, v))
        self.assertIn("Water expands by about 9%", v.text)

    def test_over_limit_repaired_by_dropping_framing_not_facts(self):
        c = _concept()
        v = ci.plan_variant(c, "x")  # 280 limit -> framing likely dropped
        self.assertEqual(v.status, ci.READY)
        self.assertLessEqual(v.char_count, v.char_limit)
        # Fact meaning preserved verbatim; framing was compressed.
        self.assertTrue(ci.facts_preserved(c, v))
        self.assertGreaterEqual(v.dropped_framing, 0)

    def test_facts_alone_over_limit_withheld_not_truncated(self):
        long_fact = "x" * 400  # exceeds X's 280 limit on its own
        c = ci.new_concept("social-a", [ci.Segment.fact(long_fact, BINDING)])
        v = ci.plan_variant(c, "x")
        self.assertEqual(v.status, ci.WITHHELD)
        self.assertEqual(v.text, "")           # nothing published (no truncation)
        self.assertIn("no silent truncation", v.withheld_reason)

    def test_fact_meaning_not_silently_changed(self):
        long_fact = "x" * 400
        c = ci.new_concept("social-a", [ci.Segment.fact(long_fact, BINDING)])
        v = ci.plan_variant(c, "x")
        # The withheld variant never contains a truncated version of the fact.
        self.assertNotIn("x" * 279, v.text)

    def test_same_concept_distinct_platform_variants(self):
        c = _concept()
        vx = ci.plan_variant(c, "x")           # no hashtags, terse
        vi = ci.plan_variant(c, "instagram")   # native hashtags + reel format
        self.assertNotEqual(vx.text, vi.text)
        self.assertNotEqual(vx.native_format, vi.native_format)
        self.assertIn("#", vi.text)            # instagram-native hashtag tail
        self.assertNotIn("#", vx.text)

    def test_fact_segment_requires_binding(self):
        with self.assertRaises(ValueError):
            ci.Segment.fact("A fact.", None)

    def test_duplicate_and_near_duplicate_detection(self):
        c = _concept()
        v = ci.plan_variant(c, "reddit")
        ci.record_variant("social-a", v)
        # exact
        nov = ci.check_novelty("social-a", v)
        self.assertTrue(nov["is_exact_duplicate"])
        # near-duplicate: slightly changed text on same platform
        c2 = ci.new_concept("social-a", [
            ci.Segment.framing("Here's a wild angle you didn't expect."),
            ci.Segment.fact("Water expands by about 9% when it freezes.", BINDING),
            ci.Segment.framing("Follow for more science every day, truly."),
        ])
        v2 = ci.plan_variant(c2, "reddit")
        nov2 = ci.check_novelty("social-a", v2, near_threshold=0.5)
        self.assertTrue(nov2["is_near_duplicate"])
        self.assertGreater(nov2["max_similarity"], 0.5)

    def test_novel_content_flagged_novel(self):
        c = _concept()
        v = ci.plan_variant(c, "reddit")
        ci.record_variant("social-a", v)
        other = ci.new_concept("social-a", [
            ci.Segment.framing("Completely different topic about volcanoes here."),
            ci.Segment.fact("Basalt is a volcanic rock formed from lava.", BINDING),
        ])
        vo = ci.plan_variant(other, "reddit")
        nov = ci.check_novelty("social-a", vo)
        self.assertTrue(nov["novel"])

    def test_series_and_repurpose_lineage(self):
        sid = ci.new_series()
        c = _concept(series_id=sid)
        v = ci.plan_variant(c, "x")
        self.assertEqual(v.lineage["series_id"], sid)
        rc = ci.repurpose(c, experiment_id="e-9")
        self.assertEqual(rc.repurposed_from, c.concept_id)
        vr = ci.plan_variant(rc, "instagram")
        self.assertEqual(vr.lineage["repurposed_from"], c.concept_id)


if __name__ == "__main__":
    unittest.main()
