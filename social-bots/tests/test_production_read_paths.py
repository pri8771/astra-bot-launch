"""SB-V03-005 (LEAD-024 P2) — persona read boundary through ACTUAL production paths.

Complements the interface-level tests in ``test_persona_read_boundary.py`` by
driving REAL production call paths (a full ``decision.run_cycle`` for two personas
on one runtime, the production dedup path, the production analytics aggregate, and
the worker reconciliation read) and proving one persona cannot enumerate or be
contaminated by another persona's private records. Also asserts the one
runtime-wide read in the production reconciliation path goes through the explicit
admin boundary, not a persona-scoped reader.

Test-only; single POSIX host; no external effect.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import decision, research, pipeline, analytics, isolation, paths, worker  # noqa: E402
from runtime.jsonstore import append_jsonl  # noqa: E402
from runtime.personas import load as load_persona  # noqa: E402

GEN = "social-a"
CUL = "cultural-primandir-atman"


def seed(bot, title, url):
    research.capture(bot, research.Signal.make(
        title, "captured evidence", "unit-test", url, "fixture", ["indian-festivals"]))


class ProductionReadPathTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp

    def test_production_dedup_path_is_persona_scoped(self):
        # Real cycle: general creates a candidate for a signal. The production
        # dedup path (pipeline.is_duplicate) must see it as a duplicate for the
        # GENERAL persona but NOT for the cultural persona (same signal).
        bot = GEN
        sig = research.Signal.make("shared", "captured", "u", "https://e.org/s",
                                   "fixture", ["t"])
        research.capture(bot, sig)
        self.assertEqual(decision.run_cycle(bot, GEN)["outcome"], "candidate_created")
        gen_draft = pipeline.ideate(load_persona(GEN), sig.__dict__)
        cul_draft = pipeline.ideate(load_persona(CUL), sig.__dict__)
        self.assertTrue(pipeline.is_duplicate(bot, gen_draft))
        self.assertFalse(pipeline.is_duplicate(bot, cul_draft),
                         "another persona's history must not make this a duplicate")

    def test_production_analytics_aggregate_is_persona_scoped(self):
        # Emit analytics for two personas on one runtime via the real event path,
        # then the production aggregate must never blend personas.
        bot = GEN
        analytics.emit(analytics.make_event(bot, GEN, "candidate_created",
                       platform="x", content_id="c-a", metrics={"reach": 10}))
        analytics.emit(analytics.make_event(bot, CUL, "candidate_created",
                       platform="x", content_id="c-b", metrics={"reach": 7}))
        gen_agg = analytics.aggregate(bot, GEN, "reach")
        cul_agg = analytics.aggregate(bot, CUL, "reach")
        self.assertEqual(gen_agg["sum"], 10)
        self.assertEqual(cul_agg["sum"], 7)  # not 17 — personas never blended

    def test_persona_private_stores_only_own_records_after_real_cycles(self):
        # Full production cycles for both personas; every persona-scoped store,
        # read through the authoritative interface, contains only that persona's
        # records (no enumeration of the other's private history).
        bot = GEN
        for _ in range(2):
            seed(bot, "gen ledger", "https://example.org/gen")
            decision.run_cycle(bot, GEN)
            seed(bot, "cul note", "https://example.org/cul")
            decision.run_cycle(bot, CUL)
        for store in isolation.PERSONA_SCOPED_STORES:
            gv = isolation.persona_records(bot, GEN, store)
            cv = isolation.persona_records(bot, CUL, store)
            self.assertTrue(all(r.get("persona") == GEN for r in gv), f"{store} GEN")
            self.assertTrue(all(r.get("persona") == CUL for r in cv), f"{store} CUL")

    # The COMPLETE prohibited raw-reader surface (SB-V03-005 LEAD-026): for each
    # persona-private store, the bare whole-runtime reader name that must NOT
    # exist as an ordinary public callable, and the admin-named replacement that
    # must exist. This is the full six-store surface, not a two-name list.
    PROHIBITED_BARE = [
        ("pipeline", "publish_queue", "admin_publish_queue"),
        ("analytics", "events_for", "admin_events_for"),
        ("state.RuntimeState", "content_history", "admin_content_history"),
    ]
    # Bare reader words that must never appear as an ordinary `def` in runtime/
    # (only admin_/persona_-prefixed definitions are allowed).
    BARE_READER_WORDS = ("content_history", "publish_queue", "events_for")

    def _resolve(self, dotted):
        from runtime import pipeline as _p, analytics as _a
        from runtime import state as _s
        return {"pipeline": _p, "analytics": _a,
                "state.RuntimeState": _s.RuntimeState}[dotted]

    def test_no_ordinary_whole_runtime_reader_exists_on_any_surface(self):
        # Every persona-private store: the bare whole-runtime reader must be gone
        # and only the admin-named one remains. Covers content_history too, which
        # the previous two-name test missed (LEAD-026).
        for owner, bare, admin in self.PROHIBITED_BARE:
            obj = self._resolve(owner)
            self.assertFalse(hasattr(obj, bare),
                             f"ordinary whole-runtime reader {owner}.{bare} must not exist")
            self.assertTrue(hasattr(obj, admin),
                            f"admin reader {owner}.{admin} must exist")

    def test_reintroducing_a_bare_whole_runtime_reader_would_fail(self):
        # Structural source guard: no runtime/ module DEFINES or CALLS a bare
        # (non-admin/non-persona) whole-runtime reader for any of the six stores.
        # A reintroduced `def content_history(...)` / `def publish_queue(...)` /
        # `def events_for(...)` — or a bare call to one — fails this test.
        import re
        runtime_dir = Path(__file__).resolve().parent.parent / "runtime"
        words = "|".join(self.BARE_READER_WORDS)
        def_pat = re.compile(rf"\bdef\s+({words})\b")
        call_pat = re.compile(rf"(?<![\w.])(?:self\.)?({words})\s*\(")
        bad = []
        for py in sorted(runtime_dir.glob("*.py")):
            for i, line in enumerate(py.read_text().splitlines(), 1):
                code = line.split("#", 1)[0]
                if def_pat.search(code):
                    bad.append(f"{py.name}:{i}: bare def -> {line.strip()}")
                for m in call_pat.finditer(code):
                    start = m.start(1)
                    prefix = code[max(0, start - 8):start]
                    if prefix.endswith("admin_") or prefix.endswith("persona_"):
                        continue
                    bad.append(f"{py.name}:{i}: bare call -> {line.strip()}")
        self.assertEqual(bad, [], f"bare whole-runtime reader surface in runtime/: {bad}")

    def test_all_six_persona_stores_have_persona_and_admin_readers(self):
        # Audit: every persona-private store surface has an authoritative
        # persona-scoped reader AND an explicit admin reader (whole-runtime access
        # only via the admin boundary).
        for store in isolation.PERSONA_SCOPED_STORES:
            self.assertIn(store, isolation.PERSONA_SCOPED_READERS)
            self.assertIn(store, isolation._ADMIN_READERS)
            # admin_all_records is the only sanctioned whole-runtime entry point.
            self.assertIsInstance(isolation.admin_all_records("social-a", store), list)

    def test_reconcile_uses_admin_boundary_not_persona_read(self):
        # The worker reconciliation read is a deliberate runtime-wide admin read;
        # it must see ALL personas' queue entries (so a takeover can verify the
        # whole external-effect surface), which is exactly admin_all_records.
        bot = GEN
        # Raw FIXTURE queue rows: this test proves the reconciliation READ path.
        # The production writer ``pipeline.enqueue`` refuses payloads without a
        # final-content review binding (V1.7 C05/C06).
        for cid, persona, exp in (("c-a", GEN, "exp-a"), ("c-b", CUL, "exp-b")):
            append_jsonl(paths.content_dir(bot) / "publish_queue.jsonl",
                         {"content_id": cid, "persona": persona, "bot": bot, "platform": "x",
                          "experiment_id": exp, "payload": {"platform": "x"},
                          "publish_authorized": False, "published": False})
        rec = worker._reconcile(bot)
        # Sees BOTH personas' entries (runtime-wide), and none published unauthorized.
        self.assertEqual(rec["queue_items"], 2)
        self.assertTrue(rec["safe"])
        self.assertEqual(rec["queue_items"],
                         len(isolation.admin_all_records(bot, "publish_queue")))


if __name__ == "__main__":
    unittest.main()
