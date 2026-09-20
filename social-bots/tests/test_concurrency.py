"""SB-R0B — adversarial concurrency correctness.

Threads exercise the filesystem-level lease primitives concurrently. The
guarantees (single owner on stale takeover; one writer per runtime state) are
enforced by atomic syscalls, so they hold across processes too — threads with a
barrier are enough to surface a race because os.rename/os.open release the GIL.
"""
import os
import sys
import json
import tempfile
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import leasing, worker, research  # noqa: E402
from runtime.state import BotState  # noqa: E402


class StaleTakeoverRaceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp

    def _contend(self, task_id, n):
        """n threads race to acquire task_id; return (winners, held_rejections)."""
        barrier = threading.Barrier(n)
        winners, rejects, errors = [], [], []

        def go(i):
            barrier.wait()
            try:
                lease = leasing.acquire(task_id, f"w{i}", ttl_seconds=300)
                winners.append(lease)
            except leasing.LeaseHeld:
                rejects.append(i)
            except Exception as e:  # noqa: BLE001
                errors.append(repr(e))

        threads = [threading.Thread(target=go, args=(i,)) for i in range(n)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        return winners, rejects, errors

    def test_concurrent_stale_takeover_single_owner(self):
        # Repeat many rounds to surface the race.
        for rnd in range(40):
            task = f"t-{rnd}"
            leasing.acquire(task, "dead", ttl_seconds=0)   # pre-existing STALE lease
            winners, rejects, errors = self._contend(task, 6)
            self.assertEqual(errors, [], f"round {rnd}: unexpected errors {errors}")
            # Exactly one contender may own the task at once.
            self.assertEqual(len(winners), 1,
                             f"round {rnd}: {len(winners)} winners (expected 1)")
            # The on-disk lease is exactly the winner's.
            on_disk = leasing.inspect(task)
            self.assertEqual(on_disk["lease_id"], winners[0].lease_id)
            self.assertTrue(winners[0].reconcile_required)
            # Everyone else was told they did NOT acquire it.
            self.assertEqual(len(rejects), 5)

    def test_concurrent_fresh_create_single_owner(self):
        for rnd in range(40):
            task = f"f-{rnd}"                                # no pre-existing lease
            winners, rejects, errors = self._contend(task, 6)
            self.assertEqual(errors, [])
            self.assertEqual(len(winners), 1)
            self.assertFalse(winners[0].reconcile_required)  # clean create, no takeover


class SharedRuntimeConcurrencyTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp

    def test_runtime_task_id_ignores_persona(self):
        # The lease boundary is the runtime, not the persona.
        self.assertEqual(worker.runtime_task_id("social-a"), "cycle:social-a")
        self.assertNotIn("cultural", worker.runtime_task_id("social-a"))

    def test_second_persona_on_runtime_blocked_while_held(self):
        # A general-persona cycle holds the runtime lease; a cultural-persona cycle
        # on the SAME runtime must be rejected (cannot co-mutate bot_state.json).
        held = leasing.acquire(worker.runtime_task_id("social-a"), "holder", ttl_seconds=300)
        with self.assertRaises(leasing.LeaseHeld):
            worker.run_one_unit(worker.runtime_task_id("social-a"),
                                "social-a", "cultural-primandir-atman")
        leasing.release(held)

    def test_concurrent_personas_no_lost_update(self):
        # Two personas on one runtime race repeatedly. Invariant: bot_state stays
        # valid, cycle counter equals the number of cycles that actually ran, and
        # the consumed-signal ledger never contains duplicates.
        bot, task = "social-a", worker.runtime_task_id("social-a")
        successes = 0
        for rnd in range(25):
            # fresh evidence each round so a cycle has something to consume
            research.capture(bot, research.Signal.make(
                f"sig {rnd}", "captured", "unit-test",
                f"https://example.org/{rnd}", "fixture", ["measurement"]))
            barrier = threading.Barrier(2)
            outcomes = []

            def go(persona):
                barrier.wait()
                try:
                    worker.run_one_unit(task, bot, persona)
                    outcomes.append("ok")
                except leasing.LeaseHeld:
                    outcomes.append("held")
                except Exception as e:  # noqa: BLE001
                    outcomes.append(repr(e))

            tg = threading.Thread(target=go, args=("social-a",))
            tc = threading.Thread(target=go, args=("cultural-primandir-atman",))
            tg.start(); tc.start(); tg.join(); tc.join()
            self.assertTrue(all(o in ("ok", "held") for o in outcomes),
                            f"round {rnd}: {outcomes}")
            successes += outcomes.count("ok")

        st = BotState.load(bot)
        # No lost update: every cycle that ran incremented the counter exactly once.
        self.assertEqual(st.data["counters"]["cycles"], successes)
        # Ledger integrity: no duplicate consumption under concurrency.
        consumed = st.data["consumed_signal_ids"]
        self.assertEqual(len(consumed), len(set(consumed)))
        # bot_state on disk is valid JSON (not torn by concurrent writers).
        raw = (Path(self.tmp) / "state" / bot / "bot_state.json").read_text()
        json.loads(raw)


if __name__ == "__main__":
    unittest.main()
