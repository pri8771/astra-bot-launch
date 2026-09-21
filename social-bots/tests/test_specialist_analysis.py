"""SB-S23-004 — analyst and reviewer specialist adapters.

Proves ``runtime/specialist_analysis.py``:
- the analyst emits one finding per resolvable evidence ref (confidence None);
  provider findings without resolvable refs become unsupported claims;
- the reviewer PASSes a consistent bundle, FAILs an uncovered/unsupported claim
  or a non-DRAFT_UNPUBLISHED draft, and a provider cannot flip FAIL to PASS;
- the reviewer/analyst can write only their own result file (RestrictedView);
  input bytes are never changed; reviewed_sha256 matches the files;
- missing inputs => NEEDS_EVIDENCE; role mismatch; cross-persona context =>
  FAILED; deadline => TIMED_OUT; no effect/state surface.

Evidence class: ENGINEERING. No network, no model call, no effect.
"""
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import specialist_contract as sc  # noqa: E402
from runtime import specialist_sandbox as sb  # noqa: E402
from runtime import specialist_budget as sbud  # noqa: E402
from runtime import specialist_analysis as sa  # noqa: E402

SHA = "b" * 64


def ref(i, status="ok"):
    return {"evidence_id": f"ev-{i}", "source_id": f"src-{i}", "url": f"https://e.org/{i}",
            "captured_at": "2026-09-21T21:00:00+00:00", "content_hash": SHA if status == "ok" else None,
            "provenance": "fixture", "collector_version": "1.0.0", "status": status}


def capture_doc(i, status="ok"):
    return {"schema": "EvidenceCapture/1", "index": i, "evidence_ref": ref(i, status),
            "receipt": {"status": status, "receipt_id": f"cap-{i}"}}


def research_doc(ids):
    return {"schema": "ResearchResult/1", "evidence_refs": [ref(i) for i in ids]}


def analysis_doc(findings):
    return {"schema": "AnalysisResult/1", "findings": findings}


def draft_doc(claims, status="DRAFT_UNPUBLISHED"):
    return {"schema": "DraftResult/1", "candidate": {"status": status, "body": "x"}, "claims": claims}


def contract(role, **kw):
    schema = {"analyst": "AnalysisResult/1", "reviewer": "ReviewResult/1"}.get(role, "DraftResult/1")
    base = dict(bot="social-a", persona="social-a", parent_run_id="run-1", role=role,
                objective="o", expected_output_schema=schema, time_budget_s=10)
    base.update(kw)
    return sc.new_contract(**base)


class StubProvider:
    adaptive = False
    provider_id = "stub-fixture"

    def __init__(self, proposal):
        self.proposal, self.calls = proposal, 0

    def propose(self, ctx):
        self.calls += 1
        return self.proposal


class AnalysisAdaptersTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def sandbox_with(self, c, files):
        s = sb.Sandbox(c)
        s.create()
        for rel, doc in files.items():
            s.write(rel, doc)
        return s

    def wrap(self, stub, c, budget=1):
        return sbud.BudgetedProvider(stub, c, artifact="A", lane="L", run_scope="S",
                                     manifest_dir=tempfile.mkdtemp())

    # 1
    def test_analyst_one_finding_per_resolvable_ref(self):
        c = contract("analyst")
        s = self.sandbox_with(c, {"inputs/research_result.json": research_doc([1, 2, 3]),
                                  "inputs/evidence/000.json": capture_doc(1),
                                  "inputs/evidence/009.json": capture_doc(9, status="failed")})
        r = sa.AnalystSpecialist().run(c, s)
        self.assertEqual(r.result, "COMPLETED")
        self.assertEqual(sc.validate_result(r, c), [])
        doc = json.loads(s.read(sa.ANALYST_RESULT_PATH))
        self.assertEqual(doc["schema"], "AnalysisResult/1")
        self.assertEqual(len(doc["findings"]), 3)                  # ev-9 failed: not evidence
        for f in doc["findings"]:
            self.assertIsNone(f["confidence"])
            self.assertEqual(len(f["evidence_refs"]), 1)
            self.assertEqual(f["evidence_refs"][0]["status"], "ok")
        self.assertEqual(sorted(e["evidence_id"] for e in r.evidence_refs), ["ev-1", "ev-2", "ev-3"])
        self.assertEqual([o["path"] for o in r.outputs], [sa.ANALYST_RESULT_PATH])
        self.assertEqual(s.sha256(sa.ANALYST_RESULT_PATH), r.outputs[0]["sha256"])
        self.assertEqual(set(doc["inputs_reviewed"]),
                         {"inputs/research_result.json", "inputs/evidence/000.json",
                          "inputs/evidence/009.json"})

    # 2
    def test_provider_finding_without_refs_becomes_unsupported(self):
        c = contract("analyst", model_call_budget=1)
        s = self.sandbox_with(c, {"inputs/research_result.json": research_doc([1])})
        stub = StubProvider({"findings": [
            {"statement": "grounded", "evidence_ids": ["ev-1"], "confidence": 0.7},
            {"statement": "ungrounded", "evidence_ids": ["ev-404"]},
            {"statement": "bad confidence", "evidence_ids": ["ev-1"], "confidence": 7},
            "malformed"], "unsupported_claims": ["also ungrounded"]})
        r = sa.AnalystSpecialist().run(c, s, provider=self.wrap(stub, c))
        self.assertEqual(r.result, "COMPLETED")
        self.assertEqual(stub.calls, 1)
        self.assertEqual(r.calls_used, 1)
        doc = json.loads(s.read(sa.ANALYST_RESULT_PATH))
        statements = [f["statement"] for f in doc["findings"]]
        self.assertIn("grounded", statements)
        self.assertIn("bad confidence", statements)
        self.assertNotIn("ungrounded", statements)
        self.assertEqual(doc["unsupported_claims"], ["ungrounded", "also ungrounded"])
        conf = {f["statement"]: f["confidence"] for f in doc["findings"]}
        self.assertEqual(conf["grounded"], 0.7)
        self.assertIsNone(conf["bad confidence"])
        self.assertTrue(any("malformed" in l for l in doc["limitations"]))

    # 3
    def test_reviewer_pass_on_consistent_bundle(self):
        c = contract("reviewer")
        files = {"inputs/evidence/000.json": capture_doc(1),
                 "inputs/analysis.json": analysis_doc([{"statement": "s", "evidence_refs": [ref(1)]}]),
                 "inputs/draft.json": draft_doc([{"text": "t", "evidence_refs": [{"evidence_id": "ev-1"}]}])}
        s = self.sandbox_with(c, files)
        r = sa.ReviewerSpecialist().run(c, s)
        self.assertEqual(r.result, "COMPLETED")
        self.assertEqual(sc.validate_result(r, c), [])
        doc = json.loads(s.read(sa.REVIEWER_RESULT_PATH))
        self.assertEqual(doc["verdict"], "PASS")
        self.assertEqual(doc["issues"], [])
        self.assertEqual(set(doc["reviewed_sha256"]), set(files))
        for rel, digest in doc["reviewed_sha256"].items():
            self.assertEqual(s.sha256(rel), digest)
        self.assertEqual(r.evidence_refs, [])

    # 4
    def test_reviewer_fails_uncovered_claim_and_provider_cannot_flip(self):
        c = contract("reviewer", model_call_budget=1)
        s = self.sandbox_with(c, {
            "inputs/evidence/000.json": capture_doc(1), "inputs/evidence/001.json": capture_doc(2),
            "inputs/analysis.json": analysis_doc([{"statement": "s", "evidence_refs": [ref(1)]}]),
            "inputs/draft.json": draft_doc([{"text": "no finding", "evidence_refs": [ref(2)]},
                                            {"text": "no evidence", "evidence_refs": []}])})
        stub = StubProvider({"verdict": "PASS", "issues": []})
        r = sa.ReviewerSpecialist().run(c, s, provider=self.wrap(stub, c))
        doc = json.loads(s.read(sa.REVIEWER_RESULT_PATH))
        self.assertEqual(doc["verdict"], "FAIL")
        self.assertEqual(sorted(i["kind"] for i in doc["issues"]), ["uncovered_claim", "unsupported_claim"])
        self.assertTrue(any("provider PASS ignored" in l for l in doc["limitations"]))
        # Deterministic integrity is pure and reusable.
        issues = sa.ReviewerSpecialist.integrity_issues(sa.Bundle(sa.RestrictedView(s, "outputs/x")))
        self.assertEqual(len(issues), 2)
        # Draft with a non-unpublished status fails.
        c2 = contract("reviewer")
        s2 = self.sandbox_with(c2, {"inputs/evidence/000.json": capture_doc(1),
                                    "inputs/analysis.json": analysis_doc([{"statement": "s", "evidence_refs": [ref(1)]}]),
                                    "inputs/draft.json": draft_doc([{"text": "t", "evidence_refs": [ref(1)]}], status="QUEUED")})
        sa.ReviewerSpecialist().run(c2, s2)
        doc2 = json.loads(s2.read(sa.REVIEWER_RESULT_PATH))
        self.assertEqual(doc2["verdict"], "FAIL")
        self.assertEqual([i["kind"] for i in doc2["issues"]], ["draft_status"])
        # A finding with no resolvable evidence fails too.
        c3 = contract("reviewer")
        s3 = self.sandbox_with(c3, {"inputs/analysis.json": analysis_doc([{"statement": "s", "evidence_refs": [ref(7)]}])})
        sa.ReviewerSpecialist().run(c3, s3)
        self.assertEqual(json.loads(s3.read(sa.REVIEWER_RESULT_PATH))["verdict"], "FAIL")
        # Provider issues on a deterministic PASS become NEEDS_EVIDENCE, never FAIL-as-fact.
        c4 = contract("reviewer", model_call_budget=1)
        s4 = self.sandbox_with(c4, {"inputs/evidence/000.json": capture_doc(1),
                                    "inputs/analysis.json": analysis_doc([{"statement": "s", "evidence_refs": [ref(1)]}])})
        sa.ReviewerSpecialist().run(c4, s4, provider=self.wrap(StubProvider({"issues": [{"detail": "tone"}]}), c4))
        doc4 = json.loads(s4.read(sa.REVIEWER_RESULT_PATH))
        self.assertEqual(doc4["verdict"], "NEEDS_EVIDENCE")
        self.assertEqual(doc4["issues"][0]["kind"], "provider_issue")

    # 5
    def test_reviewer_cannot_write_outside_its_result_file(self):
        c = contract("reviewer")
        s = self.sandbox_with(c, {"inputs/draft.json": draft_doc([])})
        before = s.read("inputs/draft.json")
        view = sa.RestrictedView(s, sa.REVIEWER_RESULT_PATH)
        for bad in ("inputs/draft.json", "context/x.json", "outputs/other.json", "evidence/0.json"):
            with self.assertRaises(sa.WriteDenied, msg=bad):
                view.write(bad, {"tampered": True})
        self.assertEqual(s.read("inputs/draft.json"), before)
        view.write(sa.REVIEWER_RESULT_PATH, {"ok": True})              # its own file is allowed
        # A full run leaves every input byte unchanged and adds only the result.
        r = sa.ReviewerSpecialist().run(c, s)
        self.assertEqual(r.result, "COMPLETED")
        self.assertEqual(s.read("inputs/draft.json"), before)
        self.assertEqual(s.list(), ["inputs/draft.json", sa.REVIEWER_RESULT_PATH])

    # 6
    def test_missing_input_needs_evidence_and_unreadable_is_a_limitation(self):
        c = contract("reviewer")
        s = self.sandbox_with(c, {})
        r = sa.ReviewerSpecialist().run(c, s)
        self.assertEqual(r.result, "COMPLETED")
        doc = json.loads(s.read(sa.REVIEWER_RESULT_PATH))
        self.assertEqual(doc["verdict"], "NEEDS_EVIDENCE")
        self.assertEqual(doc["issues"][0]["kind"], "no_reviewable_input")
        c2 = contract("reviewer")
        s2 = self.sandbox_with(c2, {})
        s2.write("inputs/broken.json", b"{not json")
        r2 = sa.ReviewerSpecialist().run(c2, s2)
        doc2 = json.loads(s2.read(sa.REVIEWER_RESULT_PATH))
        self.assertEqual(doc2["verdict"], "NEEDS_EVIDENCE")
        self.assertTrue(any("unreadable input inputs/broken.json" in l for l in r2.limitations))
        # Analyst with no evidence: empty findings + limitation, not invented findings.
        c3 = contract("analyst")
        s3 = self.sandbox_with(c3, {})
        r3 = sa.AnalystSpecialist().run(c3, s3)
        self.assertEqual(r3.result, "COMPLETED")
        self.assertIn("no evidence inputs", r3.limitations)
        self.assertEqual(json.loads(s3.read(sa.ANALYST_RESULT_PATH))["findings"], [])

    # 7
    def test_role_mismatch_for_both(self):
        for adapter, wrong in ((sa.AnalystSpecialist(), "reviewer"), (sa.ReviewerSpecialist(), "analyst")):
            c = contract(wrong)
            s = self.sandbox_with(c, {})
            with self.assertRaises(sa.RoleMismatch):
                adapter.run(c, s)
            self.assertEqual(s.list(), [])
        with self.assertRaises(sa.AdapterError):
            sa.AnalystSpecialist().run(contract("analyst"), self.sandbox_with(contract("analyst"), {}))
        with self.assertRaises(sa.AdapterError):
            c = contract("analyst")
            sa.AnalystSpecialist().run(c, self.sandbox_with(c, {}), provider=StubProvider({}))

    # 8
    def test_cross_persona_context_fails_closed(self):
        c = contract("analyst", persona="cultural-primandir-atman", bounded_context_refs=[
            {"kind": "decisions", "bot": "social-a", "persona": "social-a"}])
        s = sb.Sandbox(c)
        s.create()
        with self.assertRaises(sb.ContextError):
            s.materialize_context(sb.PersonaSnapshotResolver("social-a", "cultural-primandir-atman"))
        r = sa.AnalystSpecialist().run(c, s)
        self.assertEqual(r.result, "FAILED")
        self.assertIn("context", r.error)
        self.assertEqual(r.outputs, [])
        self.assertEqual(sc.validate_result(r, c), [])

    # 9
    def test_deadline_timed_out(self):
        for adapter, role in ((sa.AnalystSpecialist(), "analyst"), (sa.ReviewerSpecialist(), "reviewer")):
            c = contract(role)
            s = self.sandbox_with(c, {"inputs/evidence/000.json": capture_doc(1)})
            r = adapter.run(c, s, deadline=sbud.Deadline(budget_s=0, clock=lambda: 0.0))
            self.assertEqual(r.result, "TIMED_OUT")
            self.assertEqual(r.outputs, [])
            self.assertEqual(sc.validate_result(r, c), [])

    # 10
    def test_module_has_no_effect_or_state_surface(self):
        import ast
        tree_ = ast.parse(Path(sa.__file__).read_text(encoding="utf-8"))
        imported, referenced = set(), set()
        for node in ast.walk(tree_):
            if isinstance(node, ast.Import):
                imported |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom):
                imported |= {(node.module or "").split(".")[-1]} | {a.name for a in node.names}
            elif isinstance(node, ast.Name):
                referenced.add(node.id)
            elif isinstance(node, ast.Attribute):
                referenced.add(node.attr)
        self.assertEqual(imported & {"subprocess", "requests", "urllib", "socket", "collector",
                                     "pipeline", "decision", "reasoning", "reasoning_cli",
                                     "worker", "state", "leasing", "factcheck", "isolation"}, set())
        self.assertEqual(referenced & {"PersonaState", "RuntimeState", "content_dir", "state_dir",
                                       "memory_dir", "publish", "enqueue", "register_experiment",
                                       "run_cycle"}, set())


if __name__ == "__main__":
    unittest.main()
