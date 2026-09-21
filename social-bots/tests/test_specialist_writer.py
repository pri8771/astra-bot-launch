"""SB-S23-005 — writer and media-brief specialist adapters.

Proves ``runtime/specialist_writer.py``:
- a draft is assembled only from findings with resolvable evidence; every claim
  carries refs; the candidate is pipeline-shaped and DRAFT_UNPUBLISHED;
- a provider may rewrite prose but cannot add unreferenced claims or change the
  candidate status;
- a media brief mirrors evidence sources and reports missing alt text as a
  limitation, never as an empty string;
- writes stay inside the sandbox result file; role mismatch, cross-persona
  context, no findings and deadlines fail closed; no effect/state surface.

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
from runtime import specialist_writer as sw  # noqa: E402

SHA = "c" * 64


def ref(i):
    return {"evidence_id": f"ev-{i}", "source_id": f"src-{i}", "url": f"https://e.org/{i}",
            "captured_at": "2026-09-21T21:00:00+00:00", "content_hash": SHA,
            "provenance": "fixture", "collector_version": "1.0.0", "status": "ok"}


def capture_doc(i):
    return {"schema": "EvidenceCapture/1", "index": i, "evidence_ref": ref(i),
            "receipt": {"status": "ok", "receipt_id": f"cap-{i}"}}


def analysis_doc(ids):
    return {"schema": "AnalysisResult/1",
            "findings": [{"statement": f"finding {i}", "evidence_refs": [ref(i)]} for i in ids]}


def contract(role, **kw):
    schema = {"writer": "DraftResult/1", "media": "MediaBriefResult/1"}.get(role, "AnalysisResult/1")
    base = dict(bot="social-a", persona="social-a", parent_run_id="run-1", role=role,
                objective="explain the thing", expected_output_schema=schema, time_budget_s=10)
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


def tree(root, skip=("scratch",)):
    root = Path(root)
    return sorted((p.relative_to(root).as_posix(), p.read_bytes() if p.is_file() else None)
                  for p in root.rglob("*") if p.relative_to(root).parts[0] not in skip)


class WriterAdaptersTest(unittest.TestCase):
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

    def evidence_files(self, ids):
        files = {f"inputs/evidence/{i:03d}.json": capture_doc(i) for i in ids}
        files["inputs/analysis.json"] = analysis_doc(ids)
        return files

    def wrap(self, stub, c):
        return sbud.BudgetedProvider(stub, c, artifact="A", lane="L", run_scope="S",
                                     manifest_dir=tempfile.mkdtemp())

    # 1
    def test_writer_draft_from_findings(self):
        c = contract("writer")
        s = self.sandbox_with(c, self.evidence_files([1, 2, 3]))
        r = sw.WriterSpecialist().run(c, s, platform_hint="x")
        self.assertEqual(r.result, "COMPLETED")
        self.assertEqual(sc.validate_result(r, c), [])
        doc = json.loads(s.read(sw.WRITER_RESULT_PATH))
        self.assertEqual(doc["schema"], "DraftResult/1")
        self.assertEqual(len(doc["claims"]), 3)
        self.assertTrue(all(cl["evidence_refs"] for cl in doc["claims"]))
        cand = doc["candidate"]
        self.assertEqual(set(cand), set(sw.CANDIDATE_KEYS))   # JSON is written with sorted keys
        self.assertEqual(cand["status"], "DRAFT_UNPUBLISHED")
        self.assertEqual(cand["bot"], "social-a")
        self.assertEqual(cand["persona"], "social-a")
        self.assertIsNone(cand["signal_id"])
        self.assertEqual(cand["source_refs"], ["https://e.org/1", "https://e.org/2", "https://e.org/3"])
        self.assertTrue(cand["content_id"].startswith("sdraft-"))
        self.assertEqual(doc["platform_hint"], "x")
        self.assertEqual(sorted(e["evidence_id"] for e in r.evidence_refs), ["ev-1", "ev-2", "ev-3"])
        self.assertEqual([o["path"] for o in r.outputs], [sw.WRITER_RESULT_PATH])

    # 2
    def test_provider_rewrite_cannot_add_unreferenced_claims(self):
        c = contract("writer", model_call_budget=1)
        s = self.sandbox_with(c, self.evidence_files([1, 2]))
        stub = StubProvider({"hook": "Better hook", "body": "Better body",
                             "claims": [{"text": "grounded rewrite", "evidence_ids": ["ev-1"]},
                                        {"text": "made up", "evidence_ids": ["ev-99"]},
                                        {"text": "no ids"}, "junk"]})
        r = sw.WriterSpecialist().run(c, s, provider=self.wrap(stub, c))
        self.assertEqual(r.result, "COMPLETED")
        self.assertEqual(r.calls_used, 1)
        doc = json.loads(s.read(sw.WRITER_RESULT_PATH))
        self.assertEqual([cl["text"] for cl in doc["claims"]], ["grounded rewrite"])
        self.assertEqual(doc["candidate"]["hook"], "Better hook")
        self.assertEqual(doc["candidate"]["body"], "Better body")
        self.assertTrue(any("stripped" in l and "made up" in l for l in doc["limitations"]))
        self.assertTrue(any("no ids" in l for l in doc["limitations"]))
        self.assertEqual([e["evidence_id"] for e in r.evidence_refs], ["ev-1"])

    # 3
    def test_provider_cannot_change_candidate_status(self):
        c = contract("writer", model_call_budget=1)
        s = self.sandbox_with(c, self.evidence_files([1]))
        stub = StubProvider({"status": "QUEUED", "candidate": {"status": "QUEUED", "publish": True},
                             "claims": [{"text": "ok", "evidence_ids": ["ev-1"]}]})
        r = sw.WriterSpecialist().run(c, s, provider=self.wrap(stub, c))
        doc = json.loads(s.read(sw.WRITER_RESULT_PATH))
        self.assertEqual(doc["candidate"]["status"], "DRAFT_UNPUBLISHED")
        self.assertNotIn("publish", doc["candidate"])
        self.assertTrue(any("status/shape" in l for l in doc["limitations"]))
        self.assertEqual(r.effect_attempts, 0)

    # 4
    def test_media_brief_mirrors_sources_and_flags_missing_alt_text(self):
        c = contract("media")
        s = self.sandbox_with(c, self.evidence_files([1, 2]))
        r = sw.MediaBriefSpecialist().run(c, s)
        self.assertEqual(r.result, "COMPLETED")
        self.assertEqual(sc.validate_result(r, c), [])
        doc = json.loads(s.read(sw.MEDIA_RESULT_PATH))
        brief = doc["brief"]
        self.assertEqual(brief["format"], "short-vertical")
        self.assertEqual(len(brief["shots_or_frames"]), 2)
        self.assertEqual(sorted(x["evidence_id"] for x in brief["sources"]), ["ev-1", "ev-2"])
        self.assertIsNone(brief["alt_text"])
        self.assertTrue(any("alt text missing" in l for l in doc["limitations"]))
        self.assertEqual(brief["status"], "DRAFT_UNPUBLISHED")
        # Provider supplies alt text; an unreferenced extra shot is stripped.
        c2 = contract("media", model_call_budget=1)
        s2 = self.sandbox_with(c2, self.evidence_files([1]))
        stub = StubProvider({"alt_text": "A person reading", "shots": [
            {"beat": "grounded", "evidence_ids": ["ev-1"]}, {"beat": "invented", "evidence_ids": ["ev-9"]}]})
        sw.MediaBriefSpecialist().run(c2, s2, provider=self.wrap(stub, c2), fmt="carousel")
        doc2 = json.loads(s2.read(sw.MEDIA_RESULT_PATH))
        self.assertEqual(doc2["brief"]["alt_text"], "A person reading")
        self.assertEqual([x["beat"] for x in doc2["brief"]["shots_or_frames"]], ["finding 1", "grounded"])
        self.assertEqual(doc2["brief"]["format"], "carousel")
        self.assertFalse(any("alt text missing" in l for l in doc2["limitations"]))

    # 5
    def test_writes_stay_inside_result_file(self):
        before = tree(self.tmp)
        c = contract("writer")
        s = self.sandbox_with(c, self.evidence_files([1]))
        inputs_before = {rel: s.read(rel) for rel in s.list()}
        sw.WriterSpecialist().run(c, s)
        self.assertEqual(tree(self.tmp), before)
        self.assertEqual(s.list(), sorted(list(inputs_before) + [sw.WRITER_RESULT_PATH]))
        for rel, data in inputs_before.items():
            self.assertEqual(s.read(rel), data)
        with self.assertRaises(sa.WriteDenied):
            sa.RestrictedView(s, sw.WRITER_RESULT_PATH).write("inputs/analysis.json", {"x": 1})
        self.assertFalse((Path(self.tmp) / "content").exists())

    # 6
    def test_role_mismatch_for_both(self):
        for adapter, wrong in ((sw.WriterSpecialist(), "media"), (sw.MediaBriefSpecialist(), "writer")):
            c = contract(wrong)
            s = self.sandbox_with(c, {})
            with self.assertRaises(sw.RoleMismatch):
                adapter.run(c, s)
            self.assertEqual(s.list(), [])

    # 7
    def test_no_findings_yields_empty_candidate(self):
        c = contract("writer")
        s = self.sandbox_with(c, {"inputs/evidence/000.json": capture_doc(1)})   # evidence, no findings
        r = sw.WriterSpecialist().run(c, s)
        self.assertEqual(r.result, "COMPLETED")
        self.assertIn("no supported claims", r.limitations)
        doc = json.loads(s.read(sw.WRITER_RESULT_PATH))
        self.assertEqual(doc["claims"], [])
        self.assertEqual(doc["candidate"]["body"], "")
        self.assertEqual(doc["candidate"]["source_refs"], [])
        self.assertEqual(doc["candidate"]["status"], "DRAFT_UNPUBLISHED")
        self.assertEqual(r.evidence_refs, [])
        # Findings whose evidence is not in the bundle are not claims either.
        c2 = contract("writer")
        s2 = self.sandbox_with(c2, {"inputs/analysis.json": analysis_doc([5])})
        r2 = sw.WriterSpecialist().run(c2, s2)
        self.assertEqual(json.loads(s2.read(sw.WRITER_RESULT_PATH))["claims"], [])
        self.assertIn("no supported claims", r2.limitations)

    # 8
    def test_cross_persona_context_fails_closed(self):
        c = contract("media", persona="cultural-primandir-atman", bounded_context_refs=[
            {"kind": "decisions", "bot": "social-a", "persona": "social-a"}])
        s = sb.Sandbox(c)
        s.create()
        with self.assertRaises(sb.ContextError):
            s.materialize_context(sb.PersonaSnapshotResolver("social-a", "cultural-primandir-atman"))
        r = sw.MediaBriefSpecialist().run(c, s)
        self.assertEqual(r.result, "FAILED")
        self.assertEqual(r.outputs, [])
        self.assertEqual(sc.validate_result(r, c), [])

    # 9
    def test_deadline_timed_out(self):
        for adapter, role in ((sw.WriterSpecialist(), "writer"), (sw.MediaBriefSpecialist(), "media")):
            c = contract(role)
            s = self.sandbox_with(c, self.evidence_files([1]))
            r = adapter.run(c, s, deadline=sbud.Deadline(budget_s=0, clock=lambda: 0.0))
            self.assertEqual(r.result, "TIMED_OUT")
            self.assertEqual(r.outputs, [])

    # 10
    def test_module_has_no_effect_or_state_surface(self):
        import ast
        tree_ = ast.parse(Path(sw.__file__).read_text(encoding="utf-8"))
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
                                     "pipeline", "decision", "reasoning", "reasoning_cli", "worker",
                                     "state", "leasing", "experiment_engine", "content_intelligence",
                                     "cultural_review", "factcheck", "isolation"}, set())
        self.assertEqual(referenced & {"PersonaState", "RuntimeState", "content_dir", "state_dir",
                                       "memory_dir", "publish", "enqueue", "register_experiment",
                                       "run_cycle", "ideate"}, set())


if __name__ == "__main__":
    unittest.main()
