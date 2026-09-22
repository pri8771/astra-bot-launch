"""SB-R07-041 / C04 — negative regressions for the shared pre-dispatch gate.

LEAD-047 reproduced these P0 defects on the earlier source:
  * a registered model callable executed with no grant (direct-library bypass);
  * a caller-supplied label (``adaptive=False``, fixture attribute, injected-
    runner marker) exempted an object from authorization;
  * accounting ran after dispatch and was private to one wrapper, so
    concurrent, reentrant and multi-wrapper calls overran a one-slot budget.

Every test here is ENGINEERING-ONLY: fixture manifests in temp dirs, synthetic
callables, and ``subprocess.run`` replaced with a tripwire wherever the real
CLI launcher is in play. No model is called, nothing is spent, and the fixtures
prove the gate's behaviour — not live completion of anything.
"""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "bin"))

from runtime import authorization, decision, model_dispatch, reasoning, research  # noqa: E402
from runtime import divergence_prepare as dp  # noqa: E402
from runtime import reasoning_cli  # noqa: E402
from runtime import reasoning_receipt as rr  # noqa: E402
from runtime.reasoning import ReasoningContext  # noqa: E402

from tests.test_v04_authorization_gate import valid_manifest  # noqa: E402

ART, LANE, SCOPE = "SB-TEST-GATE", "windows-core", "gate-test"


def _ctx(persona_id="social-b", **over):
    base = dict(
        persona={"id": persona_id, "kind": "general", "display_name": persona_id},
        objective="grow audience",
        top_signal={"id": "sig-1", "title": "t", "summary": "s", "tags": ["x"],
                    "provenance": "fixture", "url": "https://e.org/1"},
        pending_count=1, is_duplicate=False, draft={"content_id": "c-1"},
        state_summary={"hypotheses": 0})
    base.update(over)
    return ReasoningContext(**base)


def _proposal():
    return reasoning.ReasoningProposal(
        alternatives=[reasoning.no_action("fixture: wait")], recommended_action="NO_ACTION",
        uncertainties=["fixture"], provider_id="model-adaptive-v0", adaptive=True)


def _counting(result=None, raise_exc=None):
    """A raw callable (a LIVE route by classification) that counts invocations."""
    calls = []

    def fn(ctx):
        calls.append(ctx)
        if raise_exc is not None:
            raise raise_exc
        return _proposal() if result is None else result
    fn.calls = calls
    return fn


def _seed(bot):
    research.capture(bot, research.Signal.make(
        "sig", "captured", "unit-test", "https://example.org/s", "fixture", ["measurement"]))


def _write_manifest(directory: Path, **overrides) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "fixture.json"
    path.write_text(json.dumps(valid_manifest(**overrides)), encoding="utf-8")
    return path


class _Env:
    """Set env vars for the test and restore them exactly, including absence."""

    def __init__(self, **values):
        self.values, self.prior = values, {}

    def __enter__(self):
        for k, v in self.values.items():
            self.prior[k] = os.environ.get(k)
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        return self

    def __exit__(self, *exc):
        for k, prior in self.prior.items():
            if prior is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = prior
        return False


