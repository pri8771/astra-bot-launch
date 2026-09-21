"""SB-R07-042 — controlled V0.4 divergence input freeze.

Unit tests use structurally live-shaped captures without network. A separate
live test performs real HTTPS capture when network is available.
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import divergence_freeze as df  # noqa: E402
from runtime import divergence_prepare as dp  # noqa: E402
from runtime import collector  # noqa: E402


def _caps():
    e1 = df.captured_source_from_bytes(
        "E1", "https://example.com/",
        b"<html>example domain freeze e1</html>",
        title="Example Domain public homepage",
        summary="Controlled E1 bytes for freeze unit test.",
        tags=["divergence-e1"],
    )
    e2 = df.captured_source_from_bytes(
        "E2", "https://www.rfc-editor.org/rfc/rfc8259.txt",
        b"RFC 8259 JSON freeze e2 bytes - materially different from E1",
        title="RFC 8259 JSON",
        summary="Controlled E2 bytes for freeze unit test.",
        tags=["divergence-e2"],
    )
    return e1, e2


class FreezeWriterTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_freeze_writes_immutable_bundle_with_isolation(self):
        e1, e2 = _caps()
        out = self.tmp / "freeze"
        manifest = df.freeze_from_captures(out, e1=e1, e2=e2)
        self.assertEqual(manifest["freeze_id"], "SB-R07-042")
        self.assertFalse(manifest["live_model_call_performed"])
        self.assertFalse(manifest["acceptance_claim"])
        self.assertTrue(manifest["acceptance_eligible"])
        self.assertTrue(manifest["isolation_all_isolated"])
        for name in ("E1.raw", "E2.raw", "E1.receipt.json", "E2.receipt.json",
                     "EVIDENCE_BUNDLE.json", "PREPARED_MATRIX.json",
                     "ISOLATION.json", "FREEZE_MANIFEST.json"):
            self.assertTrue((out / name).exists(), name)
        self.assertTrue((out / "prompts" / "P0.prompt.txt").exists())
        # Raw bytes round-trip.
        self.assertEqual((out / "E1.raw").read_bytes(), e1.raw)
        self.assertEqual((out / "E2.raw").read_bytes(), e2.raw)
        # Required comparisons present.
        self.assertEqual(
            [tuple(c) for c in manifest["required_comparisons"]],
            list(dp.REQUIRED_COMPARISONS),
        )
        isolation = json.loads((out / "ISOLATION.json").read_text(encoding="utf-8"))
        self.assertTrue(isolation["all_isolated"])
        self.assertEqual(len(isolation["comparisons"]), 4)

    def test_refuses_non_empty_out_dir(self):
        e1, e2 = _caps()
        out = self.tmp / "occupied"
        out.mkdir()
        (out / "preexisting.txt").write_text("x", encoding="utf-8")
        with self.assertRaises(df.FreezeError):
            df.freeze_from_captures(out, e1=e1, e2=e2)

    def test_refuses_identical_evidence(self):
        e1, _ = _caps()
        e2 = df.captured_source_from_bytes(
            "E2", "https://www.rfc-editor.org/rfc/rfc8259.txt",
            e1.raw,  # identical bytes
            title="dup", summary="dup", tags=["x"],
        )
        with self.assertRaises(df.FreezeError):
            df.freeze_from_captures(self.tmp / "dup", e1=e1, e2=e2)

    def test_refuses_non_operational_receipt(self):
        e1, e2 = _caps()
        # Downgrade E1 to fixture provenance.
        e1.receipt = collector.CaptureReceipt(
            receipt_id="cap-fx", source_url=e1.url, canonical_id="src-fx",
            retrieved_at=e1.receipt.retrieved_at, status=collector.STATUS_OK,
            capture_mode=collector.MODE_FIXTURE, transport_trusted=False,
            collector_name="c", collector_version="1", fetcher_name="fixture",
            content_hash=e1.receipt.content_hash, content_bytes=len(e1.raw),
            http_status=200, final_url=e1.url, provenance="fixture",
            error=None, partial=False)
        with self.assertRaises(df.FreezeError):
            df.freeze_from_captures(self.tmp / "fx", e1=e1, e2=e2)

    def test_written_matrix_re_verifies(self):
        e1, e2 = _caps()
        out = self.tmp / "verify"
        df.freeze_from_captures(out, e1=e1, e2=e2)
        result = dp.verify_written(out / "PREPARED_MATRIX.json", out / "prompts")
        self.assertTrue(result["verified"])


@unittest.skipUnless(
    os.environ.get("SBOTS_LIVE_FREEZE_TEST") == "1",
    "set SBOTS_LIVE_FREEZE_TEST=1 to exercise real HTTPS capture",
)
class LiveFreezeNetworkTest(unittest.TestCase):
    def test_live_capture_freeze(self):
        out = Path(tempfile.mkdtemp()) / "live-freeze"
        manifest = df.freeze_inputs(out)
        self.assertTrue(manifest["live_network_capture_performed"])
        self.assertFalse(manifest["live_model_call_performed"])
        self.assertTrue(manifest["acceptance_eligible"])
        self.assertTrue((out / "E1.raw").stat().st_size > 0)
        self.assertTrue((out / "E2.raw").stat().st_size > 0)


class FreezeCliTest(unittest.TestCase):
    def test_cli_help_and_import(self):
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "bin"))
        import freeze_divergence_inputs
        self.assertTrue(callable(freeze_divergence_inputs.main))


if __name__ == "__main__":
    unittest.main()
