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
from runtime import decision, research, pipeline, analytics, isolation, worker  # noqa: E402
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

    def test_reconcile_uses_admin_boundary_not_persona_read(self):
        # The worker reconciliation read is a deliberate runtime-wide admin read;
        # it must see ALL personas' queue entries (so a takeover can verify the
        # whole external-effect surface), which is exactly admin_all_records.
        bot = GEN
        pipeline.enqueue(bot, {"content_id": "c-a", "persona": GEN, "signal_id": "s",
                               "signature_move": "m"}, {"platform": "x"}, "exp-a")
        pipeline.enqueue(bot, {"content_id": "c-b", "persona": CUL, "signal_id": "s",
                               "signature_move": "m"}, {"platform": "x"}, "exp-b")
        rec = worker._reconcile(bot)
        # Sees BOTH personas' entries (runtime-wide), and none published unauthorized.
        self.assertEqual(rec["queue_items"], 2)
        self.assertTrue(rec["safe"])
        self.assertEqual(rec["queue_items"],
                         len(isolation.admin_all_records(bot, "publish_queue")))


if __name__ == "__main__":
    unittest.main()
