"""SB-V05-002 — claim-to-source factual support acceptance tests."""
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


class FactCheckTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp

    def test_url_present_but_unsupported_fails(self):
        receipt, ref = _verified_ref()
        claim = fc.Claim("cl-1", "The lake froze in July.", kind=fc.FACTUAL)
        # Evidence bound (URL present) but stance is UNRELATED.
        binding = fc.ClaimBinding("cl-1", fc.UNRELATED, ref)
        review = fc.review_claims([claim], [binding],
                                  {receipt.receipt_id: receipt.content_hash})
        self.assertFalse(review.passed)
        self.assertEqual(review.claim_results[0]["status"], fc.UNSUPPORTED)

    def test_conflicting_sources_yield_conflicted_and_withheld(self):
        r1, ref1 = _verified_ref(b"supports", url="https://a.org")
        r2, ref2 = _verified_ref(b"refutes", url="https://b.org")
        claim = fc.Claim("cl-2", "X causes Y.", kind=fc.FACTUAL)
        bindings = [fc.ClaimBinding("cl-2", fc.SUPPORTS, ref1),
                    fc.ClaimBinding("cl-2", fc.REFUTES, ref2)]
        hashes = {r1.receipt_id: r1.content_hash, r2.receipt_id: r2.content_hash}
        review = fc.review_claims([claim], bindings, hashes)
        self.assertFalse(review.passed)
        self.assertEqual(review.claim_results[0]["status"], fc.CONFLICTED)

    def test_supported_claim_passes_with_exact_evidence_ref(self):
        receipt, ref = _verified_ref()
        claim = fc.Claim("cl-3", "Water expands when it freezes.", kind=fc.FACTUAL)
        binding = fc.ClaimBinding("cl-3", fc.SUPPORTS, ref)
        review = fc.review_claims([claim], [binding],
                                  {receipt.receipt_id: receipt.content_hash})
        self.assertTrue(review.passed)
        res = review.claim_results[0]
        self.assertEqual(res["status"], fc.SUPPORTED)
        used = res["used_evidence"][0]
        self.assertEqual(used["receipt_id"], receipt.receipt_id)
        self.assertEqual(used["content_hash"], receipt.content_hash)
        self.assertEqual(used["source_url"], URL)

    def test_changed_source_hash_invalidates_support(self):
        receipt, ref = _verified_ref(b"original")
        claim = fc.Claim("cl-4", "Fact.", kind=fc.FACTUAL)
        binding = fc.ClaimBinding("cl-4", fc.SUPPORTS, ref)
        # The source has since changed -> different current hash.
        changed = collector.Collector(
            collector.FixtureFetcher({URL: b"rewritten"})).capture(URL)
        self.assertNotEqual(changed.content_hash, receipt.content_hash)
        review = fc.review_claims([claim], [binding],
                                  {receipt.receipt_id: changed.content_hash})
        self.assertFalse(review.passed)
        res = review.claim_results[0]
        self.assertEqual(res["status"], fc.UNSUPPORTED)
        self.assertEqual(res["stale_evidence"][0]["reason"], "stale-hash-changed")

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
        # required=False so it does not withhold, but status is UNKNOWN.
        self.assertTrue(review.passed)
        self.assertEqual(review.claim_results[0]["status"], fc.UNKNOWN)

    def test_partial_support_passes_required(self):
        receipt, ref = _verified_ref()
        claim = fc.Claim("cl-8", "Partially backed.", kind=fc.FACTUAL)
        binding = fc.ClaimBinding("cl-8", fc.PARTIAL_STANCE, ref)
        review = fc.review_claims([claim], [binding],
                                  {receipt.receipt_id: receipt.content_hash})
        self.assertTrue(review.passed)
        self.assertEqual(review.claim_results[0]["status"], fc.PARTIAL)


if __name__ == "__main__":
    unittest.main()
