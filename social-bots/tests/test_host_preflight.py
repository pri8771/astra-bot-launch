"""SB-R07-072 — persistent-host preflight.

ENGINEERING-ONLY. Never claims LIVE V0.7 acceptance. Ephemeral hosts must be
UNSUITABLE.
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import host_preflight as hp  # noqa: E402


class HostPreflightTest(unittest.TestCase):
    def test_overlay_root_is_unsuitable(self):
        """An overlay/tmpfs root is ephemeral and cannot back V0.7 LIVE."""
        with mock.patch.object(hp, "_fs_type", side_effect=lambda p: "overlay"):
            with mock.patch.object(hp.socket, "gethostname", return_value="devbox"):
                with mock.patch.dict(os.environ, {}, clear=False):
                    os.environ.pop("CURSOR", None)
                    os.environ.pop("CURSOR_AGENT", None)
                    receipt = hp.collect(repo_root=tempfile.mkdtemp())
        self.assertEqual(receipt.verdict, hp.VERDICT_UNSUITABLE)
        self.assertFalse(receipt.suitable_for_v07_live_scheduler)
        self.assertFalse(receipt.live_claim)
        self.assertTrue(any("overlay" in b for b in receipt.blockers))

    def test_cursor_hostname_is_unsuitable(self):
        """Cloud Agent hostname patterns are not persistent owner hosts."""
        with mock.patch.object(hp, "_fs_type", return_value="ext4"):
            with mock.patch.object(hp.socket, "gethostname", return_value="cursor"):
                receipt = hp.collect(repo_root=tempfile.mkdtemp())
        self.assertEqual(receipt.verdict, hp.VERDICT_UNSUITABLE)
        self.assertFalse(receipt.suitable_for_v07_live_scheduler)

    def test_owner_attestation_cannot_override_ephemeral_markers(self):
        """Owner attestation does not wash away overlay/Cloud Agent signals."""
        with mock.patch.object(hp, "_fs_type", return_value="overlay"):
            with mock.patch.object(hp.socket, "gethostname", return_value="cursor"):
                receipt = hp.collect(repo_root=tempfile.mkdtemp(),
                                     owner_attested_persistent=True)
        self.assertEqual(receipt.verdict, hp.VERDICT_UNSUITABLE)
        self.assertFalse(receipt.suitable_for_v07_live_scheduler)

    def test_clean_host_without_attestation_is_inconclusive(self):
        """Even a clean host needs owner attestation before LIVE scheduler claims."""
        with mock.patch.object(hp, "_fs_type", return_value="ext4"):
            with mock.patch.object(hp.socket, "gethostname", return_value="homeserver"):
                with mock.patch.object(hp.shutil, "which",
                                       side_effect=lambda c: f"/usr/bin/{c}"
                                       if c in {"systemctl", "crontab"} else None):
                    with mock.patch.object(hp, "_cmd", return_value={
                        "argv": [], "returncode": 0, "output": "running",
                    }):
                        with mock.patch.dict(os.environ, {}, clear=False):
                            os.environ.pop("CURSOR", None)
                            os.environ.pop("CURSOR_AGENT", None)
                            os.environ.pop("ANTHROPIC_API_KEY", None)
                            receipt = hp.collect(repo_root=tempfile.mkdtemp())
        self.assertEqual(receipt.verdict, hp.VERDICT_INCONCLUSIVE)
        self.assertFalse(receipt.suitable_for_v07_live_scheduler)
        self.assertFalse(receipt.live_claim)

    def test_attested_clean_host_is_suitable_candidate(self):
        """With owner attestation and no ephemeral markers, mark as candidate."""
        with mock.patch.object(hp, "_fs_type", return_value="ext4"):
            with mock.patch.object(hp.socket, "gethostname", return_value="homeserver"):
                with mock.patch.object(hp.shutil, "which",
                                       side_effect=lambda c: f"/usr/bin/{c}"
                                       if c in {"systemctl", "crontab"} else None):
                    with mock.patch.object(hp, "_cmd", return_value={
                        "argv": [], "returncode": 0, "output": "running",
                    }):
                        with mock.patch.dict(os.environ, {}, clear=False):
                            os.environ.pop("CURSOR", None)
                            os.environ.pop("CURSOR_AGENT", None)
                            os.environ.pop("ANTHROPIC_API_KEY", None)
                            receipt = hp.collect(
                                repo_root=tempfile.mkdtemp(),
                                owner_attested_persistent=True)
        self.assertEqual(receipt.verdict, hp.VERDICT_SUITABLE)
        self.assertTrue(receipt.suitable_for_v07_live_scheduler)
        self.assertFalse(receipt.live_claim)

    def test_write_receipt_round_trip(self):
        tmp = Path(tempfile.mkdtemp())
        path = tmp / "PREFLIGHT.json"
        receipt = hp.collect(repo_root=tmp)
        written = hp.write_receipt(receipt, path)
        loaded = json.loads(written.read_text(encoding="utf-8"))
        self.assertEqual(loaded["preflight_id"], "SB-R07-072")
        self.assertFalse(loaded["live_claim"])


class PreflightCliTest(unittest.TestCase):
    def test_cli_writes_receipt(self):
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "bin"))
        import persistent_host_preflight
        tmp = Path(tempfile.mkdtemp())
        out = tmp / "receipt.json"
        code = persistent_host_preflight.main(["--out", str(out), "--repo-root", str(tmp)])
        self.assertEqual(code, 0)
        data = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(data["preflight_id"], "SB-R07-072")
        self.assertIn(data["verdict"], {
            hp.VERDICT_UNSUITABLE, hp.VERDICT_INCONCLUSIVE, hp.VERDICT_SUITABLE,
        })


if __name__ == "__main__":
    unittest.main()
