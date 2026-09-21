"""SB-V03-005 — persona decision-history read-boundary regression.

Complements ``test_isolation.py``: every other non-shared store in the V03-005
Priority-2 list (content history, experiments, publish queue, action history,
analytics) already has a mixed-persona no-bleed regression, but the persona
*decision-history* read (``isolation.persona_decisions``) did not. This adds a
real production-path regression: two personas on ONE runtime each run a real
``decision.run_cycle`` (which writes decisions.jsonl inside the fenced commit),
then each persona's decision view must contain only its own records, the views
must be disjoint, their union must be the whole store, and the audit must be
clean for the decisions store.

Test-only; no runtime/ source is modified. Single POSIX host, no external effect.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import decision, research, isolation  # noqa: E402

GEN = "social-a"
CUL = "cultural-primandir-atman"


def seed(bot, title, url):
    research.capture(bot, research.Signal.make(
        title, "captured evidence for the runtime", "unit-test", url,
        "fixture", ["indian-festivals"]))


class DecisionHistoryIsolationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp

    def test_persona_decisions_do_not_bleed_across_personas(self):
        bot = GEN
        # Two personas on the SAME runtime each run a real decision cycle.
        seed(bot, "festival ledger", "https://example.org/gen")
        rec_gen = decision.run_cycle(bot, GEN)
        seed(bot, "festival note", "https://example.org/cul")
        rec_cul = decision.run_cycle(bot, CUL)

        gen_view = isolation.persona_decisions(bot, GEN)
        cul_view = isolation.persona_decisions(bot, CUL)

        # Each persona sees at least its own just-written decision...
        self.assertTrue(gen_view, "general persona has no decision records")
        self.assertTrue(cul_view, "cultural persona has no decision records")
        # ...and ONLY its own (strict persona filter, no bleed).
        self.assertTrue(all(r["persona"] == GEN for r in gen_view))
        self.assertTrue(all(r["persona"] == CUL for r in cul_view))
        self.assertIn(rec_gen["persona"], {GEN})
        self.assertIn(rec_cul["persona"], {CUL})

    def test_decision_views_are_disjoint_and_complete(self):
        bot = GEN
        for _ in range(3):
            seed(bot, "festival ledger", "https://example.org/gen")
            decision.run_cycle(bot, GEN)
            seed(bot, "festival note", "https://example.org/cul")
            decision.run_cycle(bot, CUL)

        gen_ids = {id(r) for r in isolation.persona_decisions(bot, GEN)}
        cul_ids = {id(r) for r in isolation.persona_decisions(bot, CUL)}
        self.assertTrue(gen_ids.isdisjoint(cul_ids))

        # Union of per-persona views == the whole decisions store (nothing lost,
        # nothing double-counted, no unlabeled/foreign-persona record).
        from runtime import paths
        from runtime.jsonstore import read_jsonl
        whole = read_jsonl(paths.memory_dir(bot) / "decisions.jsonl")
        gen_n = len(isolation.persona_decisions(bot, GEN))
        cul_n = len(isolation.persona_decisions(bot, CUL))
        self.assertEqual(gen_n + cul_n, len(whole))
        self.assertTrue(all(r.get("persona") in (GEN, CUL) for r in whole))

    def test_audit_reports_decisions_store_clean(self):
        bot = GEN
        seed(bot, "festival ledger", "https://example.org/gen")
        decision.run_cycle(bot, GEN)
        seed(bot, "festival note", "https://example.org/cul")
        decision.run_cycle(bot, CUL)

        report = isolation.audit(bot, [GEN, CUL])
        self.assertTrue(report["clean"])
        # The decisions store specifically partitions with no foreign persona.
        self.assertIn("decisions", report["stores"])
        self.assertEqual(report["stores"]["decisions"]["unknown_persona"], [])


if __name__ == "__main__":
    unittest.main()
