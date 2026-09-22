"""Mechanical regressions for the separate final-review receipt anchor."""
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from runtime import cultural_review as cr
from runtime import paths, personas, pipeline
from tests.test_review_binding import SIGNAL, _Case


class ReviewReceiptAnchorRegression(_Case):
    def _entry(self):
        self.bind()
        return pipeline.enqueue("social-a", self.cand, self.payload, "exp-1")

    def test_recomputed_queue_hashes_and_pass_flag_cannot_replace_reviewed_text(self):
        entry = self._entry()
        entry["payload"]["text"] = "replacement text never reviewed"
        digest = pipeline.text_digest(entry["payload"]["text"])
        entry["final_text_sha256"] = digest
        entry["review_binding"]["final_text_sha256"] = digest
        entry["review_binding"]["passed"] = True
        verdict = pipeline.verify_queued_entry("social-a", entry)
        self.assertFalse(verdict["verified"], verdict)
        self.assertTrue(any("receipt" in p for p in verdict["problems"]), verdict)

    def test_cross_scope_receipt_reference_is_refused(self):
        entry_a = self._entry()
        other = dict(entry_a)
        other["bot"] = "social-b"
        other["review_binding"] = dict(entry_a["review_binding"], bot="social-b")
        verdict = pipeline.verify_queued_entry("social-b", other)
        self.assertFalse(verdict["verified"], verdict)
        self.assertTrue(any("receipt" in p for p in verdict["problems"]), verdict)

    def test_missing_and_malformed_receipt_fail_closed(self):
        for mode in ("missing", "malformed"):
            with self.subTest(mode=mode):
                entry = self._entry()
                rid = entry["review_binding"]["review_receipt_id"]
                receipt = paths.receipts_dir("social-a") / f"{rid}.json"
                if mode == "missing":
                    receipt.unlink()
                else:
                    receipt.write_text("{not json", encoding="utf-8")
                verdict = pipeline.verify_queued_entry("social-a", entry)
                self.assertFalse(verdict["verified"], verdict)
                self.assertTrue(any("receipt" in p for p in verdict["problems"]), verdict)

    def test_symlinked_receipt_is_refused(self):
        entry = self._entry()
        rid = entry["review_binding"]["review_receipt_id"]
        receipt = paths.receipts_dir("social-a") / f"{rid}.json"
        target = Path(self.tmp) / "copied-receipt.json"
        target.write_bytes(receipt.read_bytes())
        receipt.unlink()
        receipt.symlink_to(target)
        verdict = pipeline.verify_queued_entry("social-a", entry)
        self.assertFalse(verdict["verified"], verdict)
        self.assertTrue(any("symlink" in p for p in verdict["problems"]), verdict)


class CulturalAttributionReceiptRegression(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.previous = os.environ.get("SBOTS_HOME")
        os.environ["SBOTS_HOME"] = self.tmp

    def tearDown(self):
        if self.previous is None:
            os.environ.pop("SBOTS_HOME", None)
        else:
            os.environ["SBOTS_HOME"] = self.previous

    def test_cultural_reviewer_mutation_breaks_receipt_anchor(self):
        persona = personas.load("cultural-primandir-atman")
        persona.setdefault("source_requirements", {})["named_reviewer"] = "reviewer-fixture"
        candidate = pipeline.ideate(persona, SIGNAL)
        platform = persona["platform_strategy"]["primary"][0]
        rendered = pipeline.format_for_platform(candidate, platform)["text"]
        candidate["cultural_review_binding"] = cr.make_binding(
            candidate_id=candidate["content_id"], reviewer_id="reviewer-fixture",
            reviewer_version="1", evidence_refs=candidate["source_refs"],
            status=cr.ACCEPTED, rationale="fixture",
            content_sha256=hashlib.sha256(rendered.encode()).hexdigest()).as_dict()
        candidate = pipeline.review(persona, candidate)
        payload = pipeline.format_for_platform(candidate, platform)
        pipeline.final_review(persona, candidate, payload)
        entry = pipeline.enqueue("social-a", candidate, payload, "exp-cultural")
        entry["review_binding"]["cultural_review_binding"]["reviewer_id"] = "other-reviewer"
        verdict = pipeline.verify_queued_entry("social-a", entry)
        self.assertFalse(verdict["verified"], verdict)
        self.assertTrue(any("receipt" in p for p in verdict["problems"]), verdict)


if __name__ == "__main__":
    unittest.main()
