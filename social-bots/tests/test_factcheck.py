"""SB-R07-051 / SB-V05-002 — claim-to-source factual support acceptance tests.

Closed operational route: BoundedPropositionAssessor (policy-owned; no public
registration). KeywordSupportAssessor remains diagnostic/test-only. Adversarial
negation/relation/numeric/predicate cases must not become SUPPORTS.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import factcheck as fc, collector, pipeline, personas  # noqa: E402

URL = "https://example.org/study"


def _fixture_ref(content=b"study body", url=URL):
    c = collector.Collector(collector.FixtureFetcher({url: content}))
    receipt = c.capture(url)
    return receipt, fc.evidence_ref_from_receipt(receipt)


def _trusted_ref(receipt_id="cap-op", content_hash="hash-op", url=URL):
    return fc.EvidenceRef(
        receipt_id=receipt_id, source_url=url, content_hash=content_hash,
        retrieved_at="2026-01-01T00:00:00+00:00",
        evidence_class=fc.EVIDENCE_TRUSTED_OPERATIONAL)


def _op(claim_id, stance, ref, excerpt="e"):
    return fc.SupportAssessment(
        claim_id=claim_id, stance=stance, evidence=ref, excerpt=excerpt, span=None,
        assessor_name="core-semantic-assessor", assessor_version="x",
        operational=True, rationale="core")


class TrustBoundaryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp
        self.diag = fc.KeywordSupportAssessor()
        self.op = fc.default_operational_assessor()

    def test_no_public_operational_registration_api(self):
        self.assertFalse(hasattr(fc, "register_operational_assessor"))

    def test_keyword_assessor_is_diagnostic_not_operational(self):
        self.assertFalse(self.diag.operational)
        self.assertFalse(fc.is_operational_assessor(self.diag))

    def test_bounded_assessor_is_policy_owned_operational(self):
        self.assertTrue(self.op.operational)
        self.assertTrue(fc.is_operational_assessor(self.op))
        self.assertIs(type(self.op), fc.BoundedPropositionAssessor)

    def test_caller_subclass_cannot_self_grant_operational(self):
        class FakeOp(fc.BoundedPropositionAssessor):
            name = "fake"
            operational = True

        fake = FakeOp()
        self.assertFalse(fc.is_operational_assessor(fake))

    def test_diagnostic_assessor_fails_closed(self):
        _, ref = _fixture_ref()
        claim = fc.Claim("cl", "Water expands when it freezes.")
        item = fc.EvidenceItem(ref, "Tests show water expands when it freezes.")
        bindings = fc.assess_bindings(claim, [item], self.diag)
        self.assertFalse(bindings[0].operational)
        review = fc.review_claims([claim], bindings, {ref.receipt_id: ref.content_hash})
        self.assertFalse(review.passed)
        self.assertEqual(review.claim_results[0]["status"], fc.UNKNOWN)

    def test_operational_stance_requires_trusted_operational_evidence(self):
        _, fx_ref = _fixture_ref()
        self.assertEqual(fx_ref.evidence_class, fc.EVIDENCE_FIXTURE)
        claim = fc.Claim("c", "Water expands when it freezes.")
        item = fc.EvidenceItem(fx_ref, "Water expands when it freezes in winter ice.")
        b = fc.assess_bindings(claim, [item], self.op)
        self.assertFalse(b[0].operational)
        review = fc.review_claims([claim], b, {fx_ref.receipt_id: fx_ref.content_hash})
        self.assertFalse(review.passed)
        self.assertEqual(review.claim_results[0]["status"], fc.UNKNOWN)

    def test_constructing_support_assessment_operational_true_is_not_enough(self):
        """Caller-built SupportAssessment(operational=True) is ignored unless
        produced through assess_bindings with a policy assessor + trusted ref.
        review_claims trusts the flag on the object — so pipeline must only
        accept bindings from assess_bindings. Prove assess_bindings clears it
        for non-policy assessors."""
        ref = _trusted_ref()
        claim = fc.Claim("c", "Sales grew 40 percent.")
        manual = fc.ManualAssessor({claim.id: fc.SUPPORTS})
        b = fc.assess_bindings(claim, [fc.EvidenceItem(ref, "Sales grew 40 percent.")],
                               manual)
        self.assertFalse(b[0].operational)


class OperationalGatingTest(unittest.TestCase):
    def test_supported_passes_with_exact_evidence_ref(self):
        ref = _trusted_ref()
        claim = fc.Claim("cl-3", "Water expands when it freezes.")
        b = [_op(claim.id, fc.SUPPORTS, ref)]
        review = fc.review_claims([claim], b, {ref.receipt_id: ref.content_hash})
        self.assertTrue(review.passed)
        self.assertEqual(review.claim_results[0]["status"], fc.SUPPORTED)

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

    def test_changed_source_hash_invalidates_support(self):
        ref = _trusted_ref("cap-c", "original-hash")
        claim = fc.Claim("cl-4", "The bridge spans 500 meters.")
        b = [_op(claim.id, fc.SUPPORTS, ref)]
        review = fc.review_claims([claim], b, {ref.receipt_id: "changed-hash"})
        self.assertFalse(review.passed)
        self.assertEqual(review.claim_results[0]["stale_evidence"][0]["reason"],
                         "stale-hash-changed")

    def test_opinion_and_creative_not_gated(self):
        claim_op = fc.Claim("cl-5", "This is the best tool.", kind=fc.OPINION)
        claim_cr = fc.Claim("cl-6", "Once upon a time...", kind=fc.CREATIVE)
        review = fc.review_claims([claim_op, claim_cr], [], {})
        self.assertTrue(review.passed)

    def test_omitted_material_claim_cannot_bypass_review(self):
        text = "Trust us, it's great. Sales grew 300 percent in 2023."
        review = fc.review_candidate(text, caller_claims=[], bindings=[],
                                     current_hashes={})
        self.assertFalse(review.passed)
        self.assertTrue(review.identified_claims)


class AdversarialBoundedAssessorTest(unittest.TestCase):
    """Packet-required adversarial cases for the closed operational assessor."""

    def setUp(self):
        self.assessor = fc.default_operational_assessor()
        self.ref = _trusted_ref()

    def _stance(self, claim_text, excerpt):
        claim = fc.Claim("c", claim_text)
        item = fc.EvidenceItem(self.ref, excerpt)
        return self.assessor.assess(claim, item)

    def test_negation_same_key_terms_is_not_supports(self):
        stance = self._stance(
            "Coffee causes cancer.",
            "Large studies found coffee does not cause cancer in humans.")
        self.assertIn(stance, {fc.REFUTES, fc.UNRELATED, fc.PARTIAL_STANCE})
        self.assertNotEqual(stance, fc.SUPPORTS)

    def test_unrelated_relation_same_key_terms_is_not_supports(self):
        stance = self._stance(
            "Acme causes pollution.",
            "Acme owns a pollution-monitoring subsidiary in Ohio.")
        self.assertIn(stance, {fc.UNRELATED, fc.PARTIAL_STANCE, fc.REFUTES})
        self.assertNotEqual(stance, fc.SUPPORTS)

    def test_numeric_date_mismatch_is_not_supports(self):
        stance = self._stance(
            "Revenue grew 40 percent in 2023.",
            "Revenue grew 12 percent in 2021 according to filings.")
        self.assertIn(stance, {fc.REFUTES, fc.UNRELATED})
        self.assertNotEqual(stance, fc.SUPPORTS)

    def test_missing_predicate_is_not_supports(self):
        stance = self._stance(
            "Nimbus launched the satellite.",
            "Nimbus discussed satellites at a press event.")
        self.assertIn(stance, {fc.UNRELATED, fc.PARTIAL_STANCE})
        self.assertNotEqual(stance, fc.SUPPORTS)

    def test_supporting_excerpt_yields_supports(self):
        stance = self._stance(
            "Water expands when it freezes.",
            "Lab tests confirm water expands when it freezes into ice.")
        self.assertEqual(stance, fc.SUPPORTS)

    def test_conflicting_evidence_withholds(self):
        claim = fc.Claim("c", "WidgetX increases throughput.")
        r1, r2 = _trusted_ref("a", "ha"), _trusted_ref("b", "hb")
        items = [
            fc.EvidenceItem(r1, "Benchmarks show WidgetX increases throughput."),
            fc.EvidenceItem(r2, "Benchmarks show WidgetX does not increase throughput."),
        ]
        b = fc.assess_bindings(claim, items, self.assessor)
        self.assertTrue(all(x.operational for x in b))
        review = fc.review_claims(
            [claim], b,
            {r1.receipt_id: r1.content_hash, r2.receipt_id: r2.content_hash})
        self.assertFalse(review.passed)
        self.assertEqual(review.claim_results[0]["status"], fc.CONFLICTED)

    def test_operational_bindings_pass_end_to_end(self):
        ref = _trusted_ref()
        claim = fc.Claim("cl", "Water expands when it freezes.")
        item = fc.EvidenceItem(ref, "Evidence: water expands when it freezes.")
        b = fc.assess_bindings(claim, [item], self.assessor)
        self.assertTrue(b[0].operational)
        self.assertEqual(b[0].stance, fc.SUPPORTS)
        review = fc.review_claims([claim], b, {ref.receipt_id: ref.content_hash})
        self.assertTrue(review.passed)


class PipelineIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp

    def test_pipeline_no_material_claims_still_requires_source_ref(self):
        p = personas.load("social-a")
        cand = pipeline.ideate(p, {
            "id": "sig-x", "title": "Quiet note", "summary": "A soft look at tide pools.",
            "source": "test", "url": "https://example.org/pools", "tags": []})
        out = pipeline.fact_check(p, cand)
        self.assertTrue(out["passed"])
        self.assertEqual(out["mode"], "no-material-claims")

    def test_pipeline_material_claim_without_trusted_evidence_withholds(self):
        p = personas.load("social-a")
        cand = pipeline.ideate(p, {
            "id": "sig-y", "title": "Revenue note",
            "summary": "Revenue grew 40 percent in 2023.",
            "source": "test", "url": "https://example.org/rev", "tags": []})
        out = pipeline.fact_check(p, cand)
        self.assertFalse(out["passed"])
        self.assertEqual(out["mode"], "claim-to-source")

    def test_pipeline_operational_evidence_supports_claim(self):
        p = personas.load("social-a")
        ref = _trusted_ref()
        # Include an explicit year so the heuristic marks a material claim.
        cand = pipeline.ideate(p, {
            "id": "sig-z", "title": "Physics note",
            "summary": "Studies confirmed water expands when it freezes in 2020.",
            "source": "test", "url": URL, "tags": []})
        cand["evidence_items"] = [
            fc.EvidenceItem(
                ref,
                "Studies confirmed water expands when it freezes in 2020.")]
        out = pipeline.fact_check(p, cand)
        self.assertTrue(out["passed"], out)
        self.assertEqual(out["mode"], "claim-to-source")
        self.assertTrue(out["operational"])

    def test_pipeline_fixture_evidence_cannot_operationally_pass(self):
        p = personas.load("social-a")
        _, fx = _fixture_ref(
            b"Studies confirmed water expands when it freezes in 2020.")
        cand = pipeline.ideate(p, {
            "id": "sig-fx", "title": "Physics note",
            "summary": "Studies confirmed water expands when it freezes in 2020.",
            "source": "test", "url": URL, "tags": []})
        cand["evidence_items"] = [
            fc.EvidenceItem(
                fx,
                "Studies confirmed water expands when it freezes in 2020.")]
        out = pipeline.fact_check(p, cand)
        self.assertFalse(out["passed"])
        self.assertEqual(out["mode"], "claim-to-source")


if __name__ == "__main__":
    unittest.main()
