"""SB-V04-002/004 — the fail-closed live-execution gate and exact call budget.

ENGINEERING-ONLY: every manifest and provider here is a test fixture. Nothing in
this file authorizes, performs or evidences a real adaptive model call. The
canonical state remains BLOCKED_OWNER_AUTHORIZATION; these tests prove the gate
holds, not that a batch may run.
"""
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import authorization  # noqa: E402


FIXTURE_SOURCE_SHA = "1" * 40
FIXTURE_SOURCE_TREE = "2" * 40


def fixture_binding(run_scope="v04-divergence-test"):
    closure = {
        "artifacts": ["SB-V04-002", "SB-V04-004"],
        "cases": [],
        "lane": "windows-core",
        "run_scope": run_scope,
    }
    return authorization.ExecutionBinding(
        json.dumps(closure, sort_keys=True, separators=(",", ":")))


def _iso(dt):
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def valid_manifest(**overrides):
    """A structurally valid ENGINEERING FIXTURE manifest (never a real grant)."""
    now = datetime.now(timezone.utc)
    manifest = {
        "schema_version": "v1",
        "manifest_id": "AUTH-FIXTURE-0001",
        "created_by": "test-fixture-not-the-lead",
        "created_at": _iso(now - timedelta(minutes=5)),
        "owner_authorization_ref": "engineering fixture; no real owner authorization",
        "artifact_scope": ["SB-V04-002", "SB-V04-004"],
        "run_scope": "v04-divergence-test",
        "lane": "windows-core",
        "provider_mode": "claude-cli",
        "max_calls": 5,
        "expires_at": _iso(now + timedelta(hours=2)),
        "retry_allowed": False,
        "public_effect_allowed": False,
        "spend_authorized": False,
        "api_key_allowed": False,
        "injected_runner_allowed": False,
        "source_sha": FIXTURE_SOURCE_SHA,
        "source_tree": FIXTURE_SOURCE_TREE,
        "execution_matrix_sha256": fixture_binding().digest,
    }
    manifest.update(overrides)
    return manifest


class ManifestValidationTest(unittest.TestCase):
    def test_fixture_manifest_is_structurally_valid(self):
        """The fixture baseline must be valid, or every negative case is vacuous."""
        self.assertEqual(authorization.validate_manifest(valid_manifest()), [])

    def test_every_required_field_is_mandatory(self):
        """A manifest that omits any required field is rejected, never defaulted."""
        for field in ("schema_version", "manifest_id", "created_by", "created_at",
                      "owner_authorization_ref", "artifact_scope", "run_scope",
                      "lane", "provider_mode", "max_calls", "expires_at",
                      "retry_allowed", "public_effect_allowed", "spend_authorized",
                      "api_key_allowed", "injected_runner_allowed", "source_sha",
                      "source_tree", "execution_matrix_sha256"):
            with self.subTest(field=field):
                manifest = valid_manifest()
                del manifest[field]
                errs = authorization.validate_manifest(manifest)
                self.assertTrue(any(field in e for e in errs), errs)

    def test_safety_postures_must_be_explicitly_false(self):
        """A permissive or truthy safety posture invalidates the whole manifest."""
        for field in ("retry_allowed", "public_effect_allowed", "spend_authorized",
                      "api_key_allowed", "injected_runner_allowed"):
            for value in (True, "false", 0, None):
                with self.subTest(field=field, value=value):
                    errs = authorization.validate_manifest(valid_manifest(**{field: value}))
                    self.assertTrue(any(field in e for e in errs), (field, value, errs))

    def test_max_calls_cannot_exceed_the_hard_ceiling(self):
        """No manifest can widen the batch beyond the conservative five-call plan."""
        errs = authorization.validate_manifest(
            valid_manifest(max_calls=authorization.HARD_MAX_CALLS + 1))
        self.assertTrue(any("hard ceiling" in e for e in errs), errs)

    def test_non_subscription_provider_mode_is_rejected(self):
        """Only the existing-subscription Claude Code route may ever be authorized."""
        errs = authorization.validate_manifest(valid_manifest(provider_mode="model"))
        self.assertTrue(any("subscription route" in e for e in errs), errs)

    def test_expired_manifest_is_rejected(self):
        """An authorization that has lapsed is not an authorization."""
        past = _iso(datetime.now(timezone.utc) - timedelta(minutes=1))
        errs = authorization.validate_manifest(valid_manifest(expires_at=past))
        self.assertTrue(any("expired" in e for e in errs), errs)


class GateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.manifests = self.tmp / "authorizations"
        self.manifests.mkdir()
        self.source_patch = mock.patch.object(
            authorization, "source_identity",
            return_value=(FIXTURE_SOURCE_SHA, FIXTURE_SOURCE_TREE))
        self.source_patch.start()

    def tearDown(self):
        self.source_patch.stop()

    def _write(self, manifest, name="auth.json"):
        (self.manifests / name).write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    def test_no_manifest_fails_closed(self):
        """The current canonical state: an empty manifest dir denies live execution."""
        with self.assertRaises(authorization.AuthorizationDenied) as ctx:
            authorization.authorize(artifact="SB-V04-002", lane="windows-core",
                                    run_scope="v04-divergence-test",
                                    manifest_dir=self.manifests)
        self.assertIn("no canonical authorization manifest", str(ctx.exception))

    def test_repository_state_denies_live_execution_right_now(self):
        """The real canonical manifest directory must deny, not merely be absent."""
        status = authorization.gate_status(artifact="SB-V04-002", lane="windows-core",
                                           run_scope="v04-divergence-prepare")
        self.assertFalse(status["authorized"])
        self.assertFalse(status["live_execution_permitted"])
        self.assertEqual(status["manifests_present"], [])

    def test_valid_scoped_manifest_grants(self):
        """A correctly scoped fixture manifest grants, so denial cases are meaningful."""
        self._write(valid_manifest())
        grant = authorization.authorize(artifact="SB-V04-004", lane="windows-core",
                                        run_scope="v04-divergence-test",
                                        manifest_dir=self.manifests,
                                        execution_binding=fixture_binding())
        self.assertEqual(grant.max_calls, 5)
        self.assertFalse(grant.retry_allowed)
        self.assertFalse(grant.authorship_attested_by_code)

    def test_wrong_scope_is_denied(self):
        """A manifest only authorizes the exact artifact, lane and run scope it names."""
        self._write(valid_manifest())
        for kwargs in ({"artifact": "SB-V06-001"}, {"lane": "intelligence"},
                       {"run_scope": "some-other-run"}):
            base = {"artifact": "SB-V04-002", "lane": "windows-core",
                    "run_scope": "v04-divergence-test"}
            base.update(kwargs)
            with self.subTest(**kwargs):
                with self.assertRaises(authorization.AuthorizationDenied):
                    authorization.authorize(manifest_dir=self.manifests, **base)

    def test_injected_runner_is_refused_even_with_a_valid_manifest(self):
        """A live batch must use the real provider; no manifest can waive that."""
        self._write(valid_manifest())
        with self.assertRaises(authorization.AuthorizationDenied) as ctx:
            authorization.authorize(artifact="SB-V04-002", lane="windows-core",
                                    run_scope="v04-divergence-test",
                                    manifest_dir=self.manifests, injected_runner=True)
        self.assertIn("injected runner", str(ctx.exception))

    def test_api_key_presence_is_refused_even_with_a_valid_manifest(self):
        """ANTHROPIC_API_KEY would route to paid billing; the gate hard-stops on it."""
        self._write(valid_manifest())
        prior = os.environ.get("ANTHROPIC_API_KEY")
        os.environ["ANTHROPIC_API_KEY"] = "fixture-value-never-used"
        try:
            with self.assertRaises(authorization.AuthorizationDenied) as ctx:
                authorization.authorize(artifact="SB-V04-002", lane="windows-core",
                                        run_scope="v04-divergence-test",
                                        manifest_dir=self.manifests)
            self.assertIn("ANTHROPIC_API_KEY", str(ctx.exception))
        finally:
            if prior is None:
                os.environ.pop("ANTHROPIC_API_KEY", None)
            else:
                os.environ["ANTHROPIC_API_KEY"] = prior

    def test_malformed_manifest_does_not_grant(self):
        """Unparseable or invalid manifest files are rejected with a stated reason."""
        (self.manifests / "broken.json").write_text("{not json", encoding="utf-8")
        self._write(valid_manifest(retry_allowed=True), "retry.json")
        with self.assertRaises(authorization.AuthorizationDenied) as ctx:
            authorization.authorize(artifact="SB-V04-002", lane="windows-core",
                                    run_scope="v04-divergence-test",
                                    manifest_dir=self.manifests)
        self.assertIn("retry_allowed", str(ctx.exception))


class CallBudgetTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def _budget(self, max_calls=5):
        return authorization.CallBudget("v04-divergence-test", max_calls, home=self.tmp)

    def _reserve(self, budget):
        return budget.reserve(manifest_id="AUTH-FIXTURE-0001", manifest_digest="sha256:fix",
                              lane="windows-core", artifact="SB-V04-002")

    def test_exact_budget_is_enforced(self):
        """Exactly max_calls slots exist; the next reservation fails closed."""
        budget = self._budget(5)
        slots = [self._reserve(budget).slot for _ in range(5)]
        self.assertEqual(slots, [1, 2, 3, 4, 5])
        self.assertEqual(budget.remaining(), 0)
        with self.assertRaises(authorization.CallBudgetExhausted):
            self._reserve(budget)

    def test_reservation_is_durable_across_process_restart(self):
        """A fresh CallBudget object sees slots consumed by an earlier process."""
        self._reserve(self._budget(5))
        self.assertEqual(self._budget(5).consumed(), 1)
        self.assertEqual(self._budget(5).remaining(), 4)

    def test_a_failed_call_still_consumes_its_slot(self):
        """No-retry: recording a failure never frees the slot for another attempt."""
        budget = self._budget(2)
        slot = self._reserve(budget)
        budget.record_outcome(slot, "provider_unavailable", {"reason": "fixture"})
        self.assertEqual(budget.remaining(), 1)
        self._reserve(budget)
        with self.assertRaises(authorization.CallBudgetExhausted):
            self._reserve(budget)

    def test_outcome_is_write_once(self):
        """A recorded slot cannot be relabeled into a better outcome."""
        budget = self._budget(3)
        slot = self._reserve(budget)
        budget.record_outcome(slot, "invalid_proposal")
        with self.assertRaises(authorization.AuthorizationDenied):
            budget.record_outcome(slot, "proposal_received")

    def test_unreserved_slot_cannot_record_an_outcome(self):
        """An outcome may only exist for a slot that was actually reserved."""
        with self.assertRaises(authorization.AuthorizationDenied):
            self._budget(3).record_outcome(2, "proposal_received")

    def test_audit_reports_reserved_but_unrecorded_slots(self):
        """A crash between reservation and invocation is visible, not silently reclaimed."""
        budget = self._budget(3)
        self._reserve(budget)                      # simulates a crashed invocation
        recorded = self._reserve(budget)
        budget.record_outcome(recorded, "proposal_received")
        audit = budget.audit()
        self.assertEqual(audit["reserved_not_recorded"], [1])
        self.assertEqual(audit["consumed"], 2)
        self.assertFalse(audit["retry_permitted"])

    def test_budget_cannot_exceed_the_hard_ceiling(self):
        """Even a caller asking for more slots is clamped to the policy ceiling."""
        budget = self._budget(50)
        self.assertEqual(budget.max_calls, authorization.HARD_MAX_CALLS)


if __name__ == "__main__":
    unittest.main()
