"""SB-S23-006 — parent result validator / integrator.

Proves ``runtime/specialist_integrator.py``:
- verify() accepts a genuine result and rejects tampered/missing/escaping
  outputs, effect attempts, changed reviewed inputs and non-adoptable states;
- adopt() copies only declared outputs into receipts/<bot>/specialists/, writes
  a sanitized receipt, retires the scratch — all inside the fence; a lost fence
  writes nothing and leaves the scratch for reject();
- reject() leaves only a truthful failure receipt; parent state is untouched;
- integrate_into() returns values (candidate stays DRAFT_UNPUBLISHED) and never
  writes persona/runtime state; persona scope mismatches fail before any write;
- concurrent adoptions for different personas do not cross.

Evidence class: ENGINEERING. No network, no model call, no effect.
"""
import json
import os
import shutil
import sys
import tempfile
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import leasing, paths  # noqa: E402
from runtime import specialist_contract as sc  # noqa: E402
from runtime import specialist_sandbox as sb  # noqa: E402
from runtime import specialist_research as sr  # noqa: E402
from runtime import specialist_analysis as sa  # noqa: E402
from runtime import specialist_writer as sw  # noqa: E402
from runtime import specialist_integrator as si  # noqa: E402
from runtime.jsonstore import append_jsonl, read_jsonl  # noqa: E402

SRC = "https://example.org/a"


def contract(role="researcher", persona="social-a", **kw):
    schema = {"researcher": "ResearchResult/1", "writer": "DraftResult/1",
              "reviewer": "ReviewResult/1"}[role]
    base = dict(bot="social-a", persona=persona, parent_run_id="run-1", role=role, objective="o",
                expected_output_schema=schema, time_budget_s=10)
    if role == "researcher":
        base["input_artifacts"] = [{"kind": "source_candidate", "url": SRC}]
    base.update(kw)
    return sc.new_contract(**base)


def snapshot(root, kinds=("state", "content", "experiments", "memory", "analytics")):
    root = Path(root)
    out = []
    for k in kinds:
        d = root / k
        if not d.exists():
            continue
        for p in d.rglob("*"):
            out.append((p.relative_to(root).as_posix(), p.read_bytes() if p.is_file() else None))
    return sorted(out)


class IntegratorTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp
        # Seed parent stores so "untouched" is a real claim.
        append_jsonl(paths.memory_dir("social-a") / "decisions.jsonl", {"persona": "social-a", "d": 1})
        (paths.state_dir("social-a") / "bot_state.json").write_text('{"x": 1}')
        (paths.content_dir("social-a") / "content_history.jsonl").write_text("")
        (paths.experiments_dir("social-a") / "index.jsonl").write_text("")
        self.before = snapshot(self.tmp)

    def tearDown(self):
        self.assertEqual(snapshot(self.tmp), self.before)        # parent stores never change
        shutil.rmtree(self.tmp, ignore_errors=True)

    # helpers ---------------------------------------------------------------
    def research(self, persona="social-a"):
        c = contract("researcher", persona=persona)
        s = sb.Sandbox(c)
        s.create()
        r = sr.ResearchSpecialist().run(c, s, collector=sr.FixtureCollector({SRC: "alpha"}))
        return c, s, r

    def writer(self):
        c = contract("writer")
        s = sb.Sandbox(c)
        s.create()
        ref = {"evidence_id": "ev-1", "url": SRC, "content_hash": "d" * 64, "status": "ok",
               "provenance": "fixture", "source_id": "src-1", "captured_at": "2026-09-21T21:00:00+00:00",
               "collector_version": "1.0.0"}
        s.write("inputs/evidence/000.json", {"schema": "EvidenceCapture/1", "evidence_ref": ref,
                                             "receipt": {"status": "ok", "receipt_id": "cap-1"}})
        s.write("inputs/analysis.json", {"schema": "AnalysisResult/1",
                                         "findings": [{"statement": "f", "evidence_refs": [ref]}]})
        r = sw.WriterSpecialist().run(c, s)
        return c, s, r

    def receipts_for(self, wid):
        idx = paths.receipts_dir("social-a") / "index.jsonl"
        return [row for row in read_jsonl(idx) if row["task_id"] == f"specialist:{wid}"]

    # 1
    def test_happy_path_adopt(self):
        c, s, r = self.research()
        self.assertEqual(si.verify(r, c, s), [])
        receipt = si.adopt(r, c, s, bot="social-a", persona="social-a")
        self.assertEqual(receipt.decision, "ADOPTED")
        kept = Path(self.tmp) / "receipts" / "social-a" / "specialists" / c.worker_id
        self.assertTrue((kept / "outputs" / "research_result.json").is_file())
        self.assertTrue((kept / "evidence" / "000.json").is_file())
        self.assertTrue((kept / "INDEX.json").is_file())
        self.assertFalse((Path(self.tmp) / "scratch" / "social-a" / c.worker_id).exists())
        self.assertEqual(s.status, "RETIRED")
        rows = self.receipts_for(c.worker_id)
        self.assertEqual([row["kind"] for row in rows], ["finish"])
        doc = json.loads(Path(receipt.receipt_path).read_bytes())
        self.assertEqual(doc["detail"]["specialist"]["decision"], "ADOPTED")
        self.assertEqual(doc["detail"]["specialist"]["effect_attempts"], 0)
        self.assertEqual([o["path"] for o in receipt.outputs],
                         ["evidence/000.json", "outputs/research_result.json"])
        self.assertEqual(len(receipt.evidence_refs), 1)
        integrated = si.integrate_into("ResearchResult/1", receipt)
        self.assertEqual([e["url"] for e in integrated["evidence_refs"]], [SRC])
        self.assertEqual(si.integrate_into("EvidenceCapture/1", receipt)["schema"], "EvidenceCapture/1")

    # 2
    def test_tampered_output_is_refused_and_nothing_written(self):
        c, s, r = self.research()
        s.write("outputs/research_result.json", {"schema": "ResearchResult/1", "swapped": True})
        errs = si.verify(r, c, s)
        self.assertTrue(any("sha256 changed" in e for e in errs), errs)
        receipts_before = sorted(p.name for p in (Path(self.tmp) / "receipts").rglob("*")) \
            if (Path(self.tmp) / "receipts").exists() else []
        with self.assertRaises(si.IntegrationError):
            si.adopt(r, c, s, bot="social-a", persona="social-a")
        receipts_after = sorted(p.name for p in (Path(self.tmp) / "receipts").rglob("*")) \
            if (Path(self.tmp) / "receipts").exists() else []
        self.assertEqual(receipts_before, receipts_after)
        self.assertEqual(s.status, "PENDING")                         # scratch untouched, reject-able
        # A declared output whose in-file schema differs is refused too.
        c2, s2, r2 = self.research()
        s2.write("outputs/research_result.json", {"schema": "DraftResult/1"})
        r2b = sc.WorkerResult(**dict(r2.as_dict(), outputs=[
            {"schema": "ResearchResult/1", "path": "outputs/research_result.json",
             "sha256": s2.sha256("outputs/research_result.json")}]))
        self.assertTrue(any("declares schema" in e for e in si.verify(r2b, c2, s2)))

    # 3
    def test_escaping_or_missing_output_is_refused(self):
        c, s, r = self.research()
        bad = sc.WorkerResult(**dict(r.as_dict(), outputs=[
            {"schema": "ResearchResult/1", "path": "../escape.json", "sha256": "a" * 64}]))
        self.assertTrue(any("path" in e for e in si.verify(bad, c, s)))
        missing = sc.WorkerResult(**dict(r.as_dict(), outputs=[
            {"schema": "ResearchResult/1", "path": "outputs/nope.json", "sha256": "a" * 64}]))
        self.assertTrue(any("missing" in e for e in si.verify(missing, c, s)))
        # Non-adoptable states are refused even when outputs are fine.
        timed = sc.WorkerResult(**dict(r.as_dict(), result="TIMED_OUT"))
        self.assertTrue(any("not adoptable" in e for e in si.verify(timed, c, s)))

    # 4
    def test_effect_attempt_is_rejected_with_failure_receipt(self):
        c, s, r = self.research()
        bad = sc.WorkerResult(**dict(r.as_dict(), effect_attempts=1))
        errs = si.verify(bad, c, s)
        self.assertTrue(any("effect" in e for e in errs))
        rej = si.reject(bad, c, s, errs)
        self.assertEqual(rej.decision, "REJECTED")
        self.assertEqual(rej.cleanup_status, "RETIRED")
        self.assertFalse((Path(self.tmp) / "scratch" / "social-a" / c.worker_id).exists())
        self.assertFalse((Path(self.tmp) / "receipts" / "social-a" / "specialists" / c.worker_id).exists())
        rows = self.receipts_for(c.worker_id)
        self.assertEqual([row["kind"] for row in rows], ["failure"])
        doc = json.loads(Path(rej.receipt_path).read_bytes())
        self.assertEqual(doc["detail"]["specialist"]["decision"], "REJECTED")
        self.assertTrue(any("effect" in x for x in doc["detail"]["specialist"]["reasons"]))

    # 5
    def test_reviewed_input_changed_after_review_is_refused(self):
        c = contract("reviewer")
        s = sb.Sandbox(c)
        s.create()
        s.write("inputs/analysis.json", {"schema": "AnalysisResult/1", "findings": []})
        r = sa.ReviewerSpecialist().run(c, s)
        self.assertEqual(si.verify(r, c, s), [])
        s.write("inputs/analysis.json", {"schema": "AnalysisResult/1", "findings": [], "edited": True})
        errs = si.verify(r, c, s)
        self.assertTrue(any("changed after review" in e for e in errs), errs)

    # 6
    def test_lost_fence_writes_nothing(self):
        c, s, r = self.research()
        a = leasing.acquire(f"specialist:{c.worker_id}", "A", ttl_seconds=0)
        fa = leasing.Fence(a)
        leasing.acquire(f"specialist:{c.worker_id}", "B", ttl_seconds=300)
        with self.assertRaises(leasing.FenceLost):
            si.adopt(r, c, s, bot="social-a", persona="social-a", fence=fa)
        self.assertTrue((Path(self.tmp) / "scratch" / "social-a" / c.worker_id).exists())
        self.assertEqual(s.status, "PENDING")
        self.assertFalse((Path(self.tmp) / "receipts" / "social-a" / "specialists").exists())
        self.assertEqual(self.receipts_for(c.worker_id), [])
        # A live fence adopts normally.
        b = leasing.Lease(**leasing.inspect(f"specialist:{c.worker_id}"))
        receipt = si.adopt(r, c, s, bot="social-a", persona="social-a", fence=leasing.Fence(b))
        self.assertEqual(receipt.decision, "ADOPTED")
        leasing.release(b)

    # 7
    def test_integrate_draft_preserves_status_and_rejects_queued(self):
        c, s, r = self.writer()
        self.assertEqual(si.verify(r, c, s), [])
        receipt = si.adopt(r, c, s, bot="social-a", persona="social-a")
        got = si.integrate_into("DraftResult/1", receipt)
        self.assertEqual(got["candidate"]["status"], "DRAFT_UNPUBLISHED")
        self.assertEqual(len(got["claims"]), 1)
        with self.assertRaises(si.IntegrationError):
            si.integrate_into("ResearchResult/1", receipt)          # not among this worker's outputs
        with self.assertRaises(si.IntegrationError):
            si.integrate_into("Unknown/9", receipt)
        # A kept draft that somehow carries a queued status is refused at integration.
        kept = Path(receipt.outputs[0]["kept_path"])
        doc = json.loads(kept.read_bytes())
        doc["candidate"]["status"] = "QUEUED"
        kept.write_text(json.dumps(doc))
        with self.assertRaises(si.IntegrationError):
            si.integrate_into("DraftResult/1", receipt)
        # verify() also refuses a draft result whose candidate is not unpublished.
        c2, s2, r2 = self.writer()
        d2 = json.loads(s2.read(sw.WRITER_RESULT_PATH))
        d2["candidate"]["status"] = "QUEUED"
        s2.write(sw.WRITER_RESULT_PATH, d2)
        r2b = sc.WorkerResult(**dict(r2.as_dict(), outputs=[
            {"schema": "DraftResult/1", "path": sw.WRITER_RESULT_PATH, "sha256": s2.sha256(sw.WRITER_RESULT_PATH)}]))
        self.assertTrue(any("DRAFT_UNPUBLISHED" in e for e in si.verify(r2b, c2, s2)))

    # 8
    def test_persona_scope_mismatch_before_any_write(self):
        c, s, r = self.research()
        with self.assertRaises(si.IntegrationError):
            si.adopt(r, c, s, bot="social-a", persona="cultural-primandir-atman")
        with self.assertRaises(si.IntegrationError):
            si.adopt(r, c, s, bot="social-b", persona="social-a")
        self.assertEqual(s.status, "PENDING")
        self.assertFalse((Path(self.tmp) / "receipts").exists())
        other = sb.Sandbox(contract("researcher"))
        other.create()
        self.assertTrue(si.verify(r, c, other))                       # sandbox of another worker
        with self.assertRaises(si.IntegrationError):
            si.reject(r, c, other, ["x"])

    # 9
    def test_reject_then_adopt_is_refused(self):
        c, s, r = self.research()
        si.reject(r, c, s, ["parent changed its mind"])
        with self.assertRaises(si.IntegrationError):
            si.adopt(r, c, s, bot="social-a", persona="social-a")
        rows = self.receipts_for(c.worker_id)
        self.assertEqual([row["kind"] for row in rows], ["failure"])
        # And adopting twice is refused (scratch is gone after the first adoption).
        c2, s2, r2 = self.research()
        si.adopt(r2, c2, s2, bot="social-a", persona="social-a")
        with self.assertRaises(si.IntegrationError):
            si.adopt(r2, c2, s2, bot="social-a", persona="social-a")
        self.assertEqual(len(self.receipts_for(c2.worker_id)), 1)

    # 10 (parent-state identity is asserted in tearDown for every test)
    def test_parent_state_identity_helper_is_live(self):
        self.assertEqual(snapshot(self.tmp), self.before)
        c, s, r = self.research()
        si.adopt(r, c, s, bot="social-a", persona="social-a")
        self.assertEqual(snapshot(self.tmp), self.before)

    # 11
    def test_concurrent_adoptions_for_different_personas(self):
        results = {}
        errors = []

        def work(persona):
            try:
                c, s, r = self.research(persona=persona)
                results[persona] = si.adopt(r, c, s, bot="social-a", persona=persona)
            except Exception as exc:                                  # noqa: BLE001
                errors.append(exc)
        threads = [threading.Thread(target=work, args=(p,))
                   for p in ("social-a", "cultural-primandir-atman")]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(errors, [])
        self.assertEqual(set(results), {"social-a", "cultural-primandir-atman"})
        for persona, rec in results.items():
            self.assertEqual(rec.persona, persona)
            kept = Path(rec.outputs[0]["kept_path"]).parent.parent
            self.assertEqual(kept.name, rec.worker_id)
            self.assertEqual(json.loads((kept / "INDEX.json").read_bytes())["persona"], persona)
        self.assertNotEqual(results["social-a"].worker_id, results["cultural-primandir-atman"].worker_id)
        self.assertFalse((Path(self.tmp) / "scratch" / "social-a").exists()
                         and any((Path(self.tmp) / "scratch" / "social-a").iterdir()))


if __name__ == "__main__":
    unittest.main()
