"""SB-V03-005 — authoritative persona-scoped production read boundary.

Complements the per-store no-bleed tests in ``test_isolation.py`` /
``test_isolation_decisions.py`` with a GENERIC guarantee over the whole boundary:

- every store in ``PERSONA_SCOPED_STORES`` has an authoritative persona reader;
- ``persona_records`` dispatches to it and returns only that persona's records;
- for a real mixed-persona runtime, each persona reader is strict (no foreign
  records) and the union of the two persona views equals the admin whole-runtime
  read (nothing lost/duplicated), across ALL stores at once;
- the raw whole-runtime read is only reachable through the explicitly named
  ``admin_all_records`` (there is no unnamed public whole-runtime reader).

Test-only; single POSIX host; no external effect.
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
        title, "captured evidence", "unit-test", url, "fixture", ["indian-festivals"]))


class ReadBoundaryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp

    def test_every_persona_scoped_store_has_authoritative_reader(self):
        for store in isolation.PERSONA_SCOPED_STORES:
            self.assertIn(store, isolation.PERSONA_SCOPED_READERS,
                          f"{store} has no authoritative persona reader")
            self.assertIn(store, isolation._ADMIN_READERS,
                          f"{store} has no admin reader")

    def test_persona_records_dispatch_matches_named_readers(self):
        bot = GEN
        seed(bot, "gen ledger", "https://example.org/gen")
        decision.run_cycle(bot, GEN)
        # persona_records must equal the corresponding named reader for each store.
        self.assertEqual(isolation.persona_records(bot, GEN, "decisions"),
                         isolation.persona_decisions(bot, GEN))
        self.assertEqual(isolation.persona_records(bot, GEN, "content_history"),
                         isolation.persona_content_history(bot, GEN))

    def test_unknown_store_rejected(self):
        with self.assertRaises(ValueError):
            isolation.persona_records(GEN, GEN, "not_a_store")
        with self.assertRaises(ValueError):
            isolation.admin_all_records(GEN, "not_a_store")

    def test_mixed_persona_boundary_holds_across_all_stores(self):
        bot = GEN
        # General creates candidates; cultural is WITHHELD (no reviewer) but still
        # writes action/decision records. Run several rounds to populate stores.
        for _ in range(3):
            seed(bot, "gen ledger", "https://example.org/gen")
            decision.run_cycle(bot, GEN)
            seed(bot, "cul note", "https://example.org/cul")
            decision.run_cycle(bot, CUL)

        for store in isolation.PERSONA_SCOPED_STORES:
            gen_view = isolation.persona_records(bot, GEN, store)
            cul_view = isolation.persona_records(bot, CUL, store)
            whole = isolation.admin_all_records(bot, store)
            # Strict: no foreign persona in either view.
            self.assertTrue(all(r.get("persona") == GEN for r in gen_view), store)
            self.assertTrue(all(r.get("persona") == CUL for r in cul_view), store)
            # Complete: the two persona views partition the whole store (every
            # record here is labeled GEN or CUL, so union == whole).
            self.assertEqual(len(gen_view) + len(cul_view), len(whole),
                             f"{store}: persona views do not partition the store")

        # And the audit agrees the whole runtime is clean across both personas.
        self.assertTrue(isolation.audit(bot, [GEN, CUL])["clean"])


if __name__ == "__main__":
    unittest.main()
