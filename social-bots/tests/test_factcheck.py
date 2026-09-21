"""SB-V05-002 — claim-to-source factual support acceptance tests.

Stances come from an attributable assessor, not from caller-declared bindings.
The operational assessor here (KeywordSupportAssessor) is deterministic and
inspectable; ManualAssessor stances are explicitly non-operational/test-only.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import factcheck as fc, collector  # noqa: E402

URL = "https://example.org/study"


def _verified_ref(content=b"study body", url=URL):
    c = collector.Collector(collector.FixtureFetcher({url: content}))
    receipt = c.capture(url)
    return receipt, fc.evidence_ref_from_receipt(receipt)


def _item(ref, excerpt, span=None):
    return fc.EvidenceItem(ref=ref, excerpt=excerpt, span=span)


class FactCheckTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp
        self.assessor = fc.KeywordSupportAssessor()

    # --- URL present but unsupported fails -------------------------------- #
    def test_url_present_but_unsupported_fails(self):
        receipt, ref = _verified_ref()
        claim = fc.Claim("cl-1", "The lake froze in July.", kind=fc.FACTUAL)
        # Evidence is bound (URL present) but the excerpt is about something else.
        item = _item(ref, "This article discusses quarterly revenue figures.")
        bindings = fc.assess_bindings(claim, [item], self.assessor)
        self.assertEqual(bindings[0].stance, fc.UNRELATED)
        review = fc.review_claims([claim], bindings,
                                  {receipt.receipt_id: receipt.content_hash})
        self.assertFalse(review.passed)
        self.assertEqual(review.claim_results[0]["status"], fc.UNSUPPORTED)

    # --- conflicting sources -> CONFLICTED/withheld ----------------------- #
    def test_conflicting_sources_yield_conflicted_and_withheld(self):
        r1, ref1 = _verified_ref(b"supports", url="https://a.org")
        r2, ref2 = _verified_ref(b"refutes", url="https://b.org")
        claim = fc.Claim("cl-2", "Vaccines reduce transmission.", kind=fc.FACTUAL)
        items = [_item(ref1, "Vaccines reduce transmission across the cohort."),
                 _item(ref2, "There is no evidence vaccines reduce transmission.")]
        bindings = fc.assess_bindings(claim, items, self.assessor)
        stances = {b.stance for b in bindings}
        self.assertIn(fc.SUPPORTS, stances)
        self.assertIn(fc.REFUTES, stances)
        hashes = {r1.receipt_id: r1.content_hash, r2.receipt_id: r2.content_hash}
        review = fc.review_claims([claim], bindings, hashes)
        self.assertFalse(review.passed)
        self.assertEqual(review.claim_results[0]["status"], fc.CONFLICTED)

    # --- supported claim passes with exact evidence ref ------------------- #
    def test_supported_claim_passes_with_exact_evidence_ref(self):
        receipt, ref = _verified_ref()
        claim = fc.Claim("cl-3", "Water expands when it freezes.", kind=fc.FACTUAL)
        item = _item(ref, "Laboratory results show water expands when it freezes.")
        bindings = fc.assess_bindings(claim, [item], self.assessor)
        review = fc.review_claims([claim], bindings,
                                  {receipt.receipt_id: receipt.content_hash})
        self.assertTrue(review.passed)
        res = review.claim_results[0]
        self.assertEqual(res["status"], fc.SUPPORTED)
        used = res["used_evidence"][0]
        self.assertEqual(used["receipt_id"], receipt.receipt_id)
        self.assertEqual(used["content_hash"], receipt.content_hash)
        self.assertEqual(used["source_url"], URL)
        # The passing support is attributed to the operational assessor.
        self.assertIn("keyword-support-assessor@1.0.0", res["assessors"])

    # --- caller cannot assert operational support directly ---------------- #
    def test_caller_declared_stance_is_not_operational_support(self):
        """A ManualAssessor SUPPORTS stance is non-operational and must NOT let a
        required factual claim pass — the core SB-V05-002 repair contract."""
        receipt, ref = _verified_ref()
        claim = fc.Claim("cl-m", "Sales tripled last quarter.", kind=fc.FACTUAL)
        manual = fc.ManualAssessor({claim.id: fc.SUPPORTS})
        bindings = fc.assess_bindings(claim, [_item(ref, "irrelevant")], manual)
        self.assertFalse(bindings[0].operational)
        review = fc.review_claims([claim], bindings,
                                  {receipt.receipt_id: receipt.content_hash})
        self.assertFalse(review.passed)
        res = review.claim_results[0]
        self.assertEqual(res["status"], fc.UNKNOWN)
        self.assertTrue(res["non_operational_evidence"])

    def test_manual_assessor_not_registered_operational(self):
        self.assertFalse(fc.is_operational_assessor(fc.ManualAssessor({})))
        self.assertTrue(fc.is_operational_assessor(fc.KeywordSupportAssessor()))

    # --- changed source hash invalidates stale support -------------------- #
    def test_changed_source_hash_invalidates_support(self):
        receipt, ref = _verified_ref(b"original")
        claim = fc.Claim("cl-4", "The bridge spans 500 meters.", kind=fc.FACTUAL)
        item = _item(ref, "The bridge spans 500 meters over the river.")
        bindings = fc.assess_bindings(claim, [item], self.assessor)
        # The source has since changed -> different current hash.
        changed = collector.Collector(
            collector.FixtureFetcher({URL: b"rewritten"})).capture(URL)
        self.assertNotEqual(changed.content_hash, receipt.content_hash)
        review = fc.review_claims([claim], bindings,
                                  {receipt.receipt_id: changed.content_hash})
        self.assertFalse(review.passed)
        res = review.claim_results[0]
        self.assertEqual(res["status"], fc.UNSUPPORTED)
        self.assertEqual(res["stale_evidence"][0]["reason"], "stale-hash-changed")

    # --- opinion / creative not gated ------------------------------------ #
    def test_opinion_and_creative_not_gated(self):
        claim_op = fc.Claim("cl-5", "This is the best tool.", kind=fc.OPINION)
        claim_cr = fc.Claim("cl-6", "Once upon a time...", kind=fc.CREATIVE)
        review = fc.review_claims([claim_op, claim_cr], [], {})
        self.assertTrue(review.passed)  # not evidence-gated
        self.assertEqual(review.claim_results[0]["status"], fc.UNKNOWN)

    def test_unverified_evidence_cannot_be_bound(self):
        failed = collector.Collector(collector.FixtureFetcher({})).capture(URL)
        with self.assertRaises(ValueError):
            fc.evidence_ref_from_receipt(failed)

    def test_unknown_when_no_evidence(self):
        claim = fc.Claim("cl-7", "Unbacked fact.", kind=fc.FACTUAL, required=False)
        review = fc.review_claims([claim], [], {})
        self.assertTrue(review.passed)  # required=False so no withhold
        self.assertEqual(review.claim_results[0]["status"], fc.UNKNOWN)

    def test_partial_support_passes_required(self):
        receipt, ref = _verified_ref()
        claim = fc.Claim("cl-8", "Solar capacity doubled worldwide.", kind=fc.FACTUAL)
        # Excerpt contains some but not all key terms -> PARTIAL.
        item = _item(ref, "Solar capacity rose sharply this year.")
        bindings = fc.assess_bindings(claim, [item], self.assessor)
        self.assertEqual(bindings[0].stance, fc.PARTIAL_STANCE)
        review = fc.review_claims([claim], bindings,
                                  {receipt.receipt_id: receipt.content_hash})
        self.assertTrue(review.passed)
        self.assertEqual(review.claim_results[0]["status"], fc.PARTIAL)

    # --- material-claim identification (LEAD-014) ------------------------- #
    def test_material_claim_identification_finds_factual_sentences(self):
        ex = fc.HeuristicClaimExtractor()
        text = ("Our product launched in 2021. We think it looks amazing. "
                "Revenue grew 40 percent.")
        claims = ex.identify(text)
        kinds = {c.kind for c in claims}
        self.assertIn(fc.FACTUAL, kinds)
        self.assertIn(fc.OPINION, kinds)
        factual = [c for c in claims if c.kind == fc.FACTUAL]
        self.assertEqual(len(factual), 2)  # the 2021 claim and the 40 percent claim

    def test_omitted_material_claim_cannot_bypass_review(self):
        """A candidate whose text contains a material factual claim the caller
        did NOT enumerate is still identified and gated."""
        text = "Trust us, it's great. Sales grew 300 percent in 2023."
        # Caller enumerates NOTHING factual (tries to bypass review).
        review = fc.review_candidate(text, caller_claims=[], bindings=[],
                                     current_hashes={})
        self.assertFalse(review.passed)
        self.assertTrue(review.identified_claims)
        # The added claim resolved to UNKNOWN and withheld the candidate.
        self.assertTrue(any(r["status"] == fc.UNKNOWN
                            for r in review.claim_results))

    def test_review_candidate_passes_when_identified_claim_is_supported(self):
        receipt, ref = _verified_ref()
        text = "The satellite reached orbit in 2022."
        # Identify the claim the caller omitted, then support it operationally.
        final, added = fc.reconcile_claims([], text)
        self.assertEqual(len(added), 1)
        auto = added[0]
        item = _item(ref, "Records confirm the satellite reached orbit in 2022.")
        bindings = fc.assess_bindings(auto, [item], self.assessor)
        review = fc.review_candidate(text, caller_claims=[], bindings=bindings,
                                     current_hashes={receipt.receipt_id: receipt.content_hash})
        self.assertTrue(review.passed)

    def test_caller_claim_covers_identified_avoids_duplicate(self):
        text = "Revenue grew 40 percent in 2023."
        caller = [fc.Claim("c-rev", "Revenue grew 40 percent in 2023.", kind=fc.FACTUAL)]
        final, added = fc.reconcile_claims(caller, text)
        self.assertEqual(added, [])  # caller already covers it
        self.assertEqual(len(final), 1)


if __name__ == "__main__":
    unittest.main()
