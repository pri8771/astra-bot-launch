"""SB-S23-008 — specialist lifecycle acceptance (ENGINEERING, fixtures only).

Proves ``runtime/specialist_lifecycle.py`` and ``bin/prove_v23_specialists.py``:
- concurrent researcher/analyst/writer lifecycles all ADOPT, with receipts,
  empty scratch and no leases;
- a raising adapter, an escaping result, an effect attempt, a child-spawn
  attempt, a cross-sandbox read and a timeout each REJECT with a failure
  receipt while other workers and parent state are unaffected;
- a retired worker id cannot start a second lifecycle; leases are gone after
  every record; the bundle's manifest hashes verify and it is fixture-only;
- max_workers bounds real concurrency.

No network, no model call, no effect. Nothing here is LIVE evidence.
"""
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import leasing, paths  # noqa: E402
from runtime import specialist_contract as sc  # noqa: E402
from runtime import specialist_budget as sbud  # noqa: E402
from runtime import specialist_sandbox as sb  # noqa: E402
from runtime import specialist_research as sr  # noqa: E402
from runtime import specialist_analysis as sa  # noqa: E402
from runtime import specialist_writer as sw  # noqa: E402
from runtime import specialist_lifecycle as sl  # noqa: E402
from runtime.jsonstore import append_jsonl, read_jsonl, now_iso  # noqa: E402

SRC = "https://fixture.invalid/a"
EV = {"evidence_id": "ev-1", "source_id": "src-1", "url": SRC, "captured_at": "2026-09-21T21:00:00+00:00",
      "content_hash": "e" * 64, "provenance": "fixture", "collector_version": "1.0.0", "status": "ok"}
CAPTURE = {"schema": "EvidenceCapture/1", "index": 0, "evidence_ref": EV,
           "receipt": {"status": "ok", "receipt_id": "cap-1"}}
ANALYSIS = {"schema": "AnalysisResult/1", "findings": [{"statement": "f", "evidence_refs": [EV]}]}


