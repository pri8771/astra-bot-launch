"""SB-R07-044 — independent divergence acceptance verifier.

ENGINEERING-ONLY: no live model call. Fixtures and self-declared labels must be
rejected for acceptance-path claims; missing live receipts yield INCOMPLETE.
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import authorization, divergence_prepare as dp  # noqa: E402
from runtime import divergence_verifier as dv  # noqa: E402
from runtime import reasoning_receipt as rr  # noqa: E402

from tests.test_v04_divergence_prepare import (  # noqa: E402
    PERSONAS, build as build_matrix, default_snapshots, receipt_for,
)


class IndependentVerifierTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.matrix = build_matrix()  # engineering-fixture snapshots by default

    def test_required_comparisons_are_exactly_the_plan_set(self):
        """P0|P1, P0|P2, P0|P3 persona and P0|E0 evidence must be required."""
        expected = [("P0", "P1", "persona"), ("P0", "P2", "persona"),
                    ("P0", "P3", "persona"), ("P0", "E0", "evidence")]
        self.assertEqual(list(dp.REQUIRED_COMPARISONS), expected)
        result = dv.verify(self.matrix, {})
        self.assertEqual(result["required_comparisons"], [list(c) for c in expected])
        self.assertTrue(result["required_comparisons_present"])
        self.assertFalse(result["acceptance_claim"])

    def test_seam_fixtures_are_rejected(self):
        """Synthetic seam fixtures must never produce an acceptance-path verdict."""
        receipts = {}
        for index, case in enumerate(self.matrix.cases):
            receipts[case.case_id] = receipt_for(
                case, recommended="CREATE_CANDIDATE" if index else "RESEARCH_MORE",
                bump=0.05 * index)
        result = dv.verify(self.matrix, receipts)
        self.assertEqual(result["verdict"], dv.VERDICT_REJECTED)
        self.assertTrue(any("seam fixture" in r for r in result["independent_rejections"]))
        self.assertFalse(result["acceptance_claim"])

    def test_self_declared_real_labels_without_ledger_are_incomplete(self):
        """Writing sanitized-real-canary into JSON is not provenance."""
        snaps = default_snapshots()
        for sid in ("E1", "E2"):
            snaps[sid].provenance_label = dp.LIVE_CAPTURE
        matrix = build_matrix(snapshots=snaps)
        receipts = {}
        for index, case in enumerate(matrix.cases):
            receipt = receipt_for(
                case, recommended="CREATE_CANDIDATE" if index else "RESEARCH_MORE",
                bump=0.05 * index)
            receipt["receipt_kind"] = rr.REAL_CANARY_KIND
            receipt["provider_id"] = "claude-code-subscription-v1"
            receipts[case.case_id] = receipt
        result = dv.verify(matrix, receipts)  # no budget
        self.assertEqual(result["verdict"], dv.VERDICT_INCOMPLETE)
        self.assertTrue(result["self_declared_real_labels_alone"])
        self.assertFalse(result["ledger_bound"])
        self.assertFalse(result["acceptance_claim"])

    def test_ledger_bound_material_still_does_not_self_accept(self):
        """Even a fully bound engineering bundle never claims ACCEPTED."""
        snaps = default_snapshots()
        for sid in ("E1", "E2"):
            snaps[sid].provenance_label = dp.LIVE_CAPTURE
        matrix = build_matrix(snapshots=snaps)
        receipts = {}
        for index, case in enumerate(matrix.cases):
            receipt = receipt_for(
                case, recommended="CREATE_CANDIDATE" if index else "RESEARCH_MORE",
                bump=0.05 * index)
            receipt["receipt_kind"] = rr.REAL_CANARY_KIND
            receipt["provider_id"] = "claude-code-subscription-v1"
            receipts[case.case_id] = receipt
        budget = authorization.CallBudget(matrix.run_scope, 5, home=self.tmp)
        for case in matrix.cases:
            slot = budget.reserve(manifest_id="AUTH-FIXTURE-0001",
                                  manifest_digest="sha256:fixture", lane="windows-core",
                                  artifact="SB-V04-002",
                                  context_digest=case.context_sha256)
            budget.record_outcome(slot, "proposal_received")
        result = dv.verify(matrix, receipts, budget=budget)
        self.assertEqual(result["verdict"], dv.VERDICT_LEDGER_BOUND_MATERIAL)
        self.assertTrue(result["ledger_bound"])
        self.assertFalse(result["acceptance_claim"])
        self.assertIn("ChatGPT lead", result["acceptance_authority"])

    def test_verify_from_paths_loads_committed_disk_evidence(self):
        """The comparator must run from on-disk artifacts, not in-memory only."""
        out = self.tmp / "bundle"
        out.mkdir()
        matrix = build_matrix()
        dp.write_prepared(matrix, out / "PREPARED_MATRIX.json")
        receipts_dir = out / "receipts"
        receipts_dir.mkdir()
        # Empty receipts → incomplete, but the load path must succeed.
        result = dv.verify_from_paths(
            matrix_path=out / "PREPARED_MATRIX.json",
            receipts_dir=receipts_dir,
        )
        self.assertEqual(result["verifier_id"], "SB-R07-044")
        self.assertEqual(result["verdict"], dv.VERDICT_REJECTED)  # fixture matrix
        self.assertEqual(result["source"]["matrix_path"],
                         str(out / "PREPARED_MATRIX.json"))
        self.assertFalse(result["live_model_call_performed"])


class VerifyCliTest(unittest.TestCase):
    def test_cli_writes_verdict_json(self):
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "bin"))
        import verify_divergence
        tmp = Path(tempfile.mkdtemp())
        matrix = build_matrix()
        matrix_path = tmp / "PREPARED_MATRIX.json"
        dp.write_prepared(matrix, matrix_path)
        receipts = tmp / "receipts"
        receipts.mkdir()
        out = tmp / "verdict.json"
        code = verify_divergence.main([
            "--matrix", str(matrix_path),
            "--receipts", str(receipts),
            "--out", str(out),
        ])
        self.assertEqual(code, 0)
        verdict = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(verdict["verifier_id"], "SB-R07-044")
        self.assertFalse(verdict["acceptance_claim"])


if __name__ == "__main__":
    unittest.main()
