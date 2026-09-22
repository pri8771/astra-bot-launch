"""V1.7 §A — first-bot starvation in scheduled due-work selection.

``worker_once`` runs one bounded unit per invocation. With a fixed candidate
order, a runtime that always has claimable work would be the only one ever
run. These tests prove the durable rotation cursor serves claimable bots in
turn across separate invocations (and separate processes), only advances on a
real claim, and never blocks selection when it is missing or corrupt.
ENGINEERING-ONLY: deterministic providers, temp homes, no model call.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "bin"))

from runtime import due_rotation, leasing, research  # noqa: E402

import worker_once  # noqa: E402

BOTS = ["social-a", "social-b", "social-c"]


class RotationOrderTest(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp())

    def test_no_cursor_keeps_the_callers_order(self):
        self.assertEqual(due_rotation.ordered(BOTS, self.home), BOTS)
        self.assertIsNone(due_rotation.read_cursor(self.home))

    def test_a_claim_rotates_the_next_invocation_past_the_claimed_bot(self):
        due_rotation.record_claim("social-a", BOTS, self.home, session_id="s-1")
        self.assertEqual(due_rotation.ordered(BOTS, self.home),
                         ["social-b", "social-c", "social-a"])
        due_rotation.record_claim("social-c", BOTS, self.home)
        self.assertEqual(due_rotation.ordered(BOTS, self.home),
                         ["social-a", "social-b", "social-c"])

    def test_the_cursor_is_durable_json_next_to_the_runtime_root(self):
        data = due_rotation.record_claim("social-b", BOTS, self.home, session_id="s-9")
        path = due_rotation.cursor_path(self.home)
        self.assertEqual(path, self.home / "scheduler" / "claim_rotation.json")
        on_disk = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(on_disk, data)
        self.assertEqual(on_disk["last_claimed"], "social-b")
        self.assertEqual(on_disk["session_id"], "s-9")
        self.assertEqual(on_disk["schema_version"], due_rotation.SCHEMA_VERSION)

    def test_a_corrupt_or_foreign_cursor_never_blocks_selection(self):
        path = due_rotation.cursor_path(self.home)
        path.parent.mkdir(parents=True)
        for junk in ("{not json", json.dumps({"schema_version": 99, "last_claimed": "social-a"}),
                     json.dumps({"schema_version": 1, "last_claimed": 7}), json.dumps([1, 2])):
            with self.subTest(junk=junk[:20]):
                path.write_text(junk, encoding="utf-8")
                self.assertEqual(due_rotation.ordered(BOTS, self.home), BOTS)

    def test_a_last_claimed_bot_that_is_no_longer_a_candidate_is_ignored(self):
        due_rotation.record_claim("social-z", BOTS + ["social-z"], self.home)
        self.assertEqual(due_rotation.ordered(BOTS, self.home), BOTS)

    def test_rotation_is_shared_across_processes(self):
        """A separate interpreter continues where this one left off."""
        due_rotation.record_claim("social-a", BOTS, self.home)
        code = (
            "import sys, json; sys.path.insert(0, %r); from runtime import due_rotation; "
            "print(json.dumps(due_rotation.ordered(%r, %r)))" % (str(ROOT), BOTS, str(self.home)))
        out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                             timeout=60, check=True).stdout
        self.assertEqual(json.loads(out), ["social-b", "social-c", "social-a"])


class ClaimOneRotationTest(unittest.TestCase):
    """The scheduler entry point serves every claimable bot in turn."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.prior_home = os.environ.get("SBOTS_HOME")
        os.environ["SBOTS_HOME"] = self.tmp
        for bot in BOTS:                           # every bot always has due work
            research.capture(bot, research.Signal.make(
                f"sig-{bot}", "captured", "unit-test", f"https://example.org/{bot}",
                "fixture", ["measurement"]))

    def tearDown(self):
        if self.prior_home is None:
            os.environ.pop("SBOTS_HOME", None)
        else:
            os.environ["SBOTS_HOME"] = self.prior_home

    def _claim(self):
        result, tried = worker_once.claim_one(BOTS, require_adaptive=None)
        return result["bot"], tried

    def test_first_bot_never_starves_the_others_across_invocations(self):
        """Six invocations, every bot always claimable: each bot runs twice."""
        claimed = [self._claim()[0] for _ in range(6)]
        self.assertEqual(claimed, ["social-a", "social-b", "social-c"] * 2)

    def test_a_skipped_held_bot_is_first_in_line_next_time(self):
        """Skipping does not advance the cursor past the skipped bot."""
        self.assertEqual(self._claim()[0], "social-a")
        leasing.acquire("cycle:social-b", "other-worker", ttl_seconds=600)
        bot, tried = self._claim()
        self.assertEqual(bot, "social-c")
        self.assertEqual([t["result"] for t in tried], ["lease_held", "claimed"])
        # Next: rotation starts after social-c -> social-a, then social-b.
        self.assertEqual(self._claim()[0], "social-a")

    def test_no_claim_leaves_the_cursor_untouched(self):
        self.assertEqual(self._claim()[0], "social-a")
        for bot in BOTS:
            leasing.acquire(f"cycle:{bot}", "other-worker", ttl_seconds=600)
        result, tried = worker_once.claim_one(BOTS, require_adaptive=None)
        self.assertIsNone(result)
        self.assertEqual(due_rotation.read_cursor()["last_claimed"], "social-a")

    def test_cursor_write_failure_prevents_any_unit_execution(self):
        from unittest.mock import patch
        with patch.object(due_rotation, "record_claim", side_effect=OSError("cursor unavailable")), \
             patch.object(worker_once.worker.decision, "run_cycle",
                          wraps=worker_once.worker.decision.run_cycle) as cycle:
            with self.assertRaisesRegex(OSError, "cursor unavailable"):
                worker_once.claim_one(BOTS, require_adaptive=None)
            cycle.assert_not_called()
        # Failure releases the lease, so recovery can actually claim the bot.
        self.assertEqual(self._claim()[0], "social-a")

    def test_cursor_is_durable_before_cycle_can_fail(self):
        from unittest.mock import patch
        seen = []
        def fail_cycle(*args, **kwargs):
            cursor = due_rotation.read_cursor()
            seen.append(cursor.get("last_claimed") if cursor else None)
            raise RuntimeError("cycle failed after claim")
        with patch.object(worker_once.worker.decision, "run_cycle", side_effect=fail_cycle):
            with self.assertRaisesRegex(RuntimeError, "cycle failed after claim"):
                worker_once.claim_one(BOTS, require_adaptive=None)
        self.assertEqual(seen, ["social-a"])
        self.assertEqual(self._claim()[0], "social-b")

    def test_an_explicit_home_is_honoured_for_the_cursor(self):
        home = Path(tempfile.mkdtemp())
        result, _ = worker_once.claim_one(BOTS, require_adaptive=None, home=home,
                                          session_id="s-explicit")
        self.assertEqual(result["bot"], "social-a")
        cursor = due_rotation.read_cursor(home)
        self.assertEqual((cursor["last_claimed"], cursor["session_id"]),
                         ("social-a", "s-explicit"))
        self.assertIsNone(due_rotation.read_cursor())     # not under SBOTS_HOME


if __name__ == "__main__":
    unittest.main()