class _GateCase(unittest.TestCase):
    """Common hygiene: fresh temp home, no API key, no leaked scope or callable."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.manifests = self.tmp / "authorizations"
        self.manifests.mkdir()
        self.env = _Env(ANTHROPIC_API_KEY=None, SBOTS_HOME=str(self.tmp), SBOTS_REASONING=None,
                        SBOTS_REASONING_REQUIRE_ADAPTIVE=None)
        self.env.__enter__()
        model_dispatch.clear()
        reasoning.register_model_callable(None)

    def tearDown(self):
        model_dispatch.clear()
        reasoning.register_model_callable(None)
        self.env.__exit__(None, None, None)

    def budget(self, run_scope=SCOPE, max_calls=5):
        return authorization.CallBudget(run_scope, max_calls, home=self.tmp)


# --------------------------------------------------------------------------- #
# 1. Classification is by exact policy-owned type — labels never exempt.
# --------------------------------------------------------------------------- #
class ClassificationTest(_GateCase):
    def test_raw_callables_are_live_whatever_they_claim(self):
        def labelled(ctx):
            return _proposal()
        labelled.adaptive = False
        labelled.fixture = True
        labelled.engineering_only = True
        labelled.__sbots_injected_runner__ = True

        class LookAlike:                       # duck-typed, same attribute surface
            adaptive = False
            label = "engineering-stub"

            def __call__(self, ctx):
                return _proposal()

        for fn in (labelled, LookAlike(), lambda ctx: _proposal()):
            with self.subTest(fn=fn):
                self.assertEqual(model_dispatch.classify(fn), model_dispatch.LIVE_MODEL)

    def test_subclasses_of_the_exempt_types_are_live(self):
        class StubSubclass(reasoning.EngineeringStub):
            pass

        class ReplaySubclass(rr.ReceiptReplay):
            pass

        self.assertEqual(model_dispatch.classify(StubSubclass(lambda c: None)),
                         model_dispatch.LIVE_MODEL)
        self.assertEqual(model_dispatch.classify(ReplaySubclass([])), model_dispatch.LIVE_MODEL)

    def test_exact_policy_types_are_classified_non_live(self):
        self.assertEqual(model_dispatch.classify(reasoning.EngineeringStub(lambda c: None)),
                         model_dispatch.ENGINEERING_STUB)
        self.assertEqual(model_dispatch.classify(rr.replay_callable([])),
                         model_dispatch.RECEIPT_REPLAY)

    def test_a_label_bypass_through_the_provider_never_runs(self):
        """The LEAD-047 label exemption: marked callables are refused, not run."""
        fn = _counting()
        fn.adaptive = False
        fn.__sbots_injected_runner__ = True
        provider = reasoning.ModelReasoningProvider(fn)
        self.assertFalse(provider.available())
        self.assertIsNone(provider.propose(_ctx()))
        self.assertEqual(fn.calls, [])
        self.assertIn("no dispatch scope", provider.reason)


# --------------------------------------------------------------------------- #
# 2. Direct-library bypass: without a configured scope nothing live runs.
# --------------------------------------------------------------------------- #
class DirectLibraryBypassTest(_GateCase):
    def test_gate_refuses_a_live_callable_without_a_scope(self):
        fn = _counting()
        with self.assertRaises(model_dispatch.DispatchRefused) as ctx:
            model_dispatch.dispatch(fn, _ctx(), provider_id="direct")
        self.assertIn("no dispatch scope configured", str(ctx.exception))
        self.assertEqual(fn.calls, [])
        rec = model_dispatch.last_record()
        self.assertEqual((rec.dispatch_class, rec.invoked), (model_dispatch.LIVE_MODEL, False))

    def test_provider_over_a_raw_callable_is_unavailable_and_never_invokes(self):
        fn = _counting()
        provider = reasoning.ModelReasoningProvider(fn)
        self.assertFalse(provider.available())
        self.assertIsNone(provider.propose(_ctx()))
        self.assertEqual(fn.calls, [])

    def test_engine_fails_closed_with_no_silent_baseline_fallback(self):
        """Adaptive required + unauthorized live route -> BLOCKED, not baseline."""
        fn = _counting()
        _seed("social-b")
        with _Env(SBOTS_REASONING="model"):
            reasoning.register_model_callable(fn)
            rec = decision.run_cycle("social-b", "social-b", require_adaptive=True)
        self.assertEqual(rec["outcome"], "blocked_reasoning_unavailable")
        self.assertEqual(rec["reasoning"]["provider"], "model-adaptive-v0")
        self.assertFalse(rec["reasoning"]["live_model_call"])
        self.assertIn("not authorized", rec["execute"]["block_reason"])
        self.assertEqual(fn.calls, [])
        self.assertIsNone(rec["observe"]["consumed_this_cycle"])   # evidence stays pending
        self.assertEqual(rec["observe"]["pending_after"], 1)

    def test_a_declared_stub_runs_outside_production_and_is_labelled_offline(self):
        fn = _counting()
        _seed("social-b")
        with _Env(SBOTS_REASONING="model"):
            reasoning.register_model_callable(reasoning.EngineeringStub(fn))
            rec = decision.run_cycle("social-b", "social-b")
        self.assertEqual(rec["outcome"], "no_action")
        self.assertEqual(len(fn.calls), 1)
        self.assertEqual(rec["reasoning"]["dispatch"]["dispatch_class"],
                         model_dispatch.ENGINEERING_STUB)
        self.assertFalse(rec["reasoning"]["live_model_call"])

    def test_receipt_replay_is_never_a_live_call(self):
        _seed("social-b")
        with _Env(SBOTS_REASONING="model"):
            reasoning.register_model_callable(rr.replay_callable([]))   # no matching receipt
            rec = decision.run_cycle("social-b", "social-b")
        self.assertEqual(rec["outcome"], "blocked_reasoning_unavailable")
        self.assertEqual(rec["reasoning"]["dispatch"]["dispatch_class"],
                         model_dispatch.RECEIPT_REPLAY)
        self.assertFalse(rec["reasoning"]["live_model_call"])


# --------------------------------------------------------------------------- #
# 3. Under a scope + fixture manifest: exact accounting, before invocation.
# --------------------------------------------------------------------------- #
class ScopedDispatchTest(_GateCase):
    def setUp(self):
        super().setUp()
        _write_manifest(self.manifests, artifact_scope=[ART], lane=LANE, run_scope=SCOPE)
        self.scope = model_dispatch.configure(ART, LANE, SCOPE, manifest_dir=self.manifests,
                                              home=self.tmp)

    def test_slot_is_reserved_before_the_callable_runs_and_recorded_after(self):
        seen = {}
        budget = self.budget()

        def fn(ctx):
            seen["consumed_during_call"] = budget.consumed()
            seen["unrecorded_during_call"] = budget.audit()["reserved_not_recorded"]
            return _proposal()

        provider = reasoning.ModelReasoningProvider(fn)
        self.assertTrue(provider.available())
        self.assertIsNotNone(provider.propose(_ctx()))
        self.assertEqual(seen, {"consumed_during_call": 1, "unrecorded_during_call": [1]})
        self.assertEqual(budget.audit()["outcomes"], [{"slot": 1, "outcome": "proposal_received"}])
        rec = model_dispatch.last_record()
        self.assertEqual((rec.dispatch_class, rec.invoked, rec.slot, rec.manifest_id, rec.outcome),
                         (model_dispatch.LIVE_MODEL, True, 1, "AUTH-FIXTURE-0001",
                          "proposal_received"))

    def test_decision_record_cites_the_live_dispatch_and_one_slot(self):
        fn = _counting()
        _seed("social-b")
        with _Env(SBOTS_REASONING="model"):
            reasoning.register_model_callable(fn)
            rec = decision.run_cycle("social-b", "social-b", require_adaptive=True)
        self.assertEqual(rec["outcome"], "no_action")
        self.assertTrue(rec["reasoning"]["live_model_call"])
        self.assertEqual(rec["reasoning"]["dispatch"]["slot"], 1)
        self.assertEqual(rec["reasoning"]["dispatch"]["dispatch_class"], model_dispatch.LIVE_MODEL)
        self.assertEqual(len(fn.calls), 1)
        # available() is consulted twice by the engine; it never consumes a slot.
        self.assertEqual(self.budget().consumed(), 1)

    def test_last_slot_concurrency_admits_exactly_one_invocation(self):
        manifests = self.tmp / "one-slot"
        _write_manifest(manifests, artifact_scope=[ART], lane=LANE, run_scope="gate-last-slot",
                        max_calls=1)
        scope = model_dispatch.DispatchScope(ART, LANE, "gate-last-slot",
                                             manifest_dir=str(manifests), home=str(self.tmp))
        n = 8
        barrier = threading.Barrier(n)
        invoked, refused, errors = [], [], []
        lock = threading.Lock()

        def fn(ctx):
            with lock:
                invoked.append(threading.get_ident())
            return _proposal()

        def worker():
            barrier.wait()
            try:
                model_dispatch.dispatch(fn, _ctx(), provider_id="t", scope=scope)
            except authorization.CallBudgetExhausted:
                with lock:
                    refused.append(1)
            except Exception as exc:                  # noqa: BLE001 - surfaced below
                with lock:
                    errors.append(repr(exc))

        threads = [threading.Thread(target=worker) for _ in range(n)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30)
        self.assertEqual(errors, [])
        self.assertEqual(len(invoked), 1)
        self.assertEqual(len(refused), n - 1)
        audit = authorization.CallBudget("gate-last-slot", 1, home=self.tmp).audit()
        self.assertEqual(audit["consumed"], 1)
        self.assertEqual(audit["outcomes"], [{"slot": 1, "outcome": "proposal_received"}])

    def test_reentry_on_the_same_thread_is_refused_and_costs_one_slot(self):
        inner = _counting()

        def outer(ctx):
            return model_dispatch.dispatch(inner, ctx, provider_id="inner")   # re-enters

        provider = reasoning.ModelReasoningProvider(outer)
        self.assertIsNone(provider.propose(_ctx()))
        self.assertIn("provider exception after dispatch", provider.reason)
        self.assertIn("reentrant", provider.reason)
        self.assertEqual(inner.calls, [])
        self.assertEqual(self.budget().audit()["outcomes"],
                         [{"slot": 1, "outcome": "provider_exception"}])

    def test_reserving_inside_an_active_dispatch_is_refused(self):
        def outer(ctx):
            with model_dispatch.reserved(self.scope):
                pass

        with self.assertRaises(model_dispatch.DispatchRefused):
            model_dispatch.dispatch(outer, _ctx(), provider_id="outer")
        self.assertEqual(self.budget().consumed(), 1)     # the outer slot only

    def test_an_exception_consumes_the_slot_and_a_later_call_takes_a_new_one(self):
        boom = _counting(raise_exc=RuntimeError("fixture failure"))
        provider = reasoning.ModelReasoningProvider(boom)
        self.assertIsNone(provider.propose(_ctx()))
        self.assertIn("provider exception", provider.reason)
        self.assertEqual(self.budget().audit()["outcomes"],
                         [{"slot": 1, "outcome": "provider_exception"}])
        ok = reasoning.ModelReasoningProvider(_counting())
        self.assertIsNotNone(ok.propose(_ctx()))
        self.assertEqual(self.budget().audit()["outcomes"],
                         [{"slot": 1, "outcome": "provider_exception"},
                          {"slot": 2, "outcome": "proposal_received"}])

    def test_budget_exhaustion_refuses_before_invocation(self):
        fn = _counting()
        for _ in range(5):
            model_dispatch.dispatch(fn, _ctx(), provider_id="t")
        with self.assertRaises(authorization.CallBudgetExhausted):
            model_dispatch.dispatch(fn, _ctx(), provider_id="t")
        self.assertEqual(len(fn.calls), 5)
        self.assertFalse(reasoning.ModelReasoningProvider(fn).available())

    def test_an_expired_manifest_is_refused_at_dispatch_time(self):
        """A grant that was fresh earlier is re-judged at every dispatch (stale grant)."""
        fn = _counting()
        self.assertTrue(model_dispatch.availability()[0])
        later = datetime.now(timezone.utc) + timedelta(hours=3)
        with mock.patch.object(authorization, "_now", return_value=later):
            self.assertFalse(model_dispatch.availability()[0])
            with self.assertRaises(authorization.AuthorizationDenied) as ctx:
                model_dispatch.dispatch(fn, _ctx(), provider_id="t")
        self.assertIn("expired", str(ctx.exception))
        self.assertEqual(fn.calls, [])
        self.assertEqual(self.budget().consumed(), 0)

    def test_a_manifest_removed_after_availability_is_refused_at_dispatch(self):
        fn = _counting()
        provider = reasoning.ModelReasoningProvider(fn)
        self.assertTrue(provider.available())
        for p in self.manifests.glob("*.json"):
            p.unlink()
        self.assertIsNone(provider.propose(_ctx()))
        self.assertIn("live model call refused", provider.reason)
        self.assertEqual(fn.calls, [])
        self.assertEqual(self.budget().consumed(), 0)

    def test_posture_violation_refuses_before_reserving(self):
        fn = _counting()
        with _Env(ANTHROPIC_API_KEY="fixture-value-never-used"):
            with self.assertRaises(model_dispatch.DispatchRefused) as ctx:
                model_dispatch.dispatch(fn, _ctx(), provider_id="t")
        self.assertIn("ANTHROPIC_API_KEY", str(ctx.exception))
        self.assertEqual(fn.calls, [])
        self.assertEqual(self.budget().consumed(), 0)

    def test_engineering_stub_is_refused_under_a_production_scope(self):
        fn = _counting()
        provider = reasoning.ModelReasoningProvider(reasoning.EngineeringStub(fn))
        self.assertFalse(provider.available())
        self.assertIn("engineering stub refused", provider.reason)
        self.assertIsNone(provider.propose(_ctx()))
        self.assertEqual(fn.calls, [])
        self.assertEqual(self.budget().consumed(), 0)
        _seed("social-b")
        with _Env(SBOTS_REASONING="model"):
            reasoning.register_model_callable(reasoning.EngineeringStub(fn))
            rec = decision.run_cycle("social-b", "social-b", require_adaptive=True)
        self.assertEqual(rec["outcome"], "blocked_reasoning_unavailable")
        self.assertIn("engineering stub refused", rec["execute"]["block_reason"])
        self.assertEqual(fn.calls, [])

    def test_a_scope_that_allows_stubs_still_never_counts_them_as_live(self):
        fn = _counting()
        model_dispatch.configure(ART, LANE, SCOPE, manifest_dir=self.manifests, home=self.tmp,
                                 allow_engineering_stubs=True)
        provider = reasoning.ModelReasoningProvider(reasoning.EngineeringStub(fn))
        self.assertTrue(provider.available())
        self.assertIsNotNone(provider.propose(_ctx()))
        self.assertEqual(model_dispatch.last_record().dispatch_class,
                         model_dispatch.ENGINEERING_STUB)
        self.assertEqual(self.budget().consumed(), 0)

    def test_dropped_batch_token_is_never_adopted_by_a_later_call(self):
        with model_dispatch.reserved(self.scope) as (_grant, _budget, slot):
            self.assertEqual(slot.slot, 1)                # nobody adopts it
        fn = _counting()
        model_dispatch.dispatch(fn, _ctx(), provider_id="later")
        self.assertEqual(model_dispatch.last_record().slot, 2)
        audit = self.budget().audit()
        self.assertEqual(audit["reserved_not_recorded"], [1])
        self.assertEqual(audit["consumed"], 2)

    def test_a_crash_after_reservation_leaves_the_slot_consumed_across_processes(self):
        """Process death mid-call is over-counted (safe), never reclaimed."""
        child = f"""
