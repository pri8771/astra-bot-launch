"""SB-S23-001 — specialist worker contract runtime (schema v2).

Proves the least-authority contract boundary in ``runtime/specialist_contract.py``:

- every role builds a valid contract whose tools are exactly the role allowlist
  and whose ``external_effect_budget`` is fixed at 0;
- tools outside the allowlist (publish, spawn_specialist, ...) cannot be granted;
- ``decision.Authority`` or any of its fields cannot reach a contract;
- credential-shaped keys cannot appear in the bounded context, even by reference;
- ``validate_result`` rejects effect attempts, budget overrun, escaping output
  paths, identity/persona mismatches and unknown result states;
- JSON round-trip is lossless and reload never silently widens.

Evidence class: ENGINEERING. Every record here is ``provenance="fixture"``.
No sandbox, execution, lease, provider or model call is involved.
"""
import json
import os
import sys
import tempfile
import unittest
from dataclasses import FrozenInstanceError, fields
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import specialist_contract as sc  # noqa: E402
from runtime import decision  # noqa: E402

SHA = "a" * 64


def contract(**kw):
    base = dict(bot="social-a", persona="social-a", parent_run_id="run-1",
                role="researcher", objective="collect two sources",
                expected_output_schema="ResearchResult/1", time_budget_s=30)
    base.update(kw)
    return sc.new_contract(**base)


def result(c, **kw):
    base = dict(worker_id=c.worker_id, parent_run_id=c.parent_run_id, bot=c.bot,
                persona=c.persona, role=c.role,
                started_at="2026-09-21T21:00:00+00:00",
                finished_at="2026-09-21T21:00:05+00:00",
                source_ref="deadbeef", result="COMPLETED",
                outputs=[{"schema": "ResearchResult/1", "path": "outputs/r.json",
                          "sha256": SHA}])
    base.update(kw)
    return sc.WorkerResult(**base)


class ContractConstructionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp

    def test_every_role_builds_least_authority_contract(self):
        for role in sc.ROLES:
            c = contract(role=role)
            self.assertEqual(sc.validate_contract(c), [])
            self.assertEqual(set(c.allowed_tools), set(sc.ROLE_TOOLS[role]))
            self.assertEqual(c.external_effect_budget, 0)
            self.assertEqual(c.scratch_scope, c.worker_id)
            self.assertEqual(c.schema_version, 2)
            self.assertEqual(c.provenance, "fixture")
            self.assertGreater(sc._parse_iso(c.expires_at), sc._parse_iso(c.created_at))

    def test_tools_outside_role_allowlist_are_refused(self):
        for bad in ({"publish"}, {"spawn_specialist"}, {"read_context", "enqueue"},
                    {"update_state"}, {"register_experiment"}, {"message_users"}):
            with self.assertRaises(sc.ContractError):
                contract(allowed_tools=bad)
        # A researcher-only tool is outside an analyst's allowlist.
        with self.assertRaises(sc.ContractError):
            contract(role="analyst", allowed_tools={"capture_source"})
        # Narrowing is allowed.
        c = contract(allowed_tools={"read_context"})
        self.assertEqual(c.allowed_tools, ["read_context"])

    def test_decision_authority_cannot_reach_a_contract(self):
        with self.assertRaises(sc.ContractError):
            contract(authority=decision.Authority())
        with self.assertRaises(sc.ContractError):
            contract(authority={"read_context_refs": True, "can_public_post": True})
        for key in ("can_public_post", "can_spend", "can_message_users",
                    "authority_scope", "external_effect_budget"):
            with self.assertRaises(sc.ContractError):
                contract(**{key: True})
        # ... and not inside nested structures either.
        with self.assertRaises(sc.ContractError):
            contract(bounded_context_refs=[{"kind": "persona", "can_public_post": True}])
        with self.assertRaises(sc.ContractError):
            contract(input_artifacts=[{"kind": "x", "nested": {"can_spend": 1}}])
        with self.assertRaises(sc.ContractError):
            contract(stop_conditions=[{"kind": "time", "external_effect_budget": 5}])

    def test_specialist_authority_has_no_effect_fields_and_is_frozen(self):
        a = sc.SpecialistAuthority()
        for name in ("can_public_post", "can_spend", "can_message_users",
                     "can_update_state", "can_register_experiment", "can_create_candidate"):
            self.assertFalse(hasattr(a, name), name)
        self.assertEqual([f.name for f in fields(a)],
                         ["read_context_refs", "write_scratch", "emit_result"])
        with self.assertRaises(FrozenInstanceError):
            a.write_scratch = False
        with self.assertRaises(sc.ContractError):
            sc.SpecialistAuthority(read_context_refs="yes")

        class Wider(sc.SpecialistAuthority):
            pass
        self.assertTrue(sc.validate_authority(Wider()))
        with self.assertRaises(sc.ContractError):
            contract(authority=Wider())
        # Narrowed authority is accepted.
        c = contract(authority=sc.SpecialistAuthority(write_scratch=False))
        self.assertFalse(c.authority.write_scratch)

    def test_external_effect_budget_is_not_a_constructor_parameter(self):
        c = contract()
        with self.assertRaises(TypeError):
            sc.WorkerContract(**{**{k: v for k, v in c.as_dict().items()
                                    if k != "authority"},
                                 "authority": c.authority,
                                 "external_effect_budget": 1})
        with self.assertRaises(FrozenInstanceError):
            c.external_effect_budget = 1
        # A dict form claiming a widened budget cannot be reloaded.
        d = c.as_dict()
        d["external_effect_budget"] = 1
        with self.assertRaises(sc.ContractError):
            sc.WorkerContract.from_dict(d)

    def test_credential_shaped_context_refs_are_refused(self):
        for ref in ({"session_cookie": "abc"}, {"kind": "account", "token": "ref:1"},
                    {"kind": "x", "nested": {"api_key": "ref"}},
                    {"kind": "x", "password_ref": "vault://1"}):
            with self.assertRaises(sc.ContractError):
                contract(bounded_context_refs=[ref])
            with self.assertRaises(sc.ContractError):
                contract(input_artifacts=[ref])
        # Ordinary evidence refs are fine.
        c = contract(bounded_context_refs=[{"kind": "evidence", "id": "ev-1"}])
        self.assertEqual(c.bounded_context_refs, [{"kind": "evidence", "id": "ev-1"}])

    def test_denied_tools_overlapping_allowed_is_an_error(self):
        with self.assertRaises(sc.ContractError):
            contract(denied_tools={"write_scratch"})
        c = contract(denied_tools={"publish"})
        self.assertEqual(c.denied_tools, ["publish"])

    def test_expiry_before_creation_is_an_error(self):
        with self.assertRaises(sc.ContractError):
            contract(ttl_s=-1)
        with self.assertRaises(sc.ContractError):
            contract(ttl_s=0)
        with self.assertRaises(sc.ContractError):
            contract(time_budget_s=0)
        with self.assertRaises(sc.ContractError):
            contract(time_budget_s=float("nan"))

    def test_scope_and_identity_validation(self):
        with self.assertRaises(sc.ContractError):
            contract(persona="../x")
        with self.assertRaises(sc.ContractError):
            contract(bot="not-a-bot")
        with self.assertRaises(sc.ContractError):
            contract(worker_id="../escape")
        with self.assertRaises(sc.ContractError):
            contract(role="publisher")
        with self.assertRaises(sc.ContractError):
            contract(expected_output_schema="free text")
        with self.assertRaises(sc.ContractError):
            contract(model_call_budget=-1)
        with self.assertRaises(sc.ContractError):
            contract(provenance="live")
        with self.assertRaises(sc.ContractError):
            contract(stop_conditions=[{"detail": "no kind"}])

    def test_round_trip_is_lossless_and_reload_never_widens(self):
        c = contract(bounded_context_refs=[{"kind": "evidence", "id": "ev-1"}],
                     stop_conditions=[{"kind": "time", "seconds": 30}],
                     model_call_budget=2, denied_tools={"publish"})
        d = json.loads(json.dumps(c.as_dict(), sort_keys=True))
        c2 = sc.WorkerContract.from_dict(d)
        self.assertEqual(c2, c)
        self.assertEqual(c2.as_dict(), c.as_dict())
        self.assertIs(type(c2.authority), sc.SpecialistAuthority)
        # Unknown key on reload -> error (no silent widening).
        widened = dict(d, can_public_post=True)
        with self.assertRaises(sc.ContractError):
            sc.WorkerContract.from_dict(widened)
        # Authority with an extra key -> error.
        bad_auth = dict(d, authority=dict(d["authority"], can_spend=True))
        with self.assertRaises(sc.ContractError):
            sc.WorkerContract.from_dict(bad_auth)
        # Missing key -> error.
        missing = {k: v for k, v in d.items() if k != "scratch_scope"}
        with self.assertRaises(sc.ContractError):
            sc.WorkerContract.from_dict(missing)
        # A reloaded contract with tools outside its allowlist is rejected even
        # though it was never built through new_contract.
        tampered = dict(d, allowed_tools=["read_context", "publish"])
        with self.assertRaises(sc.ContractError):
            sc.WorkerContract.from_dict(tampered)

    def test_worker_ids_are_unique_and_safe(self):
        ids = {contract().worker_id for _ in range(50)}
        self.assertEqual(len(ids), 50)
        self.assertTrue(all(sc._SAFE_WORKER_ID.match(i) for i in ids))


class ResultValidationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp
        self.c = contract(model_call_budget=2)

    def test_valid_result(self):
        self.assertEqual(sc.validate_result(result(self.c), self.c), [])
        r = result(self.c, result="FAILED", error="adapter raised", outputs=[])
        self.assertEqual(sc.validate_result(r, self.c), [])

    def test_effect_attempt_is_rejected(self):
        errs = sc.validate_result(result(self.c, effect_attempts=1), self.c)
        self.assertTrue(any("effect" in e for e in errs), errs)

    def test_call_budget_overrun_is_rejected(self):
        self.assertEqual(sc.validate_result(result(self.c, calls_used=2), self.c), [])
        errs = sc.validate_result(result(self.c, calls_used=3), self.c)
        self.assertTrue(any("calls_used" in e for e in errs), errs)
        errs = sc.validate_result(result(self.c, calls_used=-1), self.c)
        self.assertTrue(errs)

    def test_escaping_output_paths_are_rejected(self):
        for bad in ("../escape.json", "/abs/x.json", "outputs/../../x", "a\\b",
                    "", "C:x", "outputs/./x.json"):
            r = result(self.c, outputs=[{"schema": "ResearchResult/1", "path": bad,
                                          "sha256": SHA}])
            errs = sc.validate_result(r, self.c)
            self.assertTrue(any("path" in e for e in errs), (bad, errs))
        r = result(self.c, outputs=[{"schema": "ResearchResult/1", "path": "o/x",
                                      "sha256": "nothex"}])
        self.assertTrue(any("sha256" in e for e in sc.validate_result(r, self.c)))
        r = result(self.c, outputs=[{"schema": "ResearchResult/1", "path": "o/x",
                                      "sha256": SHA, "extra": 1}])
        self.assertTrue(any("unknown keys" in e for e in sc.validate_result(r, self.c)))

    def test_identity_and_persona_mismatch_are_rejected(self):
        for name, value in (("worker_id", "w-000000000000"), ("parent_run_id", "run-9"),
                            ("bot", "social-b"), ("persona", "social-b"),
                            ("role", "writer")):
            errs = sc.validate_result(result(self.c, **{name: value}), self.c)
            self.assertTrue(any(name in e for e in errs), (name, errs))

    def test_enumerations_and_timestamps(self):
        self.assertTrue(sc.validate_result(result(self.c, result="DONE"), self.c))
        self.assertTrue(sc.validate_result(result(self.c, cleanup_status="GONE"), self.c))
        self.assertTrue(sc.validate_result(result(self.c, provenance="live"), self.c))
        self.assertTrue(sc.validate_result(result(self.c, schema_version=1), self.c))
        self.assertTrue(sc.validate_result(
            result(self.c, finished_at="2026-09-21T20:59:59+00:00"), self.c))
        self.assertTrue(sc.validate_result(result(self.c, started_at="yesterday"), self.c))
        self.assertTrue(sc.validate_result(result(self.c, source_ref=""), self.c))
        self.assertTrue(sc.validate_result(result(self.c, limitations=["ok", 3]), self.c))

    def test_result_round_trip_and_unknown_keys(self):
        r = result(self.c)
        d = json.loads(json.dumps(r.as_dict()))
        self.assertEqual(sc.WorkerResult.from_dict(d), r)
        with self.assertRaises(sc.ContractError):
            sc.WorkerResult.from_dict(dict(d, published=True))
        with self.assertRaises(sc.ContractError):
            sc.WorkerResult.from_dict({k: v for k, v in d.items() if k != "source_ref"})
        with self.assertRaises(FrozenInstanceError):
            r.effect_attempts = 1

    def test_wrong_types_are_rejected_not_raised(self):
        self.assertTrue(sc.validate_result("not a result", self.c))
        self.assertTrue(sc.validate_result(result(self.c), "not a contract"))
        self.assertTrue(sc.validate_contract({"worker_id": "x"}))


class NoEffectSurfaceTest(unittest.TestCase):
    def test_module_has_no_effect_or_provider_code_paths(self):
        # AST-based (not a raw grep) so prose in docstrings/comments that *names*
        # a forbidden surface does not mask or fake the check: only imports,
        # calls and attribute/name references count.
        import ast
        tree = ast.parse(Path(sc.__file__).read_text(encoding="utf-8"))
        referenced = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                referenced |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom):
                referenced |= {(node.module or "").split(".")[-1]}
                referenced |= {a.name for a in node.names}
            elif isinstance(node, ast.Name):
                referenced.add(node.id)
            elif isinstance(node, ast.Attribute):
                referenced.add(node.attr)
        forbidden = {"subprocess", "requests", "urllib", "socket", "pipeline",
                     "decision", "reasoning", "reasoning_cli", "worker", "state",
                     "publish", "enqueue", "register_experiment", "content_dir",
                     "PersonaState", "RuntimeState", "spawn", "leasing"}
        self.assertEqual(referenced & forbidden, set())
        self.assertTrue(sc.ALL_SPECIALIST_TOOLS.isdisjoint(
            {"publish", "enqueue", "spend", "message_users", "update_state",
             "register_experiment", "spawn_specialist"}))


if __name__ == "__main__":
    unittest.main()
