"""SB-V05-002 — claim-to-source factual support acceptance tests.

Stances come from an attributable assessor. The bundled KeywordSupportAssessor
is DIAGNOSTIC/test-only (non-operational). Operational support must come from a
policy-owned assessor over trusted-operational evidence — none is bundled, so the
system fails closed. Gating logic for operational assessments is exercised by
constructing operational SupportAssessment values directly (representing what the
Core adaptive provider will supply).
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import factcheck as fc, collector  # noqa: E402

URL = "https://example.org/study"


def _fixture_ref(content=b"study body", url=URL):
    c = collector.Collector(collector.FixtureFetcher({url: content}))
    receipt = c.capture(url)
    return receipt, fc.evidence_ref_from_receipt(receipt)


def _trusted_ref(receipt_id="cap-op", content_hash="hash-op"):
    """A ref whose evidence is trusted-operational (as Core would supply)."""
    return fc.EvidenceRef(receipt_id=receipt_id, source_url=URL,
                          content_hash=content_hash, retrieved_at="2026-01-01T00:00:00+00:00",
                          evidence_class=fc.EVIDENCE_TRUSTED_OPERATIONAL)


def _op(claim_id, stance, ref, excerpt="e"):
    """An OPERATIONAL support assessment (what the Core provider yields)."""
    return fc.SupportAssessment(
        claim_id=claim_id, stance=stance, evidence=ref, excerpt=excerpt, span=None,
        assessor_name="core-semantic-assessor", assessor_version="x",
        operational=True, rationale="core")


class FactCheckTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp
        self.diag = fc.KeywordSupportAssessor()

    # --- built-ins are diagnostic / fail closed --------------------------- #
    def test_bundled_assessor_is_diagnostic_not_operational(self):
        self.assertFalse(self.diag.operational)
        self.assertFalse(fc.is_operational_assessor(self.diag))

    def test_no_public_operational_registration_api(self):
        self.assertFalse(hasattr(fc, "register_operational_assessor"))

    def test_diagnostic_assessor_fails_closed(self):
        """No operational assessor bundled => a required factual claim is
        withheld even when the diagnostic assessor says SUPPORTS."""
        _, ref = _fixture_ref()
        claim = fc.Claim("cl", "Water expands when it freezes.")
        item = fc.EvidenceItem(ref, "Tests show water expands when it freezes.")
        bindings = fc.assess_bindings(claim, [item], self.diag)
        self.assertEqual(bindings[0].stance, fc.SUPPORTS)
        self.assertFalse(bindings[0].operational)  # fail closed
        review = fc.review_claims([claim], bindings, {ref.receipt_id: ref.content_hash})
        self.assertFalse(review.passed)
        self.assertEqual(review.claim_results[0]["status"], fc.UNKNOWN)

    def test_operational_stance_requires_trusted_operational_evidence(self):
        """Even a (hypothetical) operational assessor over FIXTURE evidence does
        not yield operational support: fixtures are test-only."""
        _, fx_ref = _fixture_ref()
        self.assertEqual(fx_ref.evidence_class, fc.EVIDENCE_FIXTURE)
        # Build the binding as assess_bindings would, but assessor is diagnostic.
        b = fc.assess_bindings(fc.Claim("c", "x"),
                               [fc.EvidenceItem(fx_ref, "x")], self.diag)
        self.assertFalse(b[0].operational)

    # --- operational gating logic (Core-provider assessments) ------------- #
    def test_supported_passes_with_exact_evidence_ref(self):
        ref = _trusted_ref()
        claim = fc.Claim("cl-3", "Water expands when it freezes.")
        b = [_op(claim.id, fc.SUPPORTS, ref)]
        review = fc.review_claims([claim], b, {ref.receipt_id: ref.content_hash})
        self.assertTrue(review.passed)
        res = review.claim_results[0]
        self.assertEqual(res["status"], fc.SUPPORTED)
        self.assertEqual(res["used_evidence"][0]["receipt_id"], ref.receipt_id)

    def test_url_present_but_unsupported_fails(self):
        ref = _trusted_ref()
        claim = fc.Claim("cl-1", "The lake froze in July.")
        b = [_op(claim.id, fc.UNRELATED, ref)]
        review = fc.review_claims([claim], b, {ref.receipt_id: ref.content_hash})
        self.assertFalse(review.passed)
        self.assertEqual(review.claim_results[0]["status"], fc.UNSUPPORTED)

    def test_conflicting_sources_yield_conflicted(self):
        r1, r2 = _trusted_ref("cap-a", "h-a"), _trusted_ref("cap-b", "h-b")
        claim = fc.Claim("cl-2", "X causes Y.")
        b = [_op(claim.id, fc.SUPPORTS, r1), _op(claim.id, fc.REFUTES, r2)]
        hashes = {r1.receipt_id: r1.content_hash, r2.receipt_id: r2.content_hash}
        review = fc.review_claims([claim], b, hashes)
        self.assertFalse(review.passed)
        self.assertEqual(review.claim_results[0]["status"], fc.CONFLICTED)

    def test_partial_support_passes(self):
        ref = _trusted_ref()
        claim = fc.Claim("cl-8", "Solar capacity doubled.")
        b = [_op(claim.id, fc.PARTIAL_STANCE, ref)]
        review = fc.review_claims([claim], b, {ref.receipt_id: ref.content_hash})
        self.assertTrue(review.passed)
        self.assertEqual(review.claim_results[0]["status"], fc.PARTIAL)

    def test_changed_source_hash_invalidates_support(self):
        ref = _trusted_ref("cap-c", "original-hash")
        claim = fc.Claim("cl-4", "The bridge spans 500 meters.")
        b = [_op(claim.id, fc.SUPPORTS, ref)]
        # Source changed -> current hash differs.
        review = fc.review_claims([claim], b, {ref.receipt_id: "changed-hash"})
        self.assertFalse(review.passed)
        res = review.claim_results[0]
        self.assertEqual(res["status"], fc.UNSUPPORTED)
        self.assertEqual(res["stale_evidence"][0]["reason"], "stale-hash-changed")

    def test_manual_assessor_is_non_operational(self):
        ref = _trusted_ref()
        claim = fc.Claim("cl-m", "Sales tripled.")
        manual = fc.ManualAssessor({claim.id: fc.SUPPORTS})
        b = fc.assess_bindings(claim, [fc.EvidenceItem(ref, "x")], manual)
        self.assertFalse(b[0].operational)
        review = fc.review_claims([claim], b, {ref.receipt_id: ref.content_hash})
        self.assertFalse(review.passed)
        self.assertEqual(review.claim_results[0]["status"], fc.UNKNOWN)

    # --- opinion / creative not gated ------------------------------------ #
    def test_opinion_and_creative_not_gated(self):
        claim_op = fc.Claim("cl-5", "This is the best tool.", kind=fc.OPINION)
        claim_cr = fc.Claim("cl-6", "Once upon a time...", kind=fc.CREATIVE)
        review = fc.review_claims([claim_op, claim_cr], [], {})
        self.assertTrue(review.passed)
        self.assertEqual(review.claim_results[0]["status"], fc.UNKNOWN)

    def test_unverified_evidence_cannot_be_bound(self):
        failed = collector.Collector(collector.FixtureFetcher({})).capture(URL)
        with self.assertRaises(ValueError):
            fc.evidence_ref_from_receipt(failed)

    def test_unknown_when_no_evidence(self):
        claim = fc.Claim("cl-7", "Unbacked fact.", required=False)
        review = fc.review_claims([claim], [], {})
        self.assertTrue(review.passed)
        self.assertEqual(review.claim_results[0]["status"], fc.UNKNOWN)

    # --- material-claim identification (LEAD-014) ------------------------- #
    def test_material_claim_identification_finds_factual_sentences(self):
        ex = fc.HeuristicClaimExtractor()
        text = ("Our product launched in 2021. We think it looks amazing. "
                "Revenue grew 40 percent.")
        claims = ex.identify(text)
        kinds = {c.kind for c in claims}
        self.assertIn(fc.FACTUAL, kinds)
        self.assertIn(fc.OPINION, kinds)
        self.assertEqual(len([c for c in claims if c.kind == fc.FACTUAL]), 2)

    def test_omitted_material_claim_cannot_bypass_review(self):
        text = "Trust us, it's great. Sales grew 300 percent in 2023."
        review = fc.review_candidate(text, caller_claims=[], bindings=[],
                                     current_hashes={})
        self.assertFalse(review.passed)
        self.assertTrue(review.identified_claims)
        self.assertTrue(any(r["status"] == fc.UNKNOWN
                            for r in review.claim_results))

    def test_review_candidate_passes_only_with_operational_support(self):
        ref = _trusted_ref()
        text = "The satellite reached orbit in 2022."
        final, added = fc.reconcile_claims([], text)
        self.assertEqual(len(added), 1)
        auto = added[0]
        b = [_op(auto.id, fc.SUPPORTS, ref)]
        review = fc.review_candidate(text, caller_claims=[], bindings=b,
                                     current_hashes={ref.receipt_id: ref.content_hash})
        self.assertTrue(review.passed)

    def test_caller_claim_covers_identified_avoids_duplicate(self):
        text = "Revenue grew 40 percent in 2023."
        caller = [fc.Claim("c-rev", "Revenue grew 40 percent in 2023.")]
        final, added = fc.reconcile_claims(caller, text)
        self.assertEqual(added, [])
        self.assertEqual(len(final), 1)


if __name__ == "__main__":
    unittest.main()