def _load_runner():
    p = Path(__file__).resolve().parent.parent / "bin" / "prove_v23_specialists.py"
    spec = importlib.util.spec_from_file_location("prove_v23_specialists", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def contract(role="researcher", persona="social-a", **kw):
    schema = {"researcher": "ResearchResult/1", "analyst": "AnalysisResult/1",
              "writer": "DraftResult/1", "reviewer": "ReviewResult/1"}[role]
    base = dict(bot="social-a", persona=persona, parent_run_id="run-1", role=role, objective="o",
                expected_output_schema=schema, time_budget_s=10)
    if role == "researcher":
        base["input_artifacts"] = [{"kind": "source_candidate", "url": SRC}]
    base.update(kw)
    return sc.new_contract(**base)


def ok_result(contract, sandbox, ledger, started):
    sandbox.write("outputs/x.json", {"schema": "AnalysisResult/1", "findings": []})
    return sc.WorkerResult(
        worker_id=contract.worker_id, parent_run_id=contract.parent_run_id, bot=contract.bot,
        persona=contract.persona, role=contract.role, started_at=started, finished_at=now_iso(),
        source_ref="test", result="COMPLETED",
        outputs=[{"schema": "AnalysisResult/1", "path": "outputs/x.json",
                  "sha256": sandbox.sha256("outputs/x.json")}],
        calls_used=ledger.calls_used, effect_attempts=ledger.effect_attempts)


class RaisingAdapter:
    role = "analyst"

    def run(self, contract, sandbox, *, provider=None, deadline=None, ledger=None, **kw):
        raise RuntimeError("adapter blew up")


class EscapingResultAdapter:
    role = "analyst"

    def run(self, contract, sandbox, *, provider=None, deadline=None, ledger=None, **kw):
        r = ok_result(contract, sandbox, ledger, now_iso())
        return sc.WorkerResult(**dict(r.as_dict(), outputs=[
            {"schema": "AnalysisResult/1", "path": "../escape.json", "sha256": "a" * 64}]))


class EffectAdapter:
    role = "analyst"

    def run(self, contract, sandbox, *, provider=None, deadline=None, ledger=None, **kw):
        sbud.EffectGuard.attempt(contract, "publish", ledger=ledger)


class SpawnAdapter:
    role = "analyst"

    def run(self, contract, sandbox, *, provider=None, deadline=None, ledger=None, **kw):
        sbud.SpawnGuard.assert_no_child(contract, "spawn_specialist")


class PeekAdapter:
    role = "analyst"

    def __init__(self, other_worker_id):
        self.other = other_worker_id

    def run(self, contract, sandbox, *, provider=None, deadline=None, ledger=None, **kw):
        sandbox.read(f"../{self.other}/context/000-deadbeef.json")     # SandboxEscape


class TimingOutAdapter:
    role = "analyst"

    def run(self, contract, sandbox, *, provider=None, deadline=None, ledger=None, **kw):
        started = now_iso()
        try:
            deadline.check()
        except sbud.DeadlineExceeded as exc:
            r = ok_result(contract, sandbox, ledger, started)
            return sc.WorkerResult(**dict(r.as_dict(), result="TIMED_OUT", error=str(exc)))
        return ok_result(contract, sandbox, ledger, started)


class CountingAdapter:
    role = "analyst"
    lock = threading.Lock()
    active = 0
    max_active = 0

    def run(self, contract, sandbox, *, provider=None, deadline=None, ledger=None, **kw):
        with CountingAdapter.lock:
            CountingAdapter.active += 1
            CountingAdapter.max_active = max(CountingAdapter.max_active, CountingAdapter.active)
        try:
            time.sleep(0.05)
            return ok_result(contract, sandbox, ledger, now_iso())
        finally:
            with CountingAdapter.lock:
                CountingAdapter.active -= 1


class SpecialistLifecycleAcceptanceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp
        append_jsonl(paths.memory_dir("social-a") / "decisions.jsonl", {"persona": "social-a", "d": 1})
        (paths.state_dir("social-a") / "bot_state.json").write_text('{"x": 1}')
        self.before = self.parent_snapshot()

    def tearDown(self):
        self.assertEqual(self.parent_snapshot(), self.before)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def parent_snapshot(self):
        out = []
        for k in ("state", "content", "experiments", "memory", "analytics"):
            d = Path(self.tmp) / k
            if d.exists():
                out += [(p.relative_to(self.tmp).as_posix(), p.read_bytes() if p.is_file() else None)
                        for p in d.rglob("*")]
        return sorted(out)

    def scratch_files(self):
        d = Path(self.tmp) / "scratch"
        return sorted(p.as_posix() for p in d.rglob("*") if p.is_file()) if d.exists() else []

    def receipt_kinds(self, wid):
        idx = paths.receipts_dir("social-a") / "index.jsonl"
        return [r["kind"] for r in read_jsonl(idx) if r["task_id"] == f"specialist:{wid}"]

    def assert_clean(self, rec):
        self.assertTrue(rec.lease_gone, rec.stages)
        self.assertIsNone(leasing.inspect(f"specialist:{rec.worker_id}"))
        self.assertEqual(rec.cleanup_status, "RETIRED", rec.stages)
        self.assertFalse((Path(self.tmp) / "scratch" / "social-a" / rec.worker_id).exists())

    # 1
    def test_three_concurrent_workers_adopt(self):
        jobs = [
            {"contract": contract("researcher"), "adapter": sr.ResearchSpecialist(),
             "adapter_kwargs": {"collector": sr.FixtureCollector({SRC: "alpha"})}},
            {"contract": contract("analyst"), "adapter": sa.AnalystSpecialist(),
             "inputs": {"evidence/000.json": CAPTURE, "research_result.json":
                        {"schema": "ResearchResult/1", "evidence_refs": [EV]}}},
            {"contract": contract("writer", persona="cultural-primandir-atman"),
             "adapter": sw.WriterSpecialist(),
             "inputs": {"evidence/000.json": CAPTURE, "analysis.json": ANALYSIS}},
        ]
        recs = sl.run_concurrent(jobs, max_workers=3)
        self.assertEqual([r.decision for r in recs], ["ADOPTED"] * 3)
        for r in recs:
            self.assert_clean(r)
            self.assertEqual(self.receipt_kinds(r.worker_id), ["finish"])
            self.assertTrue(Path(r.receipt_ref).is_file())
            self.assertEqual([s["stage"] for s in r.stages],
                             ["CREATE", "ASSIGN", "RUN", "RETURN", "VERIFY", "ADOPT", "RETIRE"])
            self.assertTrue(all(s["ok"] for s in r.stages), r.stages)
            kept = Path(self.tmp) / "receipts" / "social-a" / "specialists" / r.worker_id
            self.assertTrue((kept / "INDEX.json").is_file())
        self.assertEqual(self.scratch_files(), [])
        self.assertEqual(recs[2].persona, "cultural-primandir-atman")
        draft = json.loads((Path(self.tmp) / "receipts" / "social-a" / "specialists" /
                            recs[2].worker_id / sw.WRITER_RESULT_PATH).read_bytes())
        self.assertEqual(draft["candidate"]["status"], "DRAFT_UNPUBLISHED")

    # 2
    def test_raising_adapter_rejects_only_itself(self):
        jobs = [
            {"contract": contract("researcher"), "adapter": sr.ResearchSpecialist(),
             "adapter_kwargs": {"collector": sr.FixtureCollector({SRC: "alpha"})}},
            {"contract": contract("analyst"), "adapter": RaisingAdapter()},
            {"contract": contract("writer"), "adapter": sw.WriterSpecialist(),
             "inputs": {"evidence/000.json": CAPTURE, "analysis.json": ANALYSIS}},
        ]
        recs = sl.run_concurrent(jobs, max_workers=3)
        self.assertEqual([r.decision for r in recs], ["ADOPTED", "REJECTED", "ADOPTED"])
        bad = recs[1]
        self.assert_clean(bad)
        self.assertEqual(self.receipt_kinds(bad.worker_id), ["failure"])
        self.assertIn("RuntimeError: adapter blew up", bad.result["error"])
        self.assertEqual(bad.result["result"], "FAILED")
        run_stage = next(s for s in bad.stages if s["stage"] == "RUN")
        self.assertFalse(run_stage["ok"])
        self.assertIn("adapter blew up", run_stage["detail"])
        receipt = json.loads(Path(bad.receipt_ref).read_bytes())
        self.assertIn("adapter blew up", receipt["detail"]["specialist"]["error"])

    # 3
    def test_escaping_result_is_rejected_at_verify(self):
        rec = sl.run_specialist(contract("analyst"), EscapingResultAdapter())
        self.assertEqual(rec.decision, "REJECTED")
        self.assertTrue(any("path" in e for e in rec.verify_errors), rec.verify_errors)
        self.assertEqual(self.receipt_kinds(rec.worker_id), ["failure"])
        self.assert_clean(rec)

    # 4
    def test_effect_attempt_is_rejected(self):
        rec = sl.run_specialist(contract("analyst"), EffectAdapter())
        self.assertEqual(rec.decision, "REJECTED")
        self.assertEqual(rec.result["effect_attempts"], 1)
        self.assertTrue(any("effect" in e for e in rec.verify_errors), rec.verify_errors)
        self.assertIn("EffectDenied", rec.result["error"])
        receipt = json.loads(Path(rec.receipt_ref).read_bytes())
        self.assertEqual(receipt["detail"]["specialist"]["effect_attempts"], 1)
        self.assert_clean(rec)

    # 5
    def test_child_spawn_attempt_is_rejected(self):
        rec = sl.run_specialist(contract("analyst"), SpawnAdapter())
        self.assertEqual(rec.decision, "REJECTED")
        self.assertIn("ChildSpawnDenied", rec.result["error"])
        self.assert_clean(rec)
        nested = contract("analyst", parent_run_id="w-0123456789ab")
        rec2 = sl.run_specialist(nested, sa.AnalystSpecialist())
        self.assertEqual(rec2.decision, "REJECTED")
        self.assertEqual(rec2.stages[0]["stage"], "CREATE")
        self.assertFalse(rec2.stages[0]["ok"])
        self.assertIn("ChildSpawnDenied", rec2.stages[0]["detail"])
        self.assertFalse((Path(self.tmp) / "scratch" / "social-a" / nested.worker_id).exists())

    # 6
    def test_persona_isolation_under_concurrency(self):
        ca = contract("researcher", persona="social-a", bounded_context_refs=[{"kind": "evidence", "id": "ctx"}])
        cb = contract("analyst", persona="cultural-primandir-atman")
        jobs = [
            {"contract": ca, "adapter": sr.ResearchSpecialist(),
             "resolver": sb.DictContextResolver({"ctx": {"private": "A"}}),
             "adapter_kwargs": {"collector": sr.FixtureCollector({SRC: "alpha"})}},
            {"contract": cb, "adapter": PeekAdapter(ca.worker_id)},
        ]
        recs = sl.run_concurrent(jobs, max_workers=2)
        self.assertEqual(recs[0].decision, "ADOPTED")
        self.assertEqual(recs[1].decision, "REJECTED")
        self.assertIn("SandboxEscape", recs[1].result["error"])
        kept = Path(self.tmp) / "receipts" / "social-a" / "specialists" / ca.worker_id
        self.assertTrue((kept / "outputs" / "research_result.json").is_file())
        for r in recs:
            self.assert_clean(r)

    # 7
    def test_timeout_is_rejected_with_cleanup(self):
        rec = sl.run_specialist(contract("analyst"), TimingOutAdapter(),
                                deadline=sbud.Deadline(budget_s=0, clock=lambda: 0.0))
        self.assertEqual(rec.decision, "REJECTED")
        self.assertEqual(rec.result["result"], "TIMED_OUT")
        self.assertTrue(any("not adoptable" in e for e in rec.verify_errors))
        self.assert_clean(rec)

    # 8
    def test_worker_id_is_never_reused(self):
        c = contract("analyst")
        first = sl.run_specialist(c, CountingAdapter())
        self.assertEqual(first.decision, "ADOPTED")
        second = sl.run_specialist(c, CountingAdapter())
        self.assertEqual(second.decision, "REJECTED")
        self.assertEqual(second.stages, second.stages[:1])            # CREATE only
        self.assertFalse(second.stages[0]["ok"])
        self.assertIn("WorkerIdReused", second.stages[0]["detail"])
        self.assertIsNone(second.receipt_ref)
        self.assertEqual(self.receipt_kinds(c.worker_id), ["finish"])  # still exactly one
        # A rejected worker id is not reusable either.
        c2 = contract("analyst")
        sl.run_specialist(c2, RaisingAdapter())
        again = sl.run_specialist(c2, CountingAdapter())
        self.assertIn("WorkerIdReused", again.stages[0]["detail"])
        # A held lease also blocks CREATE, without creating scratch.
        c3 = contract("analyst")
        held = leasing.acquire(f"specialist:{c3.worker_id}", "someone-else", ttl_seconds=300)
        blocked = sl.run_specialist(c3, CountingAdapter())
        self.assertIn("LeaseHeld", blocked.stages[0]["detail"])
        self.assertFalse((Path(self.tmp) / "scratch" / "social-a" / c3.worker_id).exists())
        leasing.release(held)

    # 9
    def test_lease_is_gone_after_every_record(self):
        recs = [sl.run_specialist(contract("analyst"), CountingAdapter()),
                sl.run_specialist(contract("analyst"), RaisingAdapter()),
                sl.run_specialist(contract("analyst"), EscapingResultAdapter())]
        for r in recs:
            self.assertTrue(r.lease_released)
            self.assertTrue(r.lease_gone)
            self.assertIsNone(leasing.inspect(f"specialist:{r.worker_id}"))
        self.assertEqual(sorted(p.name for p in (Path(self.tmp) / "leases").glob("*.lease.json")), [])
        # A lost parent fence during ADOPT still ends clean: REJECTED, scratch retired, lease gone.
        c = contract("analyst")
        a = leasing.acquire("cycle:social-a", "A", ttl_seconds=0)
        fa = leasing.Fence(a)
        leasing.acquire("cycle:social-a", "B", ttl_seconds=300)
        rec = sl.run_specialist(c, CountingAdapter(), fence=fa)
        self.assertEqual(rec.decision, "REJECTED")
        self.assertTrue(any(s["stage"] == "ADOPT" and not s["ok"] and "FenceLost" in s["detail"]
                            for s in rec.stages), rec.stages)
        self.assert_clean(rec)
        self.assertFalse((Path(self.tmp) / "receipts" / "social-a" / "specialists" / c.worker_id).exists())

    # 10
    def test_bundle_manifest_verifies_and_is_fixture_only(self):
        runner = _load_runner()
        out = Path(tempfile.mkdtemp()) / "bundle"
        try:
            manifest = runner.build_bundle(out, bot="social-a",
                                           personas=["social-a", "cultural-primandir-atman"],
                                           source_sha="test-sha", command="unit-test")
            self.assertNotIn("refused", manifest)
            self.assertEqual(manifest["classification"], "fixture")
            self.assertFalse(manifest["live"])
            self.assertTrue(manifest["parent_state_unchanged"])
            self.assertEqual(sorted(d["role"] for d in manifest["decisions"].values()),
                             ["analyst", "researcher", "reviewer", "writer"])
            self.assertTrue(all(d["decision"] == "ADOPTED" for d in manifest["decisions"].values()),
                            manifest["decisions"])
            self.assertEqual(runner.verify_bundle(out), [])
            self.assertEqual(json.loads((out / "leases_after.json").read_bytes()), [])
            self.assertEqual(json.loads((out / "scratch_after.json").read_bytes()), [])
            # Tampering with a bundle file is detected.
            victim = next(out.glob("lifecycle-*.json"))
            victim.write_text(victim.read_text() + "\n")
            self.assertTrue(any("hash mismatch" in e for e in runner.verify_bundle(out)))
            # The runner restored SBOTS_HOME to this test's home.
            self.assertEqual(os.environ["SBOTS_HOME"], self.tmp)
        finally:
            shutil.rmtree(out.parent, ignore_errors=True)

    # 11
    def test_max_workers_bounds_concurrency(self):
        CountingAdapter.active = 0
        CountingAdapter.max_active = 0
        jobs = [{"contract": contract("analyst"), "adapter": CountingAdapter()} for _ in range(5)]
        recs = sl.run_concurrent(jobs, max_workers=3)
        self.assertEqual([r.decision for r in recs], ["ADOPTED"] * 5)
        self.assertLessEqual(CountingAdapter.max_active, 3)
        self.assertGreaterEqual(CountingAdapter.max_active, 2)          # it really ran concurrently
        for r in recs:
            self.assert_clean(r)
        # max_workers above the default cap is clamped to the cap.
        CountingAdapter.max_active = 0
        recs = sl.run_concurrent([{"contract": contract("analyst"), "adapter": CountingAdapter()}
                                  for _ in range(5)], max_workers=50)
        self.assertLessEqual(CountingAdapter.max_active, sl.DEFAULT_MAX_WORKERS)


if __name__ == "__main__":
    unittest.main()
