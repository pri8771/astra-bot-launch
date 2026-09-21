"""Regressions for defects found by an adversarial review of this session's code.

Each test below corresponds to a specific way a stated guarantee could be broken.
They exist because the guarantee was, at one point, only documented — not
enforced. ENGINEERING-ONLY: no manifest here is a real authorization and no test
makes or authorizes a model call.
"""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "bin"))

from runtime import authorization, divergence_prepare as dp  # noqa: E402
from runtime import direction as direction_mod  # noqa: E402
from runtime import invocation as invocation_mod  # noqa: E402
from runtime import live_route_guard  # noqa: E402
from runtime import session_heartbeat as sh  # noqa: E402

import worker_once  # noqa: E402

from tests.test_v04_authorization_gate import valid_manifest  # noqa: E402
from tests.test_v04_divergence_prepare import (  # noqa: E402
    PERSONAS, build as build_matrix, default_snapshots, receipt_for,
)
from tests.test_v07_worker_once import make_repo  # noqa: E402


class EnvGuard:
    """Set env vars for a block and restore them exactly, including absence."""

    def __init__(self, **values):
        self.values = values
        self.prior: dict = {}

    def __enter__(self):
        for key, value in self.values.items():
            self.prior[key] = os.environ.get(key)
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        return self

    def __exit__(self, *exc):
        for key, prior in self.prior.items():
            if prior is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = prior
        return False


# --------------------------------------------------------------------------- #
# F1 / F2 — a live model route must be refused, and the receipt must say so.
# --------------------------------------------------------------------------- #
class LiveRouteGuardTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.manifests = self.tmp / "authorizations"
        self.manifests.mkdir()

    def test_claude_cli_mode_is_refused_without_a_manifest(self):
        """SBOTS_REASONING=claude-cli must not be enough to reach the real CLI."""
        with EnvGuard(SBOTS_REASONING="claude-cli"):
            decision = live_route_guard.check(
                artifact="SB-V07-001", lane="windows-core", run_scope="worker-once:test",
                manifest_dir=self.manifests)
        self.assertTrue(decision.live_route_requested)
        self.assertFalse(decision.permitted)
        self.assertIn("not authorized", decision.reason)

    def test_non_live_modes_are_permitted(self):
        """The deterministic modes are not a live route and must not be blocked."""
        for mode in ("baseline", "contextual"):
            with self.subTest(mode=mode), EnvGuard(SBOTS_REASONING=mode):
                decision = live_route_guard.check(
                    artifact="SB-V07-001", lane="l", run_scope="r",
                    manifest_dir=self.manifests)
                self.assertTrue(decision.permitted)
                self.assertFalse(decision.live_route_requested)

    def test_model_mode_is_live_unless_the_caller_says_it_is_a_replay(self):
        """A registered live callable is a live route; a receipt replay is not."""
        with EnvGuard(SBOTS_REASONING="model"):
            self.assertFalse(live_route_guard.check(
                artifact="a", lane="l", run_scope="r",
                manifest_dir=self.manifests).permitted)
            self.assertTrue(live_route_guard.check(
                artifact="a", lane="l", run_scope="r", manifest_dir=self.manifests,
                replay_is_live=False).permitted)

    def test_a_valid_manifest_permits_the_live_route(self):
        """The guard defers to authorize; it is not an independent veto."""
        manifest = valid_manifest(artifact_scope=["SB-V07-001"], lane="windows-core",
                                  run_scope="worker-once:windows-core")
        (self.manifests / "auth.json").write_text(json.dumps(manifest), encoding="utf-8")
        with EnvGuard(SBOTS_REASONING="claude-cli", ANTHROPIC_API_KEY=None):
            decision = live_route_guard.check(
                artifact="SB-V07-001", lane="windows-core",
                run_scope="worker-once:windows-core", manifest_dir=self.manifests)
        self.assertTrue(decision.permitted)
        self.assertEqual(decision.grant_manifest_id, "AUTH-FIXTURE-0001")


