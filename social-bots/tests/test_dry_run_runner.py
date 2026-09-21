"""SB-R07-061 — reusable V0.6 dry-run runner acceptance tests."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import dry_run_runner as drr, decision  # noqa: E402


SIGNALS = {
    "social-a": [dict(title="Fixture A", summary="A soft measurement note.",
                      source="fixture", url="https://example.org/a",
                      tags=["a"], provenance="fixture")],
    "social-b": [dict(title="Fixture B", summary="A soft wonder note.",
                      source="fixture", url="https://example.org/b",
                      tags=["b"], provenance="fixture")],
    "social-c": [dict(title="Fixture C", summary="A soft culture note.",
                      source="fixture", url="https://example.org/c",
                      tags=["c"], provenance="fixture")],
}


class DryRunRunnerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp
        self.manifests = Path(self.tmp) / "manifests"

    def test_zero_public_authority_defaults(self):
        a = drr.ZERO_PUBLIC_AUTHORITY
        self.assertFalse(a.can_public_post)
        self.assertFalse(a.can_spend)
        self.assertFalse(a.can_message_users)

    def test_refuses_public_effect_authority(self):
        with self.assertRaises(ValueError):
            drr.run_one_dry_run(
                "social-a", "social-a",
                authority=decision.Authority(can_public_post=True),
                signals=SIGNALS["social-a"])

    def test_three_bot_runner_writes_immutable_manifests(self):
        results = drr.run_three_bot_dry_runs(
            artifact_id="SB-R07-061",
            source_code_ref="test-ref",
            signal_map=SIGNALS,
            manifest_dir=self.manifests,
        )
        self.assertEqual(len(results), 3)
        for r in results:
            self.assertIn(r.bot, {"social-a", "social-b", "social-c"})
            self.assertFalse(r.published)
            self.assertFalse(r.publish_authorized)
            self.assertEqual(r.manifest["model_calls_used"], 0)
            self.assertEqual(r.manifest["public_effect_budget"], 0)
            self.assertEqual(r.manifest["schema_version"], drr.SCHEMA_VERSION)
            path = self.manifests / f"{r.bot}-{r.persona}.run_manifest.json"
            self.assertTrue(path.exists())
            on_disk = json.loads(path.read_text())
            self.assertEqual(on_disk["run_id"], r.manifest["run_id"])
            # Required schema fields present.
            for key in (
                "schema_version", "run_id", "artifact_id", "version_target",
                "bot", "persona", "started_at", "finished_at", "source_code_ref",
                "config_hash", "persona_hash", "objective_hash", "host_alias",
                "scheduler_or_invoker", "authorization_manifest_ref",
                "evidence_refs", "provider_runs", "model_call_budget",
                "model_calls_used", "public_effect_budget",
                "public_effects_attempted", "public_effects_verified",
                "result", "limitations", "receipt_refs",
            ):
                self.assertIn(key, on_disk)
            self.assertTrue(r.passed, r.checks)

    def test_manifest_refuse_overwrite(self):
        dest = self.manifests / "social-a-social-a.run_manifest.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text("{}")
        with self.assertRaises(FileExistsError):
            drr.run_one_dry_run(
                "social-a", "social-a",
                signals=SIGNALS["social-a"],
                write_manifest_to=dest)

    def test_no_pending_signal_yields_no_action_still_manifests(self):
        r = drr.run_one_dry_run(
            "social-a", "social-a",
            capture_signals=False,
            write_manifest_to=self.manifests / "empty.run_manifest.json")
        self.assertEqual(r.outcome, "no_action")
        self.assertTrue(r.passed)
        self.assertFalse(r.published)


if __name__ == "__main__":
    unittest.main()
