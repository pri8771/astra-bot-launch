"""SB-S23-003 — research specialist adapter.

Proves ``runtime/specialist_research.py``:
- fixture sources become EvidenceCapture files + a ResearchResult, hashes verify;
- a raising collector marks only that source failed (no fabricated capture);
- a provider can only rank/summarize captured evidence; invented ids are dropped;
- deadlines produce TIMED_OUT with only fully written files listed;
- role mismatch, failed context, missing sources and forged provenance fail
  closed; writes never leave the sandbox; no effect/publish surface.

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
from runtime import specialist_research as sr  # noqa: E402

SRC_A, SRC_B = "https://example.org/a", "https://example.org/b"


def contract(role="researcher", sources=(SRC_A, SRC_B), **kw):
    base = dict(bot="social-a", persona="social-a", parent_run_id="run-1", role=role,
                objective="collect sources", expected_output_schema="ResearchResult/1",
                time_budget_s=10,
                input_artifacts=[{"kind": "source_candidate", "url": u} for u in sources])
    base.update(kw)
    return sc.new_contract(**base)


def tree(root, skip=("scratch",)):
    root = Path(root)
    out = []
    for p in root.rglob("*"):
        rel = p.relative_to(root).as_posix()
        if rel.split("/")[0] in skip:
            continue
        out.append((rel, p.read_bytes() if p.is_file() else None))
    return sorted(out)


class StubProvider:
    adaptive = False
    provider_id = "stub-fixture"

    def __init__(self, proposal):
        self.proposal, self.calls = proposal, 0

    def propose(self, ctx):
        self.calls += 1
        return self.proposal


class ResearchSpecialistTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp
        self.collector = sr.FixtureCollector({SRC_A: "alpha text", SRC_B: {"k": "v"}})

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_it(self, c, **kw):
        s = sb.Sandbox(c)
        s.create()
        kw.setdefault("collector", self.collector)
        return sr.ResearchSpecialist().run(c, s, **kw), s

    # 1
    def test_two_sources_become_evidence_and_result(self):
        c = contract()
        r, s = self.run_it(c)
        self.assertEqual(r.result, "COMPLETED")
        self.assertEqual(sc.validate_result(r, c), [])
        self.assertEqual([o["path"] for o in r.outputs],
                         ["evidence/000.json", "evidence/001.json", "outputs/research_result.json"])
        for o in r.outputs:
            self.assertEqual(s.sha256(o["path"]), o["sha256"])
        self.assertEqual(len(r.evidence_refs), 2)
        self.assertTrue(all(e["status"] == "ok" and e["provenance"] == "fixture"
                            and len(e["content_hash"]) == 64 for e in r.evidence_refs))
        doc = json.loads(s.read("outputs/research_result.json"))
        self.assertEqual(doc["schema"], "ResearchResult/1")
        self.assertEqual(doc["captured"], 2)
        self.assertEqual(doc["unresolved"], [])
        ev0 = json.loads(s.read("evidence/000.json"))
        self.assertEqual(ev0["receipt"]["source_url"], SRC_A)
        self.assertEqual(ev0["receipt"]["extracted"]["text"], "alpha text")
        self.assertEqual(r.calls_used, 0)
        self.assertEqual(r.effect_attempts, 0)
        self.assertEqual(r.provenance, "fixture")

    # 2
    def test_raising_collector_marks_only_that_source_failed(self):
        c = contract()
        coll = sr.FixtureCollector({SRC_A: "alpha", SRC_B: "beta"}, raise_for={SRC_B})
        r, s = self.run_it(c, collector=coll)
        self.assertEqual(r.result, "COMPLETED")
        self.assertEqual([e["url"] for e in r.evidence_refs], [SRC_A])
        doc = json.loads(s.read("outputs/research_result.json"))
        self.assertEqual(len(doc["unresolved"]), 1)
        self.assertEqual(doc["unresolved"][0]["source"], SRC_B)
        self.assertIn("RuntimeError", doc["unresolved"][0]["error"])
        ev1 = json.loads(s.read("evidence/001.json"))
        self.assertEqual(ev1["receipt"]["status"], "failed")
        self.assertIsNone(ev1["receipt"]["content_hash"])
        # An unknown source is a truthful failure, not a fabricated capture.
        c2 = contract(sources=("https://example.org/missing",))
        r2, _ = self.run_it(c2)
        self.assertEqual(r2.evidence_refs, [])
        self.assertEqual(r2.result, "COMPLETED")

    # 3
    def test_provider_cannot_invent_evidence(self):
        c = contract(model_call_budget=1)
        stub = StubProvider({"ranked_evidence_ids": ["ev-invented", "x"], "summary": ["s1", 3, ""]})
        bp = sbud.BudgetedProvider(stub, c, artifact="A", lane="L", run_scope="S",
                                   manifest_dir=tempfile.mkdtemp())
        r, s = self.run_it(c, provider=bp)
        self.assertEqual(r.result, "COMPLETED")
        self.assertEqual(stub.calls, 1)
        self.assertEqual(r.calls_used, 1)
        self.assertTrue(any("uncaptured evidence ids" in l for l in r.limitations), r.limitations)
        doc = json.loads(s.read("outputs/research_result.json"))
        self.assertEqual(len(doc["evidence_refs"]), 2)       # nothing invented, nothing lost
        self.assertIn("s1", doc["summary"])
        # A provider that ranks real ids reorders; one that raises is a limitation, not a failure.
        c2 = contract(model_call_budget=0)
        bp2 = sbud.BudgetedProvider(StubProvider({}), c2, artifact="A", lane="L", run_scope="S",
                                    manifest_dir=tempfile.mkdtemp())
        r2, _ = self.run_it(c2, provider=bp2)
        self.assertEqual(r2.result, "COMPLETED")
        self.assertTrue(any("provider unavailable" in l for l in r2.limitations))
        # Unwrapped providers are refused outright.
        with self.assertRaises(sr.AdapterError):
            self.run_it(contract(), provider=StubProvider({}))

    # 4
    def test_deadline_yields_timed_out_with_only_complete_files(self):
        c = contract()
        r, s = self.run_it(c, deadline=sbud.Deadline(budget_s=0, clock=lambda: 0.0))
        self.assertEqual(r.result, "TIMED_OUT")
        self.assertEqual([o["path"] for o in r.outputs], ["outputs/research_result.json"])
        self.assertEqual(r.evidence_refs, [])
        self.assertEqual(sc.validate_result(r, c), [])
        # Mid-run timeout: one capture lands, the second does not.
        t = {"now": 0.0}

        class TickingCollector(sr.FixtureCollector):
            def capture(self, ref):
                t["now"] += 1.0
                return super().capture(ref)
        c2 = contract()
        # Each capture advances the clock by 1s; a 0.5s budget lets the first
        # capture complete (it is kept) and trips the check before the second.
        r2, s2 = self.run_it(c2, collector=TickingCollector({SRC_A: "a", SRC_B: "b"}),
                             deadline=sbud.Deadline(budget_s=0.5, clock=lambda: t["now"]))
        self.assertEqual(r2.result, "TIMED_OUT")
        self.assertEqual([o["path"] for o in r2.outputs],
                         ["evidence/000.json", "outputs/research_result.json"])
        self.assertEqual(len(r2.evidence_refs), 1)
        for o in r2.outputs:
            self.assertEqual(s2.sha256(o["path"]), o["sha256"])

    # 5
    def test_role_mismatch(self):
        c = contract(role="writer", expected_output_schema="DraftResult/1")
        s = sb.Sandbox(c)
        s.create()
        with self.assertRaises(sr.RoleMismatch):
            sr.ResearchSpecialist().run(c, s)
        self.assertEqual(s.list(), [])

    # 6
    def test_writes_stay_inside_the_sandbox(self):
        before = tree(self.tmp)
        c = contract()
        r, s = self.run_it(c)
        self.assertEqual(tree(self.tmp), before)                       # nothing outside scratch/
        root = Path(self.tmp) / "scratch" / "social-a" / c.worker_id
        for o in r.outputs:
            self.assertTrue((root / o["path"]).is_file())
        self.assertFalse((Path(self.tmp) / "content").exists())
        self.assertFalse((Path(self.tmp) / "memory").exists())

    # 7
    def test_module_has_no_effect_or_network_surface(self):
        import ast
        tree_ = ast.parse(Path(sr.__file__).read_text(encoding="utf-8"))
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
        # Modules this adapter must never import (network, runtime stores, effects).
        forbidden_imports = {"subprocess", "requests", "urllib", "socket", "http", "collector",
                             "pipeline", "decision", "reasoning", "reasoning_cli", "worker",
                             "state", "leasing", "research", "analytics", "isolation"}
        # Names/attributes it must never touch (state objects, effect paths).
        forbidden_refs = {"PersonaState", "RuntimeState", "content_dir", "state_dir",
                          "memory_dir", "publish", "enqueue", "register_experiment",
                          "admin_all_records", "run_cycle", "run_one_unit"}
        self.assertEqual(imported & forbidden_imports, set())
        self.assertEqual(referenced & forbidden_refs, set())

    # 8
    def test_failed_context_means_no_run(self):
        c = contract(bounded_context_refs=[
            {"kind": "decisions", "bot": "social-a", "persona": "cultural-primandir-atman"}])
        s = sb.Sandbox(c)
        s.create()
        with self.assertRaises(sb.ContextError):
            s.materialize_context(sb.PersonaSnapshotResolver("social-a", "social-a"))
        r = sr.ResearchSpecialist().run(c, s, collector=self.collector)
        self.assertEqual(r.result, "FAILED")
        self.assertIn("context", r.error)
        self.assertEqual(r.outputs, [])
        self.assertEqual(r.evidence_refs, [])
        self.assertEqual(self.collector.calls, 0)
        self.assertEqual(sc.validate_result(r, c), [])
        # A sandbox for a different worker is refused.
        other = sb.Sandbox(contract())
        other.create()
        with self.assertRaises(sr.AdapterError):
            sr.ResearchSpecialist().run(c, other)

    # 9
    def test_missing_sources_completes_with_limitation(self):
        c = contract(sources=())
        r, s = self.run_it(c)
        self.assertEqual(r.result, "COMPLETED")
        self.assertEqual(r.evidence_refs, [])
        self.assertIn("no sources", r.limitations)
        self.assertEqual([o["path"] for o in r.outputs], ["outputs/research_result.json"])
        self.assertEqual(self.collector.calls, 0)
        # capture_source narrowed away: nothing captured, truthfully unresolved.
        c2 = contract(allowed_tools={"read_context", "write_scratch"})
        r2, s2 = self.run_it(c2)
        self.assertEqual(r2.result, "COMPLETED")
        self.assertEqual(r2.evidence_refs, [])
        self.assertTrue(any("capture_source not granted" in l for l in r2.limitations))
        self.assertEqual(json.loads(s2.read("outputs/research_result.json"))["failed"], 2)
        # write_scratch narrowed away: cannot produce outputs at all.
        c3 = contract(allowed_tools={"read_context"})
        r3, s3 = self.run_it(c3)
        self.assertEqual(r3.result, "FAILED")
        self.assertEqual(s3.list(), [])

    def test_forged_provenance_is_recorded_as_failed(self):
        c = contract(sources=(SRC_A,))
        forged = sr.FixtureCollector({SRC_A: "x"}, forge_provenance="trusted_operational")
        r, s = self.run_it(c, collector=forged)
        self.assertEqual(r.result, "COMPLETED")
        self.assertEqual(r.evidence_refs, [])
        ev = json.loads(s.read("evidence/000.json"))
        self.assertEqual(ev["receipt"]["status"], "failed")
        self.assertIn("forged", ev["receipt"]["error"])
        self.assertTrue(sr.validate_receipt({"status": "ok"}))
        self.assertTrue(sr.validate_receipt("nope"))


if __name__ == "__main__":
    unittest.main()
