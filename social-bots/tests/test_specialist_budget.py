"""SB-S23-007 — specialist budget and child-spawn guard.

Proves ``runtime/specialist_budget.py``:
- a fixture (non-adaptive) provider needs no manifest and is budget-capped;
- an adaptive provider is refused without a canonical manifest WHATEVER the env
  reasoning mode says, and is never called when refused;
- with a valid fixture manifest it constructs and the budget is the min of the
  contract budget and the grant's max_calls;
- ANTHROPIC_API_KEY (PAYG posture) is refused regardless of manifest;
- deadlines use an injected clock (no sleeping); spawn/tool/effect guards deny
  and record; persona-scope mismatches fail closed; a raising provider still
  consumes a call.

ENGINEERING-ONLY: every manifest and provider here is a fixture. Nothing in this
file authorizes, performs or evidences a real model call.
"""
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import specialist_contract as sc  # noqa: E402
from runtime import specialist_budget as sbud  # noqa: E402
from runtime import authorization  # noqa: E402

ART, LANE, SCOPE = "SB-S23-007-TEST", "specialist-test", "specialist-fixture-run"


def _iso(dt):
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def fixture_manifest(**overrides):
    now = datetime.now(timezone.utc)
    m = {
        "schema_version": "v1", "manifest_id": "AUTH-FIXTURE-S23-007",
        "created_by": "test-fixture-not-the-lead",
        "created_at": _iso(now - timedelta(minutes=5)),
        "owner_authorization_ref": "engineering fixture; no real owner authorization",
        "artifact_scope": [ART], "run_scope": SCOPE, "lane": LANE,
        "provider_mode": "claude-cli", "max_calls": 3,
        "expires_at": _iso(now + timedelta(hours=2)),
        "retry_allowed": False, "public_effect_allowed": False, "spend_authorized": False,
        "api_key_allowed": False, "injected_runner_allowed": False,
    }
    m.update(overrides)
    return m


class StubProvider:
    """Counts calls; ``adaptive`` decides whether it is a live route."""
    def __init__(self, adaptive, raise_on=None):
        self.adaptive = adaptive
        self.provider_id = "stub-adaptive" if adaptive else "stub-fixture"
        self.calls = 0
        self.raise_on = raise_on

    def available(self):
        return True

    def propose(self, ctx):
        self.calls += 1
        if self.raise_on == self.calls:
            raise RuntimeError("provider blew up")
        return {"proposal": self.calls}


def contract(**kw):
    base = dict(bot="social-a", persona="social-a", parent_run_id="run-1", role="analyst",
                objective="o", expected_output_schema="AnalysisResult/1", time_budget_s=5,
                model_call_budget=2)
    base.update(kw)
    return sc.new_contract(**base)


def ctx(persona="social-a", bot="social-a"):
    return SimpleNamespace(persona={"id": persona, "runtime": bot}, objective="o")


class BudgetedProviderTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp
        self.manifests = tempfile.mkdtemp()          # empty: the expected canonical state
        self._env = {k: os.environ.get(k) for k in ("ANTHROPIC_API_KEY", "SBOTS_REASONING")}
        os.environ.pop("ANTHROPIC_API_KEY", None)
        os.environ.pop("SBOTS_REASONING", None)

    def tearDown(self):
        for k, v in self._env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def wrap(self, provider, c=None, **kw):
        return sbud.BudgetedProvider(provider, c or contract(), artifact=ART, lane=LANE,
                                     run_scope=SCOPE, manifest_dir=self.manifests, **kw)

    # 1
    def test_fixture_provider_is_budget_capped_without_manifest(self):
        stub = StubProvider(adaptive=False)
        bp = self.wrap(stub)
        self.assertFalse(bp.ledger.authorization["required"])
        self.assertEqual(bp.propose(ctx()), {"proposal": 1})
        self.assertEqual(bp.propose(ctx()), {"proposal": 2})
        with self.assertRaises(authorization.CallBudgetExhausted):
            bp.propose(ctx())
        self.assertEqual(bp.calls_used, 2)
        self.assertEqual(stub.calls, 2)
        self.assertEqual(bp.remaining, 0)
        self.assertFalse(bp.available())
        self.assertEqual([e["kind"] for e in bp.ledger.events], ["model_call", "model_call"])

    # 2 (+ the env-mode bypass class)
    def test_adaptive_provider_without_manifest_is_refused_and_never_called(self):
        for mode in (None, "baseline", "contextual", "model", "claude-cli"):
            if mode is None:
                os.environ.pop("SBOTS_REASONING", None)
            else:
                os.environ["SBOTS_REASONING"] = mode
            stub = StubProvider(adaptive=True)
            with self.assertRaises(sbud.ProviderNotAuthorized, msg=mode):
                self.wrap(stub)
            self.assertEqual(stub.calls, 0, mode)

    # 3
    def test_adaptive_provider_with_fixture_manifest_constructs_and_is_capped(self):
        Path(self.manifests, "fixture.json").write_text(json.dumps(fixture_manifest()))
        stub = StubProvider(adaptive=True)
        bp = self.wrap(stub, contract(model_call_budget=10))
        self.assertTrue(bp.ledger.authorization["required"])
        self.assertEqual(bp.ledger.authorization["manifest_id"], "AUTH-FIXTURE-S23-007")
        self.assertEqual(bp.budget, 3)                       # min(10, manifest max_calls=3)
        for i in range(3):
            bp.propose(ctx())
        with self.assertRaises(authorization.CallBudgetExhausted):
            bp.propose(ctx())
        self.assertEqual(stub.calls, 3)
        # A manifest for another lane/scope/artifact does not authorize this one.
        for bad in (dict(lane="other-lane"), dict(run_scope="other-scope"),
                    dict(artifact_scope=["SB-OTHER"]), dict(max_calls=6),
                    dict(spend_authorized=True), dict(provider_mode="api")):
            Path(self.manifests, "fixture.json").write_text(json.dumps(fixture_manifest(**bad)))
            stub2 = StubProvider(adaptive=True)
            with self.assertRaises(sbud.ProviderNotAuthorized, msg=bad):
                self.wrap(stub2)
            self.assertEqual(stub2.calls, 0)

    # 4
    def test_api_key_posture_is_refused_regardless_of_manifest(self):
        Path(self.manifests, "fixture.json").write_text(json.dumps(fixture_manifest()))
        os.environ["ANTHROPIC_API_KEY"] = "sk-not-real"
        stub = StubProvider(adaptive=True)
        with self.assertRaises(sbud.ProviderNotAuthorized):
            self.wrap(stub)
        self.assertEqual(stub.calls, 0)

    # 5
    def test_deadline_uses_injected_clock(self):
        t = {"now": 100.0}
        d = sbud.Deadline(contract(time_budget_s=5), clock=lambda: t["now"])
        self.assertFalse(d.expired())
        self.assertAlmostEqual(d.remaining_s(), 5.0)
        d.check()
        t["now"] = 104.9
        d.check()
        t["now"] = 105.0
        self.assertTrue(d.expired())
        with self.assertRaises(sbud.DeadlineExceeded):
            d.check()
        self.assertTrue(sbud.Deadline(budget_s=0, clock=lambda: 0.0).expired())
        self.assertTrue(sbud.Deadline(budget_s=-1, clock=lambda: 0.0).expired())
        with self.assertRaises(sbud.BudgetError):
            sbud.Deadline()
        # The provider honours the deadline too.
        t["now"] = 100.0
        bp = self.wrap(StubProvider(adaptive=False), deadline=d)
        t["now"] = 200.0
        with self.assertRaises(sbud.DeadlineExceeded):
            bp.propose(ctx())
        self.assertEqual(bp.calls_used, 0)                   # never reached the provider

    # 6
    def test_spawn_guard(self):
        c = contract()
        self.assertEqual(sbud.SpawnGuard.depth_of(c), 1)
        sbud.SpawnGuard.assert_depth(c)
        for tool in ("spawn_specialist", "spawn_worker", "create_worker", "delegate_specialist"):
            with self.assertRaises(sbud.ChildSpawnDenied):
                sbud.SpawnGuard.assert_no_child(c, tool)
            with self.assertRaises(sbud.ChildSpawnDenied):
                sbud.SpawnGuard.assert_tool_allowed(c, tool)
        sbud.SpawnGuard.assert_tool_allowed(c, "read_context")
        for tool in ("publish", "capture_source", "update_state"):   # outside analyst allowlist
            with self.assertRaises(sbud.ToolDenied):
                sbud.SpawnGuard.assert_tool_allowed(c, tool)
        nested = contract(parent_run_id="w-0123456789ab")          # a specialist as parent
        self.assertEqual(sbud.SpawnGuard.depth_of(nested), 2)
        with self.assertRaises(sbud.ChildSpawnDenied):
            sbud.SpawnGuard.assert_depth(nested)

    # 7
    def test_effect_guard_denies_and_records(self):
        c = contract()
        ledger = sbud.WorkerLedger.for_contract(c)
        with self.assertRaises(sbud.EffectDenied):
            sbud.EffectGuard.attempt(c, "publish", ledger=ledger)
        with self.assertRaises(sbud.EffectDenied):
            sbud.EffectGuard.attempt(c, "", ledger=ledger)
        self.assertEqual(ledger.effect_attempts, 2)
        self.assertEqual([e["effect"] for e in ledger.events], ["publish", "unspecified"])
        self.assertTrue(all(e["denied"] for e in ledger.events))
        # The recorded count makes the result rejectable by the contract validator.
        r = sc.WorkerResult(worker_id=c.worker_id, parent_run_id=c.parent_run_id, bot=c.bot,
                            persona=c.persona, role=c.role,
                            started_at="2026-09-21T21:00:00+00:00",
                            finished_at="2026-09-21T21:00:01+00:00", source_ref="x",
                            result="COMPLETED", effect_attempts=ledger.effect_attempts)
        self.assertTrue(any("effect" in e for e in sc.validate_result(r, c)))

    # 8
    def test_persona_scope_mismatch_fails_closed(self):
        stub = StubProvider(adaptive=False)
        bp = self.wrap(stub)
        for bad in (ctx(persona="social-b"), ctx(bot="social-b"),
                    SimpleNamespace(persona=None), {}, SimpleNamespace(objective="no persona"),
                    {"persona": "cultural-primandir-atman"}):
            with self.assertRaises(sbud.ScopeMismatch, msg=bad):
                bp.propose(bad)
        self.assertEqual(stub.calls, 0)
        self.assertEqual(bp.calls_used, 0)
        bp.propose({"persona": "social-a", "bot": "social-a"})     # dict contexts work too
        self.assertEqual(stub.calls, 1)

    # 9
    def test_a_raising_provider_still_consumes_a_call(self):
        stub = StubProvider(adaptive=False, raise_on=1)
        bp = self.wrap(stub)
        with self.assertRaises(RuntimeError):
            bp.propose(ctx())
        self.assertEqual(bp.calls_used, 1)
        self.assertFalse(bp.ledger.events[0]["ok"])
        bp.propose(ctx())
        with self.assertRaises(authorization.CallBudgetExhausted):
            bp.propose(ctx())
        self.assertEqual(stub.calls, 2)

    # 10
    def test_module_cannot_spawn_anything(self):
        import ast
        tree = ast.parse(Path(sbud.__file__).read_text(encoding="utf-8"))
        referenced = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                referenced |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom):
                referenced |= {(node.module or "").split(".")[-1]} | {a.name for a in node.names}
            elif isinstance(node, ast.Name):
                referenced.add(node.id)
            elif isinstance(node, ast.Attribute):
                referenced.add(node.attr)
        forbidden = {"subprocess", "os", "requests", "urllib", "socket", "reasoning_cli",
                     "reasoning", "resolve_provider", "register_model_callable",
                     "ClaudeCodeReasoningProvider", "ModelReasoningProvider", "pipeline",
                     "decision", "publish", "enqueue", "register_experiment", "content_dir",
                     "PersonaState", "RuntimeState", "state", "worker"}
        self.assertEqual(referenced & forbidden, set())

    def test_misuse_is_refused(self):
        with self.assertRaises(sbud.BudgetError):
            self.wrap(None)
        with self.assertRaises(sbud.BudgetError):
            self.wrap(object())                                  # no propose
        c = contract()
        bad = sc.WorkerContract(**dict({k: v for k, v in c.as_dict().items()
                                        if k not in ("authority", "external_effect_budget")},
                                       authority=c.authority, model_call_budget=-1))
        with self.assertRaises(sbud.BudgetError):
            self.wrap(StubProvider(adaptive=False), bad)
        with self.assertRaises(sbud.BudgetError):
            sbud.WorkerLedger.for_contract(bad)
        # Budget 0: the very first call is refused before delegation.
        stub = StubProvider(adaptive=False)
        bp = self.wrap(stub, contract(model_call_budget=0))
        with self.assertRaises(authorization.CallBudgetExhausted):
            bp.propose(ctx())
        self.assertEqual(stub.calls, 0)

    def test_env_live_mode_does_not_block_a_fixture_provider_but_is_recorded(self):
        os.environ["SBOTS_REASONING"] = "claude-cli"
        bp = self.wrap(StubProvider(adaptive=False))
        self.assertFalse(bp.ledger.authorization["required"])
        self.assertFalse(bp.ledger.authorization["route"]["permitted"])
        self.assertTrue(bp.ledger.authorization["route"]["live_route_requested"])
        bp.propose(ctx())                                          # fixture; no live call


if __name__ == "__main__":
    unittest.main()
