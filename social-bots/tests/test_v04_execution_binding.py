"""LEAD-064: exact source and complete V0.4 execution-closure binding.

All manifests, evidence and providers are temporary engineering fixtures.  The
provider sentinel reaches only an in-process callable through the real dispatch
gate; these tests perform no model, provider, network, account or public action.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from runtime import authorization, model_dispatch, reasoning
from runtime import divergence_prepare as dp
from tests.test_v04_divergence_prepare import (
    OBJECTIVE,
    PERSONAS,
    build,
    default_snapshots,
)

SHA = "1" * 40
TREE = "2" * 40


def _iso(value):
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _proposal():
    return reasoning.ReasoningProposal(
        alternatives=[reasoning.no_action("offline sentinel")],
        recommended_action="NO_ACTION",
        uncertainties=["fixture"],
        provider_id="offline-sentinel",
        adaptive=True,
    )


class _OfflineProvider:
    provider_id = "offline-sentinel"
    reason = None
    constructed = 0
    calls = 0

    def __init__(self):
        type(self).constructed += 1

    def propose(self, ctx):
        def sentinel(inner_ctx):
            type(self).calls += 1
            return _proposal()

        return model_dispatch.dispatch(
            sentinel, ctx, provider_id=self.provider_id, live=True
        )


class ExecutionBindingTest(unittest.TestCase):
    def setUp(self):
        self.tmp_obj = tempfile.TemporaryDirectory()
        self.tmp = Path(self.tmp_obj.name)
        self.manifests = self.tmp / "authorizations"
        self.manifests.mkdir()
        self.home = self.tmp / "home"
        self.matrix = build()
        self.binding = dp.execution_binding(self.matrix)
        self.snapshots = default_snapshots()
        self.old_key = os.environ.pop("ANTHROPIC_API_KEY", None)
        _OfflineProvider.constructed = 0
        _OfflineProvider.calls = 0
        model_dispatch.clear()

    def tearDown(self):
        model_dispatch.clear()
        if self.old_key is not None:
            os.environ["ANTHROPIC_API_KEY"] = self.old_key
        self.tmp_obj.cleanup()

    def _manifest(self, **updates):
        now = datetime.now(timezone.utc)
        value = {
            "schema_version": "v1",
            "manifest_id": "AUTH-BINDING-FIXTURE",
            "created_by": "test-fixture-not-lead",
            "created_at": _iso(now - timedelta(minutes=1)),
            "owner_authorization_ref": "engineering fixture only",
            "artifact_scope": ["SB-V04-002", "SB-V04-004"],
            "run_scope": self.matrix.run_scope,
            "lane": self.matrix.lane,
            "provider_mode": "claude-cli",
            "max_calls": 5,
            "expires_at": _iso(now + timedelta(hours=1)),
            "retry_allowed": False,
            "public_effect_allowed": False,
            "spend_authorized": False,
            "api_key_allowed": False,
            "injected_runner_allowed": False,
            "source_sha": SHA,
            "source_tree": TREE,
            "execution_matrix_sha256": self.binding.digest,
        }
        value.update(updates)
        return value

    def _write_manifest(self, **updates):
        path = self.manifests / "binding.json"
        path.write_text(json.dumps(self._manifest(**updates)), encoding="utf-8")
        return path

    def _case_context(self, case_id):
        case = self.matrix.case(case_id)
        return dp._context_for(
            PERSONAS[case.persona_slot],
            self.snapshots[case.evidence_id],
            objective=self.matrix.objective,
            pending_count=self.matrix.held_constant["pending_count"],
            is_duplicate=self.matrix.held_constant["is_duplicate"],
            prior_hypotheses=self.matrix.held_constant["prior_hypotheses"],
            draft={},
        )

    def _execute(self, matrix=None, snapshots=None):
        matrix = matrix or self.matrix
        with (
            mock.patch.object(
                authorization, "source_identity", return_value=(SHA, TREE)
            ),
            mock.patch.object(
                dp.reasoning_cli, "ClaudeCodeReasoningProvider", _OfflineProvider
            ),
        ):
            return dp.execute_batch(
                matrix,
                lane=matrix.lane,
                personas=PERSONAS,
                snapshots=snapshots or self.snapshots,
                manifest_dir=self.manifests,
                home=self.home,
            )

    def _assert_batch_preflight_denied(
        self,
        matrix,
        *,
        snapshots=None,
        source=(SHA, TREE),
        error=authorization.AuthorizationDenied,
        message=None,
    ):
        """Exercise execute_batch while proving no effectful setup was reached."""
        matcher = (
            self.assertRaisesRegex(error, message)
            if message
            else self.assertRaises(error)
        )
        with (
            mock.patch.object(authorization, "source_identity", return_value=source),
            mock.patch.object(
                authorization,
                "CallBudget",
                side_effect=AssertionError(
                    "CallBudget constructed before binding preflight"
                ),
            ) as budget,
            mock.patch.object(
                dp.reasoning_cli,
                "ClaudeCodeReasoningProvider",
                side_effect=AssertionError(
                    "provider constructed before binding preflight"
                ),
            ) as provider,
            mock.patch.object(model_dispatch, "configure") as configure,
            matcher,
        ):
            dp.execute_batch(
                matrix,
                lane=matrix.lane,
                personas=PERSONAS,
                snapshots=snapshots or self.snapshots,
                manifest_dir=self.manifests,
                home=self.home,
            )
        budget.assert_not_called()
        provider.assert_not_called()
        configure.assert_not_called()
        self.assertIsNone(model_dispatch.current_scope())
        self.assertFalse((self.home / "call-budget").exists())

    def test_exact_binding_reaches_only_offline_sentinel_and_records_binding(self):
        self._write_manifest()
        result = self._execute()
        self.assertEqual((_OfflineProvider.constructed, _OfflineProvider.calls), (1, 5))
        expected = (SHA, TREE, self.binding.digest)
        for item in result["results"]:
            self.assertEqual(
                (
                    item["source_sha"],
                    item["source_tree"],
                    item["execution_matrix_sha256"],
                ),
                expected,
            )
            self.assertEqual(item["outcome"], "proposal_received")
        slots = authorization.CallBudget(
            self.matrix.run_scope, 5, home=self.home
        ).slots()
        self.assertEqual(len(slots), 5)
        self.assertTrue(
            all(
                (s["source_sha"], s["source_tree"], s["execution_matrix_sha256"])
                == expected
                for s in slots
            )
        )
        record = model_dispatch.last_record()
        self.assertEqual(
            (record.source_sha, record.source_tree, record.execution_matrix_sha256),
            expected,
        )

    def test_coherent_objective_prompt_and_evidence_changes_fail_before_provider_or_budget(
        self,
    ):
        self._write_manifest()
        changed_objective = build(objective=OBJECTIVE + " changed")
        changed_snaps = default_snapshots()
        changed_snaps["E1"] = dp.EvidenceSnapshot.from_bytes(
            "E1",
            {**changed_snaps["E1"].signal, "url": "https://changed.invalid/e1"},
            b"E1-changed",
            {"kind": "engineering-fixture", "byte_length": 10},
            provenance_label=dp.ENGINEERING_FIXTURE,
            captured_at="2026-09-21T00:00:00Z",
        )
        changed_evidence = build(snapshots=changed_snaps)
        stale_prompt = deepcopy(self.matrix)
        stale_prompt.cases[0].prompt += " changed without updating its digest"
        stale_receipt_url = deepcopy(self.matrix)
        stale_receipt_url.snapshots[0]["signal"]["url"] = (
            "https://changed.invalid/receipt"
        )

        cases = (
            (
                "objective",
                changed_objective,
                default_snapshots(),
                authorization.AuthorizationDenied,
                "execution_matrix_binding_mismatch",
            ),
            (
                "evidence",
                changed_evidence,
                changed_snaps,
                authorization.AuthorizationDenied,
                "execution_matrix_binding_mismatch",
            ),
            (
                "prompt_stale_hash",
                stale_prompt,
                default_snapshots(),
                dp.MatrixError,
                "digests or isolation are invalid",
            ),
            (
                "receipt_url_stale_digest",
                stale_receipt_url,
                default_snapshots(),
                authorization.AuthorizationDenied,
                "execution_matrix_binding_mismatch",
            ),
        )
        for label, matrix, snapshots, error, message in cases:
            with self.subTest(label=label):
                self._assert_batch_preflight_denied(
                    matrix, snapshots=snapshots, error=error, message=message
                )

        runtime_drift = default_snapshots()
        runtime_drift["E1"] = dp.EvidenceSnapshot.from_bytes(
            "E1",
            {**runtime_drift["E1"].signal, "url": "https://runtime.invalid/drift"},
            b"runtime-drift",
            {"kind": "engineering-fixture", "byte_length": 13},
            provenance_label=dp.ENGINEERING_FIXTURE,
            captured_at="2026-09-21T00:00:00Z",
        )
        self._assert_batch_preflight_denied(
            self.matrix,
            snapshots=runtime_drift,
            error=dp.MatrixError,
            message="execution evidence closure differs",
        )
        self._assert_batch_preflight_denied(
            self.matrix,
            source=("3" * 40, TREE),
            message="source_binding_mismatch",
        )
        self.assertEqual((_OfflineProvider.constructed, _OfflineProvider.calls), (0, 0))

    def test_missing_or_wrong_source_binding_is_denied(self):
        for field in ("source_sha", "source_tree", "execution_matrix_sha256"):
            with self.subTest(missing=field):
                manifest = self._manifest()
                manifest.pop(field)
                self.assertTrue(
                    any(
                        field in err
                        for err in authorization.validate_manifest(manifest)
                    )
                )
        for source, message in (
            ((("3" * 40), TREE), "source_binding_mismatch"),
            ((SHA, "4" * 40), "source_binding_mismatch"),
        ):
            with self.subTest(source=source):
                self._write_manifest()
                with (
                    mock.patch.object(
                        authorization, "source_identity", return_value=source
                    ),
                    self.assertRaisesRegex(authorization.AuthorizationDenied, message),
                ):
                    authorization.authorize(
                        artifact="SB-V04-002",
                        lane=self.matrix.lane,
                        run_scope=self.matrix.run_scope,
                        manifest_dir=self.manifests,
                        execution_binding=self.binding,
                    )
        self.assertFalse((self.home / "call-budget").exists())

    def test_both_v04_artifacts_refuse_direct_dispatch_without_binding(self):
        self._write_manifest()
        invoked = []
        for artifact in ("SB-V04-002", "SB-V04-004"):
            scope = model_dispatch.DispatchScope(
                artifact,
                self.matrix.lane,
                self.matrix.run_scope,
                manifest_dir=str(self.manifests),
                home=str(self.home),
            )
            with (
                self.subTest(artifact=artifact),
                self.assertRaisesRegex(
                    model_dispatch.DispatchRefused, "execution_binding_required"
                ),
            ):
                model_dispatch.dispatch(
                    lambda ctx: invoked.append(ctx),
                    object(),
                    provider_id="offline",
                    scope=scope,
                )
        self.assertEqual(invoked, [])
        self.assertFalse((self.home / "call-budget").exists())

    def test_reserved_token_rejects_missing_or_different_binding_without_second_slot(
        self,
    ):
        self._write_manifest()
        invoked = []
        correct = model_dispatch.DispatchScope(
            "SB-V04-002",
            self.matrix.lane,
            self.matrix.run_scope,
            manifest_dir=str(self.manifests),
            home=str(self.home),
            execution_binding=self.binding,
        )
        different = authorization.ExecutionBinding(
            json.dumps(
                {**self.binding.closure(), "objective": "different"},
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        for label, attempted in (
            ("missing", None),
            (
                "different",
                model_dispatch.DispatchScope(
                    "SB-V04-002",
                    self.matrix.lane,
                    self.matrix.run_scope,
                    manifest_dir=str(self.manifests),
                    home=str(self.home),
                    execution_binding=different,
                ),
            ),
        ):
            case_home = self.tmp / label
            reserved_scope = model_dispatch.DispatchScope(
                correct.artifact,
                correct.lane,
                correct.run_scope,
                manifest_dir=correct.manifest_dir,
                home=str(case_home),
                execution_binding=correct.execution_binding,
            )
            with (
                self.subTest(label=label),
                mock.patch.object(
                    authorization, "source_identity", return_value=(SHA, TREE)
                ),
                model_dispatch.reserved(
                    reserved_scope,
                    context_digest=self.matrix.case("P0").context_sha256,
                ),
                self.assertRaisesRegex(
                    model_dispatch.DispatchRefused, "reserved_execution_scope_mismatch"
                ),
            ):
                model_dispatch.dispatch(
                    lambda ctx: invoked.append(ctx),
                    object(),
                    provider_id="offline",
                    scope=attempted,
                )
            budget = authorization.CallBudget(self.matrix.run_scope, 5, home=case_home)
            self.assertEqual(budget.consumed(), 1)
            self.assertEqual(len(budget.slots()), 1)
        self.assertEqual(invoked, [])

    def test_reserved_p0_token_cannot_dispatch_p1_under_the_same_binding(self):
        self._write_manifest()
        p0 = self.matrix.case("P0")
        p1_ctx = self._case_context("P1")
        invoked = []
        scope = model_dispatch.DispatchScope(
            "SB-V04-002",
            self.matrix.lane,
            self.matrix.run_scope,
            manifest_dir=str(self.manifests),
            home=str(self.home),
            execution_binding=self.binding,
        )
        with (
            mock.patch.object(
                authorization, "source_identity", return_value=(SHA, TREE)
            ),
            model_dispatch.reserved(scope, context_digest=p0.context_sha256),
            self.assertRaisesRegex(
                model_dispatch.DispatchRefused, "reserved_execution_context_mismatch"
            ),
        ):
            model_dispatch.dispatch(
                lambda ctx: invoked.append(ctx),
                p1_ctx,
                provider_id="offline",
                scope=scope,
            )
        budget = authorization.CallBudget(self.matrix.run_scope, 5, home=self.home)
        self.assertEqual(budget.consumed(), 1)
        self.assertEqual(len(budget.slots()), 1)
        self.assertIsNone(budget.slots()[0]["outcome"])
        self.assertEqual(invoked, [])

    def test_direct_p0_ignores_caller_supplied_p1_digest_and_records_actual_p0(self):
        self._write_manifest()
        p0 = self.matrix.case("P0")
        p1 = self.matrix.case("P1")
        p0_ctx = self._case_context("P0")
        invoked = []
        scope = model_dispatch.DispatchScope(
            "SB-V04-002",
            self.matrix.lane,
            self.matrix.run_scope,
            manifest_dir=str(self.manifests),
            home=str(self.home),
            execution_binding=self.binding,
        )
        with mock.patch.object(
            authorization, "source_identity", return_value=(SHA, TREE)
        ):
            model_dispatch.dispatch(
                lambda ctx: invoked.append(ctx) or _proposal(),
                p0_ctx,
                provider_id="offline",
                scope=scope,
                context_digest=p1.context_sha256,
            )
        slots = authorization.CallBudget(
            self.matrix.run_scope, 5, home=self.home
        ).slots()
        self.assertEqual(len(slots), 1)
        self.assertEqual(slots[0]["context_digest"], p0.context_sha256)
        self.assertNotEqual(slots[0]["context_digest"], p1.context_sha256)
        self.assertEqual(len(invoked), 1)

    def test_readonly_source_identity_rejects_tracked_and_untracked_runtime_changes(
        self,
    ):
        repo = self.tmp / "repo"
        runtime = repo / "social-bots" / "runtime"
        runtime.mkdir(parents=True)
        tracked = runtime / "gate.py"
        tracked.write_text("clean = True\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        subprocess.run(
            ["git", "-C", str(repo), "config", "user.email", "test@example.invalid"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(repo), "config", "user.name", "Test"], check=True
        )
        subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-qm", "fixture"], check=True)
        with mock.patch.object(authorization, "ROOT", repo / "social-bots"):
            clean = authorization.source_identity()
            self.assertEqual(len(clean), 2)
            tracked.write_text("clean = False\n", encoding="utf-8")
            with self.assertRaisesRegex(
                authorization.AuthorizationDenied,
                "source_identity_unavailable_or_modified",
            ):
                authorization.source_identity()
            subprocess.run(["git", "-C", str(repo), "checkout", "--", "."], check=True)
            (runtime / "untracked.py").write_text("x = 1\n", encoding="utf-8")
            with self.assertRaisesRegex(
                authorization.AuthorizationDenied,
                "source_identity_unavailable_or_modified",
            ):
                authorization.source_identity()


if __name__ == "__main__":
    unittest.main()
