"""SB-R07-053 — cultural-review evidence binding acceptance tests."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import cultural_review as cr, pipeline, personas, decision, research  # noqa: E402


def _persona_with_reviewer(reviewer="reviewer-priya-v1"):
    p = dict(personas.load("cultural-primandir-atman"))
    sr = dict(p.get("source_requirements") or {})
    sr["named_reviewer"] = reviewer
    p["source_requirements"] = sr
    return p


class CulturalReviewBindingTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp

    def test_missing_binding_fails_closed(self):
        p = _persona_with_reviewer()
        cand = pipeline.ideate(p, {
            "id": "sig-1", "title": "Practice note", "summary": "A sourced practice.",
            "source": "test", "url": "https://example.org/p", "tags": []})
        out = pipeline.cultural_review(p, cand)
        self.assertTrue(out["required"])
        self.assertFalse(out["passed"])
        self.assertEqual(out["status"], cr.UNKNOWN)

    def test_no_named_reviewer_on_persona_fails_closed(self):
        p = personas.load("cultural-primandir-atman")
        self.assertFalse(p.get("source_requirements", {}).get("named_reviewer"))
        cand = pipeline.ideate(p, {
            "id": "sig-2", "title": "Practice note", "summary": "A sourced practice.",
            "source": "test", "url": "https://example.org/p", "tags": []})
        out = pipeline.cultural_review(p, cand)
        self.assertFalse(out["passed"])
        self.assertEqual(out["status"], cr.WITHHELD)

    def test_accepted_binding_passes(self):
        p = _persona_with_reviewer("reviewer-priya-v1")
        cand = pipeline.ideate(p, {
            "id": "sig-3", "title": "Practice note", "summary": "A sourced practice.",
            "source": "test", "url": "https://example.org/p", "tags": []})
        cand["cultural_review_binding"] = cr.make_binding(
            candidate_id=cand["content_id"],
            reviewer_id="reviewer-priya-v1",
            reviewer_version="2026.09.21",
            evidence_refs=cand["source_refs"],
            status=cr.ACCEPTED,
            rationale="paraphrase-first; sources checked",
        ).as_dict()
        out = pipeline.cultural_review(p, cand)
        self.assertTrue(out["passed"])
        self.assertEqual(out["status"], cr.ACCEPTED)
        self.assertEqual(out["binding"]["reviewer_id"], "reviewer-priya-v1")
        self.assertEqual(out["binding"]["candidate_id"], cand["content_id"])

    def test_failed_status_withholds(self):
        p = _persona_with_reviewer("reviewer-priya-v1")
        cand = pipeline.ideate(p, {
            "id": "sig-4", "title": "Practice note", "summary": "A sourced practice.",
            "source": "test", "url": "https://example.org/p", "tags": []})
        cand["cultural_review_binding"] = cr.make_binding(
            candidate_id=cand["content_id"],
            reviewer_id="reviewer-priya-v1",
            reviewer_version="1",
            evidence_refs=cand["source_refs"],
            status=cr.FAILED,
            rationale="unsourced textual claim",
        ).as_dict()
        out = pipeline.cultural_review(p, cand)
        self.assertFalse(out["passed"])
        self.assertEqual(out["status"], cr.FAILED)

    def test_unknown_status_withholds(self):
        p = _persona_with_reviewer("reviewer-priya-v1")
        cand = pipeline.ideate(p, {
            "id": "sig-5", "title": "Practice note", "summary": "A sourced practice.",
            "source": "test", "url": "https://example.org/p", "tags": []})
        cand["cultural_review_binding"] = cr.make_binding(
            candidate_id=cand["content_id"],
            reviewer_id="reviewer-priya-v1",
            reviewer_version="1",
            evidence_refs=cand["source_refs"],
            status=cr.UNKNOWN,
        ).as_dict()
        out = pipeline.cultural_review(p, cand)
        self.assertFalse(out["passed"])

    def test_reviewer_mismatch_fails(self):
        p = _persona_with_reviewer("reviewer-priya-v1")
        cand = pipeline.ideate(p, {
            "id": "sig-6", "title": "Practice note", "summary": "A sourced practice.",
            "source": "test", "url": "https://example.org/p", "tags": []})
        cand["cultural_review_binding"] = cr.make_binding(
            candidate_id=cand["content_id"],
            reviewer_id="someone-else",
            reviewer_version="1",
            evidence_refs=cand["source_refs"],
            status=cr.ACCEPTED,
        ).as_dict()
        out = pipeline.cultural_review(p, cand)
        self.assertFalse(out["passed"])
        self.assertEqual(out["status"], cr.FAILED)

    def test_candidate_id_mismatch_fails(self):
        p = _persona_with_reviewer("reviewer-priya-v1")
        cand = pipeline.ideate(p, {
            "id": "sig-7", "title": "Practice note", "summary": "A sourced practice.",
            "source": "test", "url": "https://example.org/p", "tags": []})
        cand["cultural_review_binding"] = cr.make_binding(
            candidate_id="other-candidate",
            reviewer_id="reviewer-priya-v1",
            reviewer_version="1",
            evidence_refs=cand["source_refs"],
            status=cr.ACCEPTED,
        ).as_dict()
        out = pipeline.cultural_review(p, cand)
        self.assertFalse(out["passed"])

    def test_evidence_refs_must_cover_source_refs(self):
        p = _persona_with_reviewer("reviewer-priya-v1")
        cand = pipeline.ideate(p, {
            "id": "sig-8", "title": "Practice note", "summary": "A sourced practice.",
            "source": "test", "url": "https://example.org/p", "tags": []})
        cand["cultural_review_binding"] = cr.make_binding(
            candidate_id=cand["content_id"],
            reviewer_id="reviewer-priya-v1",
            reviewer_version="1",
            evidence_refs=["https://example.org/unrelated"],
            status=cr.ACCEPTED,
        ).as_dict()
        out = pipeline.cultural_review(p, cand)
        self.assertFalse(out["passed"])
        self.assertEqual(out["status"], cr.FAILED)

    def test_disguised_advertising_disallowed_invariant(self):
        p = _persona_with_reviewer("reviewer-priya-v1")
        cand = pipeline.ideate(p, {
            "id": "sig-9", "title": "Practice note", "summary": "A sourced practice.",
            "source": "test", "url": "https://example.org/p", "tags": []})
        binding = cr.make_binding(
            candidate_id=cand["content_id"],
            reviewer_id="reviewer-priya-v1",
            reviewer_version="1",
            evidence_refs=cand["source_refs"],
            status=cr.ACCEPTED,
        ).as_dict()
        binding["advertising_disallowed"] = False
        cand["cultural_review_binding"] = binding
        out = pipeline.cultural_review(p, cand)
        self.assertFalse(out["passed"])

    def test_general_persona_not_required(self):
        p = personas.load("social-a")
        cand = pipeline.ideate(p, {
            "id": "sig-g", "title": "Note", "summary": "A soft look.",
            "source": "test", "url": "https://example.org/g", "tags": []})
        out = pipeline.cultural_review(p, cand)
        self.assertFalse(out["required"])
        self.assertTrue(out["passed"])

    def test_decision_cycle_still_withholds_without_binding(self):
        bot = "social-a"
        s = research.Signal.make(
            "signal cultural", "captured evidence", "unit-test",
            "https://example.org/c", "fixture", ["hindu-practice"])
        research.capture(bot, s)
        rec = decision.run_cycle(bot, "cultural-primandir-atman")
        self.assertEqual(rec["outcome"], "withheld")
        self.assertFalse(rec["verify"]["queued"])


if __name__ == "__main__":
    unittest.main()