import os, sys
sys.path.insert(0, {str(ROOT)!r})
from runtime import model_dispatch
model_dispatch.configure({ART!r}, {LANE!r}, "gate-crash",
                         manifest_dir={str(self.tmp / "crash")!r}, home={str(self.tmp)!r})
def die(ctx):
    os._exit(7)                       # dies after the slot file exists
model_dispatch.dispatch(die, None, provider_id="crash")
"""
        _write_manifest(self.tmp / "crash", artifact_scope=[ART], lane=LANE,
                        run_scope="gate-crash")
        env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        proc = subprocess.run([sys.executable, "-c", child], env=env, capture_output=True,
                              text=True, timeout=60)
        self.assertEqual(proc.returncode, 7, proc.stderr)
        audit = authorization.CallBudget("gate-crash", 5, home=self.tmp).audit()
        self.assertEqual(audit["consumed"], 1)
        self.assertEqual(audit["reserved_not_recorded"], [1])
        # The survivor takes slot 2; slot 1 is never re-issued.
        scope = model_dispatch.DispatchScope(ART, LANE, "gate-crash",
                                             manifest_dir=str(self.tmp / "crash"),
                                             home=str(self.tmp))
        model_dispatch.dispatch(_counting(), _ctx(), provider_id="survivor", scope=scope)
        self.assertEqual(model_dispatch.last_record().slot, 2)


# --------------------------------------------------------------------------- #
# 4. The real CLI launcher: never spawned without authorization; when it is
#    reached, the slot is already consumed. subprocess.run is a tripwire.
# --------------------------------------------------------------------------- #
class SpawnAttempted(AssertionError):
    pass


def _tripwire(*args, **kwargs):
    raise SpawnAttempted("subprocess.run must not be reached")


class RealLauncherGateTest(_GateCase):
    def setUp(self):
        super().setUp()
        self._patch = mock.patch.object(reasoning_cli.subprocess, "run", _tripwire)
        self._patch.start()

    def tearDown(self):
        self._patch.stop()
        super().tearDown()

    def test_real_launcher_is_refused_without_a_scope(self):
        provider = reasoning_cli.ClaudeCodeReasoningProvider()
        self.assertTrue(provider._spawns_for_real())
        self.assertFalse(provider.available())
        self.assertIn("no dispatch scope", provider.reason)
        self.assertIsNone(provider.propose(_ctx()))

    def test_real_launcher_is_refused_under_a_scope_without_a_manifest(self):
        model_dispatch.configure(ART, LANE, SCOPE, manifest_dir=self.manifests, home=self.tmp)
        provider = reasoning_cli.ClaudeCodeReasoningProvider()
        self.assertFalse(provider.available())
        self.assertIn("no canonical authorization manifest", provider.reason)
        self.assertIsNone(provider.propose(_ctx()))
        self.assertEqual(self.budget().consumed(), 0)

    def test_real_launcher_is_refused_on_posture_even_with_a_manifest(self):
        _write_manifest(self.manifests, artifact_scope=[ART], lane=LANE, run_scope=SCOPE)
        model_dispatch.configure(ART, LANE, SCOPE, manifest_dir=self.manifests, home=self.tmp)
        provider = reasoning_cli.ClaudeCodeReasoningProvider()
        with _Env(ANTHROPIC_API_KEY="fixture-value-never-used"):
            self.assertFalse(provider.available())
            self.assertIsNone(provider.propose(_ctx()))
        self.assertEqual(self.budget().consumed(), 0)

    def test_real_launcher_reserves_a_slot_before_the_subprocess_is_attempted(self):
        """With a fixture manifest in force the gate admits the launcher; the slot
        is consumed BEFORE subprocess.run, which the tripwire proves was the next
        step (no real process is created)."""
        _write_manifest(self.manifests, artifact_scope=[ART], lane=LANE, run_scope=SCOPE)
        model_dispatch.configure(ART, LANE, SCOPE, manifest_dir=self.manifests, home=self.tmp)
        provider = reasoning_cli.ClaudeCodeReasoningProvider()
        with mock.patch.object(reasoning_cli.shutil, "which", return_value="/fixture/claude"):
            self.assertTrue(provider.available())
            self.assertIsNone(provider.propose(_ctx()))
        self.assertIn("cli launch error", provider.reason)
        self.assertEqual(self.budget().audit()["outcomes"],
                         [{"slot": 1, "outcome": "provider_exception"}])
        rec = model_dispatch.last_record()
        self.assertEqual((rec.dispatch_class, rec.invoked, rec.slot),
                         (model_dispatch.LIVE_MODEL, True, 1))

    def test_injected_runner_is_a_seam_outside_production_and_refused_inside(self):
        calls = []

        def runner(prompt, *, timeout_s, model):
            calls.append(prompt)
            return reasoning_cli.CLIResult(returncode=0, stdout="{}", stderr="")

        provider = reasoning_cli.ClaudeCodeReasoningProvider(runner=runner)
        self.assertTrue(provider.available())           # no scope: engineering seam
        model_dispatch.configure(ART, LANE, SCOPE, manifest_dir=self.manifests, home=self.tmp)
        self.assertFalse(provider.available())
        self.assertIn("injected runner refused", provider.reason)
        self.assertIsNone(provider.propose(_ctx()))
        self.assertEqual(calls, [])

    def test_a_wrapper_around_the_real_launcher_cannot_ride_the_seam_in_production(self):
        _write_manifest(self.manifests, artifact_scope=[ART], lane=LANE, run_scope=SCOPE)
        model_dispatch.configure(ART, LANE, SCOPE, manifest_dir=self.manifests, home=self.tmp)

        def wrapper(prompt, *, timeout_s, model):       # would launch for real
            return reasoning_cli._CAPTURED_REAL_CLI_RUNNER(prompt, timeout_s=timeout_s,
                                                           model=model)

        provider = reasoning_cli.ClaudeCodeReasoningProvider(runner=wrapper)
        self.assertFalse(provider.available())
        self.assertIsNone(provider.propose(_ctx()))
        self.assertEqual(self.budget().consumed(), 0)


# --------------------------------------------------------------------------- #
# 5. Batch executor: one reservation per case, adopted by the provider's gate.
# --------------------------------------------------------------------------- #
class BatchTokenAdoptionTest(_GateCase):
    def setUp(self):
        super().setUp()
        from tests.test_v04_divergence_prepare import PERSONAS, build, default_snapshots
        self.matrix = build()
        self.personas, self.snapshots = PERSONAS, default_snapshots()
        _write_manifest(self.manifests, run_scope=self.matrix.run_scope)   # SB-V04-002 scope
        self.grant = authorization.ExecutionGrant(
            manifest_id="AUTH-FIXTURE-0001", manifest_path="(fixture)",
            manifest_digest="sha256:fixture", created_by="test-fixture",
            owner_authorization_ref="engineering fixture", artifact="SB-V04-002",
            lane="windows-core", run_scope=self.matrix.run_scope,
            provider_mode="claude-cli", max_calls=5, expires_at="2099-01-01T00:00:00Z",
            granted_at="2026-09-21T00:00:00Z")
        self.batch_budget = authorization.CallBudget(self.matrix.run_scope, 5, home=self.tmp)

    def _run(self, provider, case_id="P0"):
        case = self.matrix.case(case_id)
        return dp._execute_one_case(
            case, provider, self.batch_budget, grant=self.grant, draft={},
            persona=self.personas[case.persona_slot], objective=self.matrix.objective,
            snapshot_signal=self.snapshots[case.evidence_id].signal,
            pending_count=0, is_duplicate=False, prior_hypotheses=0,
            manifest_dir=self.manifests)

    def test_provider_gate_adopts_the_batch_reservation_without_a_second_slot(self):
        fn = _counting()

        class Provider:
            provider_id = "adopting-fixture"
            reason = None

            def propose(self, ctx):
                return model_dispatch.dispatch(fn, ctx, provider_id=self.provider_id, live=True)

        result = self._run(Provider())
        self.assertEqual((result["outcome"], result["slot"]), ("proposal_received", 1))
        self.assertEqual(len(fn.calls), 1)
        self.assertEqual(self.batch_budget.audit()["outcomes"],
                         [{"slot": 1, "outcome": "proposal_received"}])
        rec = model_dispatch.last_record()
        self.assertEqual((rec.dispatch_class, rec.slot, rec.outcome),
                         (model_dispatch.LIVE_MODEL, 1, "proposal_received"))

    def test_five_cases_consume_exactly_five_slots_then_refuse(self):
        fn = _counting()

        class Provider:
            provider_id = "adopting-fixture"
            reason = None

            def propose(self, ctx):
                return model_dispatch.dispatch(fn, ctx, provider_id=self.provider_id, live=True)

        for case in self.matrix.cases:
            self._run(Provider(), case.case_id)
        self.assertEqual(len(fn.calls), 5)
        self.assertEqual(self.batch_budget.consumed(), 5)
        with self.assertRaises(authorization.CallBudgetExhausted):
            self._run(Provider())
        self.assertEqual(len(fn.calls), 5)

    def test_a_provider_that_re_enters_the_gate_inside_the_batch_costs_one_slot(self):
        inner = _counting()

        class Provider:
            provider_id = "reentrant-fixture"
            reason = None

            def propose(self, ctx):
                def outer(c):
                    return model_dispatch.dispatch(inner, c, provider_id="inner")
                return model_dispatch.dispatch(outer, ctx, provider_id=self.provider_id,
                                               live=True)

        result = self._run(Provider())
        self.assertEqual(result["outcome"], "provider_exception")
        self.assertEqual(inner.calls, [])
        self.assertEqual(self.batch_budget.consumed(), 1)

    def test_execute_batch_holds_the_scope_only_for_the_batch(self):
        fn = _counting()

        class Provider:
            provider_id = "batch-fixture"
            reason = None

            def propose(self, ctx):
                seen.append(model_dispatch.current_scope())
                return model_dispatch.dispatch(fn, ctx, provider_id=self.provider_id, live=True)

        seen = []
        # An injected provider factory is a posture violation for execute_batch
        # (injected_runner=True), which is the documented gate; prove that first.
        with self.assertRaises(authorization.AuthorizationDenied):
            dp.execute_batch(self.matrix, lane="windows-core", personas=self.personas,
                             snapshots=self.snapshots, provider_factory=Provider,
                             manifest_dir=self.manifests, home=self.tmp)
        self.assertEqual(fn.calls, [])
        self.assertIsNone(model_dispatch.current_scope())


# --------------------------------------------------------------------------- #
# 6. Production entrypoints install the scope and undo it on exit.
# --------------------------------------------------------------------------- #
class EntrypointWiringTest(_GateCase):
    def test_run_worker_installs_a_production_scope_that_refuses_a_stub(self):
        import run_worker
        _write_manifest(self.manifests, artifact_scope=["SB-RUNTIME-WORKER"], lane="windows-core",
                        run_scope="run-worker:social-a")
        fn = _counting()
        _seed("social-a")
        out = io.StringIO()
        argv_prior = sys.argv[:]
        try:
            sys.argv = ["run_worker.py", "social-a"]
            with _Env(SBOTS_REASONING="model", SBOTS_MANIFEST_DIR=str(self.manifests),
                      SBOTS_LANE="windows-core"), contextlib.redirect_stdout(out):
                reasoning.register_model_callable(reasoning.EngineeringStub(fn))
                code = run_worker.main()
        finally:
            sys.argv = argv_prior
        self.assertEqual(code, 0, out.getvalue())
        self.assertIn("blocked_reasoning_unavailable", out.getvalue())
        self.assertEqual(fn.calls, [])                   # stub refused in production
        self.assertIsNone(model_dispatch.current_scope())   # undone on exit
        self.assertEqual(self.budget("run-worker:social-a").consumed(), 0)

    def test_worker_once_installs_the_route_guard_scope_before_direction(self):
        import worker_once
        home = self.tmp / "home"
        seen = {}

        def fake_consume(lane, repo_root, fetch=True):
            seen["scope"] = model_dispatch.current_scope()
            raise worker_once.direction_mod.DirectionError("fixture: no direction")

        err = io.StringIO()
        with mock.patch.object(worker_once.direction_mod, "consume", fake_consume), \
                _Env(SBOTS_REASONING="baseline"), contextlib.redirect_stderr(err):
            code = worker_once.main([
                "--lane", "windows-core", "--branch", "fixture", "--bots", "social-a",
                "--repo-root", str(self.tmp), "--skip-fetch", "--home", str(home),
                "--manifest-dir", str(self.manifests)])
        self.assertEqual(code, worker_once.EXIT_FAILURE)
        self.assertEqual(seen["scope"], model_dispatch.DispatchScope(
            artifact="SB-V07-001", lane="windows-core", run_scope="worker-once:windows-core",
            manifest_dir=str(self.manifests), home=str(home), allow_engineering_stubs=False))
        self.assertIsNone(model_dispatch.current_scope())


if __name__ == "__main__":
    unittest.main()