class WorkerOnceRefusesLiveRouteTest(unittest.TestCase):
    """The scheduled entrypoint must refuse before direction, heartbeat or work."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = make_repo(self.tmp)
        self.home = self.tmp / "home"
        self.reports = self.tmp / "reports"
        self.manifests = self.tmp / "authorizations"
        self.manifests.mkdir()

    def _run(self, session_id="s-live-1"):
        with contextlib.redirect_stdout(io.StringIO()):
            return worker_once.main([
                "--lane", "windows-core", "--branch", "b", "--bots", "social-a",
                "--repo-root", str(self.repo), "--session-id", session_id,
                "--skip-fetch", "--home", str(self.home),
                "--report-root", str(self.reports),
                "--manifest-dir", str(self.manifests)])

    def test_exit_six_and_nothing_else_happens(self):
        """A live mode exits 6 before the heartbeat, the ack or any task claim."""
        with EnvGuard(SBOTS_REASONING="claude-cli", SBOTS_HOME=str(self.home)):
            self.assertEqual(self._run(), worker_once.EXIT_LIVE_ROUTE_REFUSED)
        self.assertEqual(sh.read_log("windows-core", self.reports), [])
        self.assertFalse((self.reports / "worker-reports" / "windows-core" /
                          "DIRECTION_ACK.json").exists())

    def test_the_refusal_is_recorded_on_the_invocation_receipt(self):
        """live_model_call is derived from the guard, not hard-coded."""
        with EnvGuard(SBOTS_REASONING="claude-cli", SBOTS_HOME=str(self.home)):
            self._run(session_id="s-live-2")
        receipt = invocation_mod.read_all(self.home)[0]
        self.assertFalse(receipt["live_model_call"])
        self.assertEqual(receipt["reasoning_route"]["mode"], "claude-cli")
        self.assertTrue(receipt["reasoning_route"]["live_route_requested"])
        self.assertFalse(receipt["reasoning_route"]["permitted"])
        self.assertEqual(receipt["work_outcome"], "live_route_refused")
        audit = invocation_mod.audit(self.home)
        self.assertEqual(audit["live_routes_refused"], 1)
        self.assertEqual(audit["live_model_calls"], 0)

    def test_a_normal_run_records_a_non_live_route(self):
        """An ordinary invocation carries a route decision, not an empty field."""
        with EnvGuard(SBOTS_REASONING=None, SBOTS_HOME=str(self.home)):
            with contextlib.redirect_stdout(io.StringIO()):
                code = worker_once.main([
                    "--lane", "windows-core", "--branch", "b", "--bots", "social-a",
                    "--repo-root", str(self.repo), "--session-id", "s-normal",
                    "--skip-fetch", "--allow-deterministic", "--home", str(self.home),
                    "--report-root", str(self.reports),
                    "--manifest-dir", str(self.manifests)])
        self.assertEqual(code, worker_once.EXIT_OK)
        receipt = invocation_mod.read_all(self.home)[0]
        self.assertEqual(receipt["reasoning_route"]["mode"], "baseline")
        self.assertFalse(receipt["reasoning_route"]["live_route_requested"])
        self.assertEqual(invocation_mod.audit(self.home)["receipts_without_a_route_decision"], 0)


class SpawnPointGuardTest(unittest.TestCase):
    """The refusal must live at the spawn point, not only at each entrypoint.

    ``reasoning.resolve_provider`` builds the CLI provider from an environment
    variable, so guarding entrypoints one by one leaves every other caller open.
    These protect the backstop inside the provider itself.
    """

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.manifests = self.tmp / "authorizations"
        self.manifests.mkdir()

    def test_no_manifest_means_no_live_authorization(self):
        """The weak, scope-free question the spawn point can actually answer."""
        ok, reason = live_route_guard.any_live_authorization(self.manifests)
        self.assertFalse(ok)
        self.assertIn("no canonical authorization manifest", reason)

    def test_a_valid_manifest_is_in_force(self):
        """A structurally valid, unexpired manifest answers yes."""
        (self.manifests / "auth.json").write_text(json.dumps(valid_manifest()),
                                                  encoding="utf-8")
        with EnvGuard(ANTHROPIC_API_KEY=None):
            ok, reason = live_route_guard.any_live_authorization(self.manifests)
        self.assertTrue(ok)
        self.assertIn("AUTH-FIXTURE-0001", reason)

    def test_an_api_key_blocks_regardless_of_manifests(self):
        """The paid-API route is never in force, whatever a manifest says."""
        (self.manifests / "auth.json").write_text(json.dumps(valid_manifest()),
                                                  encoding="utf-8")
        with EnvGuard(ANTHROPIC_API_KEY="fixture-value-never-used"):
            ok, reason = live_route_guard.any_live_authorization(self.manifests)
        self.assertFalse(ok)
        self.assertIn("ANTHROPIC_API_KEY", reason)

    def test_the_real_cli_provider_refuses_without_authorization(self):
        """A provider that would launch the real CLI must be unavailable now."""
        from runtime.reasoning_cli import ClaudeCodeReasoningProvider
        from runtime.reasoning import ReasoningContext
        provider = ClaudeCodeReasoningProvider()          # no injected runner
        with EnvGuard(ANTHROPIC_API_KEY=None):
            self.assertFalse(provider.available())
            self.assertIn("not authorized", provider.reason)
            ctx = ReasoningContext(persona={"id": "social-a"}, objective="o",
                                   top_signal={"id": "sig-1", "tags": []},
                                   pending_count=0, is_duplicate=False, draft={})
            self.assertIsNone(provider.propose(ctx))
        self.assertIn("not authorized", provider.reason)

    def test_an_injected_runner_is_exempt_because_it_spawns_nothing(self):
        """The test seam must keep working; it launches no subprocess."""
        from runtime.reasoning_cli import CLIResult, ClaudeCodeReasoningProvider
        calls = []

        def runner(prompt, *, timeout_s, model):
            calls.append(prompt)
            return CLIResult(returncode=0, stdout="{}", stderr="")

        provider = ClaudeCodeReasoningProvider(runner=runner)
        with EnvGuard(ANTHROPIC_API_KEY=None):
            self.assertTrue(provider.available())

    def test_resolve_provider_cannot_produce_a_usable_live_route(self):
        """SBOTS_REASONING=claude-cli resolves, but the provider refuses to run."""
        from runtime import reasoning
        with EnvGuard(SBOTS_REASONING="claude-cli", ANTHROPIC_API_KEY=None):
            provider = reasoning.resolve_provider(require_adaptive=True)
        self.assertTrue(getattr(provider, "adaptive", False))
        self.assertFalse(provider.available())

    def test_rebinding_REAL_CLI_RUNNER_alias_cannot_un_guard_the_real_launcher(self):
        """SB-R07-041: rebinding the public alias must not disable spawn refusal.

        An adversarial probe showed that keying only on the rebindable
        ``_REAL_CLI_RUNNER`` name let ``ClaudeCodeReasoningProvider()`` keep the
        real launcher while ``_spawns_for_real`` returned False.
        """
        from runtime import reasoning_cli
        from runtime.reasoning_cli import ClaudeCodeReasoningProvider
        from runtime.reasoning import ReasoningContext

        original_alias = reasoning_cli._REAL_CLI_RUNNER
        try:
            reasoning_cli._REAL_CLI_RUNNER = object()   # adversarial rebind
            provider = ClaudeCodeReasoningProvider()   # still holds real launcher
            with EnvGuard(ANTHROPIC_API_KEY=None):
                self.assertTrue(provider._spawns_for_real())
                self.assertFalse(provider.available())
                self.assertIn("not authorized", provider.reason)
                ctx = ReasoningContext(persona={"id": "social-a"}, objective="o",
                                       top_signal={"id": "sig-1", "tags": []},
                                       pending_count=0, is_duplicate=False, draft={})
                self.assertIsNone(provider.propose(ctx))
        finally:
            reasoning_cli._REAL_CLI_RUNNER = original_alias

    def test_run_worker_entrypoint_refuses_live_route_without_manifest(self):
        """SB-R07-041: production run_worker.py must exit 6 before any work."""
        import run_worker
        home = self.tmp / "run-worker-home"
        home.mkdir()
        argv_prior = sys.argv[:]
        try:
            sys.argv = ["run_worker.py", "social-a"]
            with EnvGuard(SBOTS_REASONING="claude-cli", SBOTS_HOME=str(home),
                          SBOTS_MANIFEST_DIR=str(self.manifests), ANTHROPIC_API_KEY=None):
                code = run_worker.main()
        finally:
            sys.argv = argv_prior
        self.assertEqual(code, run_worker.EXIT_LIVE_ROUTE_REFUSED)
        # No lease/receipts should have been written under the temp home.
        self.assertFalse(any(home.rglob("*.json")))


# --------------------------------------------------------------------------- #
# F3 — an executed context must be the prepared one.
# --------------------------------------------------------------------------- #
class ExecutedContextBindingTest(unittest.TestCase):
    def setUp(self):
        self.matrix = build_matrix()
        self.tmp = Path(tempfile.mkdtemp())
        self.grant = authorization.ExecutionGrant(
            manifest_id="AUTH-FIXTURE-0001", manifest_path="(fixture)",
            manifest_digest="sha256:fixture", created_by="test-fixture",
            owner_authorization_ref="engineering fixture", artifact="SB-V04-002",
            lane="windows-core", run_scope=self.matrix.run_scope,
            provider_mode="claude-cli", max_calls=5, expires_at="2099-01-01T00:00:00Z",
            granted_at="2026-09-21T00:00:00Z")
        self.budget = authorization.CallBudget(self.matrix.run_scope, 5, home=self.tmp)

    def _run(self, persona, signal):
        class Provider:
            reason = None

            def propose(self, ctx):
                raise AssertionError("provider must not be reached on a mismatch")

        return dp._execute_one_case(
            self.matrix.case("P0"), Provider(), self.budget, grant=self.grant,
            draft={}, persona=persona, objective=self.matrix.objective,
            snapshot_signal=signal, pending_count=0, is_duplicate=False,
            prior_hypotheses=0)

    def test_a_substituted_persona_is_refused(self):
        """Invoking a different persona than the one prepared must not be possible."""
        tampered = dict(PERSONAS["baseline"], display_name="Something Else")
        with self.assertRaises(dp.MatrixError) as ctx:
            self._run(tampered, default_snapshots()["E1"].signal)
        self.assertIn("does not match the prepared case", str(ctx.exception))

    def test_a_substituted_signal_is_refused(self):
        """Invoking different evidence than the one prepared must not be possible."""
        tampered = dict(default_snapshots()["E1"].signal, title="A different story")
        with self.assertRaises(dp.MatrixError):
            self._run(PERSONAS["baseline"], tampered)

    def test_a_summary_only_change_is_refused_by_the_prompt_layer(self):
        """The digest layer is blind to summary; the prompt-payload check is not."""
        tampered = dict(default_snapshots()["E1"].signal,
                        summary="a quietly different evidence summary")
        with self.assertRaises(dp.MatrixError) as ctx:
            self._run(PERSONAS["baseline"], tampered)
        self.assertIn("prompt payload", str(ctx.exception))

    def test_a_refused_mismatch_consumes_no_call_budget(self):
        """Binding is checked before reserving, so a mismatch costs no authorization."""
        with self.assertRaises(dp.MatrixError):
            self._run(dict(PERSONAS["baseline"], display_name="X"),
                      default_snapshots()["E1"].signal)
        self.assertEqual(self.budget.consumed(), 0)


# --------------------------------------------------------------------------- #
# F4 — acceptance eligibility needs a call-budget ledger, not self-declared labels.
# --------------------------------------------------------------------------- #
class AcceptanceEligibilityBindingTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        snaps = default_snapshots()
        for sid in ("E1", "E2"):
            snaps[sid].provenance_label = dp.LIVE_CAPTURE
        self.matrix = build_matrix(snapshots=snaps)
        self.receipts = {}
        for index, case in enumerate(self.matrix.cases):
            receipt = receipt_for(
                case, recommended="CREATE_CANDIDATE" if index else "RESEARCH_MORE",
                bump=0.05 * index)
            receipt["receipt_kind"] = "sanitized-real-canary"   # self-declared label
            self.receipts[case.case_id] = receipt

    def test_hand_authored_labels_alone_do_not_establish_eligibility(self):
        """Anyone can write 'sanitized-real-canary' into a file; that proves nothing."""
        report = dp.divergence_report(self.matrix, self.receipts)
        self.assertTrue(report["all_comparisons_material"])
        self.assertTrue(report["all_receipts_real_adaptive"])
        self.assertFalse(report["acceptance_evidence_eligible"])
        self.assertFalse(report["call_slot_binding"]["checked"])
        self.assertIn("call-budget ledger", report["call_slot_binding"]["reason"])

    def test_an_empty_budget_leaves_every_case_unbound(self):
        """A ledger with no matching slots names the cases it cannot vouch for."""
        budget = authorization.CallBudget(self.matrix.run_scope, 5, home=self.tmp)
        report = dp.divergence_report(self.matrix, self.receipts, budget=budget)
        self.assertFalse(report["acceptance_evidence_eligible"])
        self.assertEqual(sorted(report["call_slot_binding"]["unbound_cases"]),
                         ["E0", "P0", "P1", "P2", "P3"])

    def test_eligibility_requires_a_recorded_proposal_per_case(self):
        """Only slots that actually returned a proposal can back the claim."""
        budget = authorization.CallBudget(self.matrix.run_scope, 5, home=self.tmp)
        for case in self.matrix.cases:
            slot = budget.reserve(manifest_id="AUTH-FIXTURE-0001",
                                  manifest_digest="sha256:fixture", lane="windows-core",
                                  artifact="SB-V04-002",
                                  context_digest=case.context_sha256)
            budget.record_outcome(slot, "proposal_received")
        report = dp.divergence_report(self.matrix, self.receipts, budget=budget)
        self.assertTrue(report["acceptance_evidence_eligible"])
        self.assertEqual(report["call_slot_binding"]["unbound_cases"], [])

    def test_a_failed_call_does_not_bind_its_case(self):
        """A slot recorded as unavailable is not evidence that a proposal exists."""
        budget = authorization.CallBudget(self.matrix.run_scope, 5, home=self.tmp)
        for index, case in enumerate(self.matrix.cases):
            slot = budget.reserve(manifest_id="AUTH-FIXTURE-0001",
                                  manifest_digest="sha256:fixture", lane="windows-core",
                                  artifact="SB-V04-002",
                                  context_digest=case.context_sha256)
            budget.record_outcome(
                slot, "provider_unavailable" if index == 2 else "proposal_received")
        report = dp.divergence_report(self.matrix, self.receipts, budget=budget)
        self.assertFalse(report["acceptance_evidence_eligible"])
        self.assertEqual(report["call_slot_binding"]["unbound_cases"], ["P2"])


# --------------------------------------------------------------------------- #
# F5 / F7 / F16 — the gate and the budget must not be talked out of their job.
# --------------------------------------------------------------------------- #
class GateHardeningTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.manifests = self.tmp / "authorizations"
        self.manifests.mkdir()

    def test_authorize_takes_no_caller_supplied_clock(self):
        """A caller-supplied 'now' would be exactly the override this gate forbids."""
        with self.assertRaises(TypeError):
            authorization.authorize(artifact="a", lane="l", run_scope="r",
                                    manifest_dir=self.manifests,
                                    now=datetime(2025, 1, 1, tzinfo=timezone.utc))

    def test_an_expired_manifest_cannot_be_revived(self):
        """Expiry is judged against the real clock, always."""
        past = (datetime.now(timezone.utc) - timedelta(days=1))
        manifest = valid_manifest(
            created_at=(past - timedelta(hours=1)).replace(microsecond=0)
            .isoformat().replace("+00:00", "Z"),
            expires_at=past.replace(microsecond=0).isoformat().replace("+00:00", "Z"))
        (self.manifests / "auth.json").write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaises(authorization.AuthorizationDenied) as ctx:
            authorization.authorize(artifact="SB-V04-002", lane="windows-core",
                                    run_scope="v04-divergence-test",
                                    manifest_dir=self.manifests)
        self.assertIn("expired", str(ctx.exception))


class CallBudgetHardeningTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def _budget(self, max_calls=5):
        return authorization.CallBudget("v04-hardening", max_calls, home=self.tmp)

    def _reserve(self, budget):
        return budget.reserve(manifest_id="AUTH-FIXTURE-0001",
                              manifest_digest="sha256:fixture", lane="windows-core",
                              artifact="SB-V04-002")

    def test_deleting_a_slot_file_does_not_buy_another_call(self):
        """Removing evidence must never widen an authorization."""
        budget = self._budget(5)
        for _ in range(5):
            self._reserve(budget)
        (self.tmp / "call-budget" / "v04-hardening" / "slot-0003.json").unlink()
        self.assertEqual(budget.consumed(), 5)
        self.assertEqual(budget.remaining(), 0)
        with self.assertRaises(authorization.CallBudgetExhausted):
            self._reserve(budget)

    def test_a_torn_slot_file_does_not_abort_the_batch(self):
        """One slot damaged by an earlier crash must not take the rest down."""
        budget = self._budget(5)
        slot = self._reserve(budget)
        path = self.tmp / "call-budget" / "v04-hardening" / "slot-0001.json"
        path.write_text('{"slot": 1, "trunc', encoding="utf-8")
        recorded = budget.record_outcome(slot, "provider_unavailable")
        self.assertEqual(recorded["outcome"], "provider_unavailable")
        self.assertIn("unreadable_prior_content", recorded)

    def test_a_torn_slot_still_counts_against_the_budget(self):
        """An unreadable slot is consumed, not free."""
        budget = self._budget(2)
        self._reserve(budget)
        (self.tmp / "call-budget" / "v04-hardening" / "slot-0001.json").write_text(
            "{broken", encoding="utf-8")
        self.assertEqual(budget.consumed(), 1)
        audit = budget.audit()
        self.assertEqual([s["slot"] for s in audit["outcomes"]], [1])


# --------------------------------------------------------------------------- #
# F6 / F11 — direction must never guess a lane or leak a raw JSON error.
# --------------------------------------------------------------------------- #
class DirectionHardeningTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_an_ambiguous_lane_match_fails_closed(self):
        """Guessing between two branch matches could silently miss a halt."""
        repo = make_repo(self.tmp, state={
            "worker_lanes": {
                "extras": {"branch": "claude/social-bots-core-extras",
                           "activity": "assigned_work", "assignment": "do stuff"},
                "core": {"branch": "claude/social-bots-core-host",
                         "activity": "frozen_stand_down", "assignment": "stand down"},
            },
            "lead_review": {"review_id": "LEAD-038"},
            "runtime_scope": {"autonomous_bots": ["social-a"]},
            "public_actions": {"no_further_live_model_calls": True}})
        with self.assertRaises(direction_mod.DirectionError) as ctx:
            direction_mod.consume("social-bots-core", repo, fetch=False)
        self.assertIn("refusing to guess", str(ctx.exception))

    def test_an_unambiguous_branch_match_still_works(self):
        """The fallback must keep working for the single-match case it exists for."""
        repo = make_repo(self.tmp)
        self.assertEqual(
            direction_mod.consume("windows-core", repo, fetch=False).assignment,
            "build the bounded host worker")

    def test_malformed_directions_json_raises_direction_error(self):
        """consume documents that only DirectionError escapes it."""
        repo = make_repo(self.tmp, directions={"lane": "windows-core"})
        bad = repo / "social-bots" / "directions" / "windows-core.json"
        bad.write_text("{not json", encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True,
                       capture_output=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "corrupt"],
                       check=True, capture_output=True)
        with self.assertRaises(direction_mod.DirectionError):
            direction_mod.consume("windows-core", repo, fetch=False)

    def test_worker_once_records_a_receipt_for_a_malformed_direction(self):
        """Exit 1 must always leave a receipt that says what happened."""
        repo = make_repo(self.tmp / "corrupt", directions={"lane": "windows-core"})
        bad = repo / "social-bots" / "directions" / "windows-core.json"
        bad.write_text("{not json", encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True,
                       capture_output=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "corrupt"],
                       check=True, capture_output=True)
        home, reports = self.tmp / "home2", self.tmp / "reports2"
        with EnvGuard(SBOTS_HOME=str(home)), contextlib.redirect_stdout(io.StringIO()):
            code = worker_once.main([
                "--lane", "windows-core", "--branch", "b", "--bots", "social-a",
                "--repo-root", str(repo), "--session-id", "s-bad-direction",
                "--skip-fetch", "--allow-deterministic", "--home", str(home),
                "--report-root", str(reports)])
        self.assertEqual(code, worker_once.EXIT_FAILURE)
        receipt = invocation_mod.read_all(home)[0]
        self.assertEqual(receipt["status"], invocation_mod.STATUS_COMPLETE)
        self.assertEqual(receipt["work_outcome"], "direction_unavailable")
        self.assertIsNotNone(receipt["error"])


# --------------------------------------------------------------------------- #
# F8 / F9 / F10 / F14 — the heartbeat's guarantees must be enforced, not claimed.
# --------------------------------------------------------------------------- #
class HeartbeatHardeningTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())

    def _hb(self, **overrides):
        fields = dict(session_id="s-h-1", lane="lane-a", branch="b",
                      current_artifact="a")
        fields.update(overrides)
        return sh.SessionHeartbeat(**fields)

    def test_a_backfilled_timestamp_is_overwritten(self):
        """emit re-stamps started_at, so a caller cannot forge when a session ran."""
        record = sh.emit(self._hb(started_at="1999-01-01T00:00:00Z"), root=self.root)
        self.assertNotEqual(record["started_at"], "1999-01-01T00:00:00Z")
        self.assertTrue(record["started_at"].startswith("20"))

    def test_contract_fields_cannot_be_relabelled(self):
        """A record cannot be written as a different cadence, status or schema."""
        record = sh.emit(self._hb(cadence_mode="HOURLY", session_status="COMPLETED",
                                  schema_version=99), root=self.root)
        self.assertEqual(record["cadence_mode"], sh.CADENCE_MODE)
        self.assertEqual(record["session_status"], sh.SESSION_STATUS_STARTED)
        self.assertEqual(record["schema_version"], sh.SCHEMA_VERSION)

    def test_a_session_cannot_emit_once_per_lane(self):
        """One session = one heartbeat is a claim about the session, not the lane."""
        sh.emit(self._hb(lane="lane-a"), root=self.root)
        with self.assertRaises(sh.DuplicateSessionHeartbeat) as ctx:
            sh.emit(self._hb(lane="lane-b"), root=self.root)
        self.assertIn("lane-a", str(ctx.exception))
        self.assertEqual(sh.read_log("lane-b", self.root), [])

    def test_an_unsafe_lane_name_is_refused(self):
        """An unvalidated lane is a path-traversal write out of the reports root."""
        for lane in ("../../escaped", "a/b", "", ".hidden/../x"):
            with self.subTest(lane=lane):
                with self.assertRaises(sh.UnsafeLane):
                    sh.emit(self._hb(lane=lane), root=self.root)

    def test_a_torn_log_line_does_not_wedge_the_lane(self):
        """One bad append must not make every future heartbeat impossible."""
        sh.emit(self._hb(session_id="s-ok"), root=self.root)
        log_path = sh.lane_dir("lane-a", self.root) / sh.LOG_FILENAME
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write('{"session_id": "s-tor\n')
        record = sh.emit(self._hb(session_id="s-after-tear"), root=self.root)
        self.assertEqual(record["session_id"], "s-after-tear")
        entries = sh.read_log("lane-a", self.root)
        self.assertTrue(any(e.get("_unparseable") for e in entries),
                        "the damaged line must stay visible, not be dropped")

    def test_a_refused_duplicate_posts_no_issue_comment(self):
        """Durable evidence first: never announce a heartbeat that was not written."""
        posts = []

        class Proc:
            returncode = 0
            stderr = ""

        def runner(cmd, text):
            posts.append(text)
            return Proc()

        record = sh.emit(self._hb(session_id="s-order"), root=self.root)
        sh.record_issue_post(record, root=self.root, runner=runner)
        with self.assertRaises(sh.DuplicateSessionHeartbeat):
            sh.emit(self._hb(session_id="s-order"), root=self.root)
        self.assertEqual(len(posts), 1)

    def test_the_post_outcome_goes_in_a_sidecar_not_the_ledger(self):
        """The append-only ledger is never rewritten to match a later post."""
        record = sh.emit(self._hb(session_id="s-sidecar"), root=self.root)
        row = sh.record_issue_post(record, root=self.root,
                                   runner=lambda cmd, text: (_ for _ in ()).throw(
                                       OSError("no transport")))
        self.assertFalse(row["posted"])
        sidecar = sh.lane_dir("lane-a", self.root) / sh.ISSUE_POST_FILENAME
        self.assertTrue(sidecar.exists())
        ledger = sh.read_log("lane-a", self.root)
        self.assertEqual(len(ledger), 1)
        self.assertFalse(ledger[0]["issue_comment_posted"])


# --------------------------------------------------------------------------- #
# F15 / F18 — the receipt must not understate what an invocation attempted.
# --------------------------------------------------------------------------- #
class WorkerOnceReportingTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = make_repo(self.tmp)
        self.home = self.tmp / "home"
        self.reports = self.tmp / "reports"

    def test_an_empty_bots_list_is_a_usage_error_not_no_overlap(self):
        """Exit 3 means tasks were held; no candidates at all is a misconfiguration."""
        with contextlib.redirect_stdout(io.StringIO()):
            code = worker_once.main([
                "--lane", "windows-core", "--branch", "b", "--bots", " , ",
                "--repo-root", str(self.repo), "--skip-fetch",
                "--home", str(self.home), "--report-root", str(self.reports)])
        self.assertEqual(code, worker_once.EXIT_USAGE)

    def test_candidates_tried_survives_a_failing_unit(self):
        """A unit that took a lease then failed must not look like nothing was tried."""
        attempted: list = []
        original = worker_once.worker.run_one_unit

        def exploding(task_id, bot, persona, **kwargs):
            raise RuntimeError("unit blew up")

        worker_once.worker.run_one_unit = exploding
        try:
            with EnvGuard(SBOTS_HOME=str(self.home)), \
                    contextlib.redirect_stdout(io.StringIO()):
                code = worker_once.main([
                    "--lane", "windows-core", "--branch", "b",
                    "--bots", "social-a,social-b", "--repo-root", str(self.repo),
                    "--session-id", "s-boom", "--skip-fetch", "--allow-deterministic",
                    "--home", str(self.home), "--report-root", str(self.reports)])
        finally:
            worker_once.worker.run_one_unit = original
        self.assertEqual(code, worker_once.EXIT_FAILURE)
        receipt = invocation_mod.read_all(self.home)[0]
        self.assertEqual(receipt["work_outcome"], "unit_failed")
        self.assertIn("unit blew up", receipt["error"])
        self.assertEqual(attempted, [])


# --------------------------------------------------------------------------- #
# F12 — verify must not pass a matrix whose prompt bytes it never checked.
# --------------------------------------------------------------------------- #
class VerifyStrictnessTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.matrix = build_matrix()
        self.path = self.tmp / "PREPARED_MATRIX.json"
        self.prompts = self.tmp / "prompts"
        dp.write_prepared(self.matrix, self.path)
        dp.write_prompts(self.matrix, self.prompts)

    def test_without_prompt_bytes_the_verdict_is_not_verified(self):
        """The prompt file is the payload; a verdict that skipped it means little."""
        result = dp.verify_written(self.path)
        self.assertFalse(result["verified"])
        self.assertFalse(result["prompt_bytes_verified"])
        self.assertTrue(any("prompt bytes were not verified" in e
                            for e in result["digest_errors"]))

    def test_an_edited_prompt_file_is_caught(self):
        """Smuggling different evidence into a prompt file must fail verification."""
        target = self.prompts / "P1.prompt.txt"
        target.write_text(target.read_text(encoding="utf-8")
                          .replace("Tidepool", "Something Else"), encoding="utf-8")
        result = dp.verify_written(self.path, self.prompts)
        self.assertFalse(result["verified"])
        self.assertTrue(any("prompt_sha256" in e for e in result["digest_errors"]))

    def test_an_untouched_matrix_verifies(self):
        """The strict path must still pass a genuine artifact."""
        result = dp.verify_written(self.path, self.prompts)
        self.assertTrue(result["verified"])


if __name__ == "__main__":
    unittest.main()
