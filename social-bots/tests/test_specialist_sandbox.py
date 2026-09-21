"""SB-S23-002 — specialist scratch-state sandbox.

Proves ``runtime/specialist_sandbox.py``:
- a worker can only read/write inside its own 0o700 scratch directory;
- absolute paths, '..', symlinked components and out-of-root resolution are
  refused BEFORE any filesystem write (whole-``SBOTS_HOME`` snapshots compared);
- context is materialized as files (copies), never live objects; the persona
  snapshot resolver refuses any other persona/bot;
- retire keeps only validated outputs under receipts/, deletes the rest, is
  idempotent, and fails closed on an escaping keep entry;
- persistent persona/runtime stores are never touched.

Evidence class: ENGINEERING. No model call, no effect, no network.
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
from runtime import paths  # noqa: E402
from runtime.jsonstore import append_jsonl  # noqa: E402


def contract(persona="social-a", refs=(), **kw):
    base = dict(bot="social-a", persona=persona, parent_run_id="run-1", role="researcher",
                objective="o", expected_output_schema="ResearchResult/1", time_budget_s=10,
                bounded_context_refs=list(refs))
    base.update(kw)
    return sc.new_contract(**base)


def tree(root):
    root = Path(root)
    out = []
    for p in root.rglob("*"):
        rel = p.relative_to(root).as_posix()
        if p.is_symlink():
            out.append(("L", rel))
        elif p.is_file():
            out.append(("F", rel, p.read_bytes()))
        else:
            out.append(("D", rel))
    return sorted(out, key=lambda t: t[1])


class SandboxTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp
        self.outside = tempfile.mkdtemp()
        Path(self.outside, "secret.txt").write_bytes(b"outside")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)
        shutil.rmtree(self.outside, ignore_errors=True)

    def parent_stores(self):
        return {k: tree(Path(self.tmp) / k) if (Path(self.tmp) / k).exists() else None
                for k in ("state", "content", "experiments", "memory", "analytics")}

    # 1
    def test_create_write_read_list_and_mode(self):
        c = contract()
        s = sb.Sandbox(c)
        root = s.create()
        self.assertEqual(root, Path(self.tmp) / "scratch" / "social-a" / c.worker_id)
        self.assertEqual(s.mode(), 0o700)
        p = s.write("outputs/result.json", {"schema": "ResearchResult/1", "x": 1})
        self.assertEqual(p, root / "outputs" / "result.json")
        self.assertEqual(json.loads(s.read("outputs/result.json")), {"schema": "ResearchResult/1", "x": 1})
        s.write("outputs/raw.bin", b"\x00\x01")
        self.assertEqual(s.read("outputs/raw.bin"), b"\x00\x01")
        self.assertEqual(s.list(), ["outputs/raw.bin", "outputs/result.json"])
        self.assertEqual(len(s.sha256("outputs/raw.bin")), 64)
        with self.assertRaises(sb.SandboxError):
            s.write("outputs/x", 42)                     # unsupported type

    # 2
    def test_escapes_are_refused_before_any_write(self):
        s = sb.Sandbox(contract())
        s.create()
        before = tree(self.tmp)
        for bad in ("../x", "/etc/x", "a/../../x", "outputs/./x", "", " x", "a\\b",
                    "C:x", "outputs//x", ".", "..", f"../{'z' * 3}/y"):
            with self.assertRaises(sb.SandboxEscape, msg=bad):
                s.write(bad, b"x")
            with self.assertRaises(sb.SandboxEscape, msg=bad):
                s.read(bad)
        self.assertEqual(tree(self.tmp), before)
        self.assertFalse(Path("/etc/x").exists())

    # 3
    def test_symlinks_inside_scratch_are_refused(self):
        s = sb.Sandbox(contract())
        root = s.create()
        os.symlink(self.outside, root / "link")                       # dir link out
        os.symlink(Path(self.outside, "secret.txt"), root / "outputs" / "evil")  # file link out
        before_outside = tree(self.outside)
        for bad in ("link/file", "link", "outputs/evil", "outputs/evil/x"):
            with self.assertRaises(sb.SandboxEscape, msg=bad):
                s.write(bad, b"pwned")
            with self.assertRaises(sb.SandboxEscape, msg=bad):
                s.read(bad)
        self.assertEqual(tree(self.outside), before_outside)
        self.assertEqual(s.list(), [])                                 # links are not listed
        # retire never follows the links out
        self.assertEqual(s.retire(keep=[]), "RETIRED")
        self.assertEqual(tree(self.outside), before_outside)
        self.assertFalse(root.exists())

    # 4
    def test_materialize_context_writes_copies_not_live_objects(self):
        live = {"ev-1": {"title": "a", "nested": {"n": 1}}, "ev-2": b"raw-bytes"}
        resolver = sb.DictContextResolver(live)
        c = contract(refs=[{"kind": "evidence", "id": "ev-1"}, {"kind": "evidence", "id": "ev-2"}])
        s = sb.Sandbox(c)
        s.create()
        out = s.materialize_context(resolver)
        self.assertEqual([o["index"] for o in out], [0, 1])
        self.assertTrue(out[0]["path"].startswith("context/000-"))
        self.assertTrue(out[0]["path"].endswith(".json"))
        self.assertTrue(out[1]["path"].endswith(".bin"))
        self.assertEqual(json.loads(s.read(out[0]["path"])), live["ev-1"])
        self.assertEqual(s.read(out[1]["path"]), b"raw-bytes")
        self.assertEqual(s.sha256(out[0]["path"]), out[0]["sha256"])
        # Mutating what came back never reaches the resolver's data.
        out[0]["ref"]["id"] = "changed"
        self.assertEqual(c.bounded_context_refs[0]["id"], "ev-1")
        data = json.loads(s.read(out[0]["path"]))
        data["nested"]["n"] = 99
        self.assertEqual(live["ev-1"]["nested"]["n"], 1)
        with self.assertRaises(sb.SandboxError):
            s.materialize_context(resolver)                # once only
        self.assertFalse(s.context_failed())

    def test_materialize_failure_leaves_note_and_raises(self):
        c = contract(refs=[{"kind": "evidence", "id": "ok"}, {"kind": "evidence", "id": "missing"}])
        s = sb.Sandbox(c)
        s.create()
        with self.assertRaises(sb.ContextError):
            s.materialize_context(sb.DictContextResolver({"ok": {"a": 1}}))
        self.assertTrue(s.context_failed())
        note = json.loads(s.read(sb.FAILED_NOTE))
        self.assertEqual(note["index"], 1)
        self.assertIn("KeyError", note["error"])
        self.assertEqual(len(note["materialized_before_failure"]), 1)

    # 5
    def test_persona_snapshot_resolver_is_scoped(self):
        append_jsonl(paths.memory_dir("social-a") / "decisions.jsonl",
                     {"persona": "social-a", "decision_id": "d-a"})
        append_jsonl(paths.memory_dir("social-a") / "decisions.jsonl",
                     {"persona": "cultural-primandir-atman", "decision_id": "d-c"})
        r = sb.PersonaSnapshotResolver("social-a", "social-a")
        snap = r.read({"kind": "decisions", "bot": "social-a", "persona": "social-a"})
        self.assertEqual([x["decision_id"] for x in snap["records"]], ["d-a"])
        self.assertEqual(snap["persona"], "social-a")
        for bad in ({"kind": "decisions", "bot": "social-a", "persona": "cultural-primandir-atman"},
                    {"kind": "decisions", "bot": "social-b", "persona": "social-a"},
                    {"kind": "bot_state", "bot": "social-a", "persona": "social-a"},
                    {"kind": "decisions"}, "decisions"):
            with self.assertRaises(sb.ScopeError, msg=bad):
                r.read(bad)
        # Through the sandbox: a cross-persona ref fails closed with a note.
        c = contract(persona="social-a", refs=[
            {"kind": "decisions", "bot": "social-a", "persona": "cultural-primandir-atman"}])
        s = sb.Sandbox(c)
        s.create()
        with self.assertRaises(sb.ContextError):
            s.materialize_context(r)
        self.assertTrue(s.context_failed())
        # Snapshots are plain data and limited when asked.
        snap2 = r.read({"kind": "decisions", "bot": "social-a", "persona": "social-a", "limit": 0})
        self.assertEqual(snap2["records"], [])
        self.assertNotIn("bot_state", sb.SNAPSHOT_KINDS)

    # 6
    def test_retire_keeps_only_listed_outputs_and_is_idempotent(self):
        c = contract()
        s = sb.Sandbox(c)
        root = s.create()
        s.write("outputs/result.json", {"r": 1})
        s.write("outputs/scratch-notes.txt", b"discard me")
        s.write("inputs/in.json", {"i": 1})
        self.assertEqual(s.retire(keep=["outputs/result.json"]), "RETIRED")
        self.assertFalse(root.exists())
        kept = Path(self.tmp) / "receipts" / "social-a" / "specialists" / c.worker_id
        self.assertEqual(json.loads((kept / "outputs" / "result.json").read_bytes()), {"r": 1})
        self.assertFalse((kept / "outputs" / "scratch-notes.txt").exists())
        index = json.loads((kept / "INDEX.json").read_bytes())
        self.assertEqual(index["worker_id"], c.worker_id)
        self.assertEqual(index["kept"][0]["path"], "outputs/result.json")
        self.assertEqual(len(index["kept"][0]["sha256"]), 64)
        self.assertEqual(s.retire(keep=["outputs/result.json"]), "RETIRED")   # no error
        self.assertIsNotNone(s.retired_at)
        with self.assertRaises(sb.SandboxError):
            s.write("outputs/late.json", {"late": True})
        with self.assertRaises(sb.SandboxError):
            s.read("outputs/result.json")

    # 7
    def test_retire_with_escaping_keep_fails_closed(self):
        c = contract()
        s = sb.Sandbox(c)
        root = s.create()
        s.write("outputs/result.json", {"r": 1})
        before = tree(self.tmp)
        self.assertEqual(s.retire(keep=["../escape", "outputs/result.json"]), "FAILED")
        self.assertEqual(tree(self.tmp), before)                     # nothing copied, nothing deleted
        self.assertFalse((Path(self.tmp) / "receipts").exists())
        self.assertTrue(root.exists())
        self.assertEqual(s.retire(keep=[]), "FAILED")                # recorded status sticks
        # A keep entry that is not a regular file is also refused.
        c2 = contract()
        s2 = sb.Sandbox(c2)
        s2.create()
        self.assertEqual(s2.retire(keep=["outputs"]), "FAILED")
        self.assertEqual(s2.retire(keep=["outputs/nope.json"]), "FAILED")

    # 8
    def test_two_sandboxes_cannot_reach_each_other(self):
        ca, cb = contract(persona="social-a"), contract(persona="cultural-primandir-atman")
        sa, sbx = sb.Sandbox(ca), sb.Sandbox(cb)
        ra, rb = sa.create(), sbx.create()
        sa.write("outputs/a.json", {"a": 1})
        sbx.write("outputs/b.json", {"b": 1})
        for bad in (f"../{ca.worker_id}/outputs/a.json", str(ra / "outputs" / "a.json"),
                    f"../../social-a/{ca.worker_id}/outputs/a.json"):
            with self.assertRaises(sb.SandboxEscape, msg=bad):
                sbx.read(bad)
            with self.assertRaises(sb.SandboxEscape, msg=bad):
                sbx.write(bad, b"x")
        self.assertEqual(json.loads(sa.read("outputs/a.json")), {"a": 1})
        self.assertEqual(sa.list(), ["outputs/a.json"])
        self.assertEqual(sbx.list(), ["outputs/b.json"])
        self.assertNotEqual(ra, rb)

    # 9
    def test_create_twice_or_reuse_is_refused(self):
        c = contract()
        s = sb.Sandbox(c)
        s.create()
        with self.assertRaises(sb.SandboxError):
            s.create()
        with self.assertRaises(sb.SandboxError):
            sb.Sandbox(c).create()                                  # same worker id, new instance
        with self.assertRaises(sb.SandboxError):
            sb.Sandbox(c).write("outputs/x", b"x")                  # not created
        with self.assertRaises(sb.SandboxError):
            sb.Sandbox(c).retire(keep=[])                           # not created

    # 10
    def test_invalid_contract_creates_nothing(self):
        c = contract()
        bad = sc.WorkerContract(**dict({k: v for k, v in c.as_dict().items()
                                        if k not in ("authority", "external_effect_budget")},
                                       authority=c.authority, scratch_scope="other"))
        self.assertTrue(sc.validate_contract(bad))
        with self.assertRaises(sb.SandboxError):
            sb.Sandbox(bad)
        with self.assertRaises(sb.SandboxError):
            sb.Sandbox("not a contract")
        self.assertEqual(tree(self.tmp), [])

    def test_parent_stores_are_never_touched(self):
        # Seed persistent stores, then run a full sandbox lifecycle.
        append_jsonl(paths.memory_dir("social-a") / "decisions.jsonl", {"persona": "social-a", "d": 1})
        (paths.state_dir("social-a") / "bot_state.json").write_text('{"x": 1}')
        (paths.content_dir("social-a") / "content_history.jsonl").write_text("")
        before = self.parent_stores()
        c = contract(refs=[{"kind": "decisions", "bot": "social-a", "persona": "social-a"}])
        s = sb.Sandbox(c)
        s.create()
        s.materialize_context(sb.PersonaSnapshotResolver("social-a", "social-a"))
        s.write("outputs/result.json", {"r": 1})
        self.assertEqual(s.retire(keep=["outputs/result.json"]), "RETIRED")
        self.assertEqual(self.parent_stores(), before)

    def test_module_has_no_state_or_effect_surface(self):
        import ast
        tree_ = ast.parse(Path(sb.__file__).read_text(encoding="utf-8"))
        referenced = set()
        for node in ast.walk(tree_):
            if isinstance(node, ast.Import):
                referenced |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom):
                referenced |= {(node.module or "").split(".")[-1]} | {a.name for a in node.names}
            elif isinstance(node, ast.Name):
                referenced.add(node.id)
            elif isinstance(node, ast.Attribute):
                referenced.add(node.attr)
        forbidden = {"subprocess", "requests", "urllib", "socket", "pipeline", "decision",
                     "reasoning", "reasoning_cli", "worker", "state", "PersonaState",
                     "RuntimeState", "state_dir", "admin_all_records", "admin_publish_queue",
                     "publish", "enqueue", "register_experiment", "content_dir", "leasing"}
        self.assertEqual(referenced & forbidden, set())


if __name__ == "__main__":
    unittest.main()
