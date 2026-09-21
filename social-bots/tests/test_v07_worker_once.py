"""SB-V07-001 — bounded worker-once execution, one-task claiming and receipts.

Covers the four properties an OS-scheduled bounded session has to have before
V0.7 operational proof is even meaningful:

* direction is consumed from a real git repository with no ``gh``, no API token
  and no human relay, and the exact canonical SHA is recorded;
* every invocation emits exactly one durable heartbeat and exactly one
  invocation receipt, including when it claims nothing;
* at most ONE task is ever claimed, and a task already held by a live worker is
  skipped as benign no-overlap rather than contended;
* a killed invocation leaves an ``incomplete`` receipt, and the restart writes a
  new one instead of reusing it.

No live model call occurs anywhere here: the bounded unit runs with the
deterministic diagnostic posture explicitly enabled, which is labeled as such.
"""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
BIN = Path(__file__).resolve().parent.parent / "bin"
sys.path.insert(0, str(BIN))

from runtime import direction as direction_mod  # noqa: E402
from runtime import invocation as invocation_mod  # noqa: E402
from runtime import leasing, session_heartbeat as sh  # noqa: E402

import worker_once  # noqa: E402

CANONICAL = direction_mod.CANONICAL_BRANCH


def _git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                          text=True, check=True)


def make_repo(tmp: Path, *, state: dict | None = None,
              directions: dict | None = None) -> Path:
    """A throwaway git repo carrying the canonical coordination branch."""
    repo = tmp / "repo"
    (repo / "social-bots").mkdir(parents=True)
    _git(repo.parent, "init", "-q", str(repo))
    _git(repo, "config", "user.email", "test@example.invalid")
    _git(repo, "config", "user.name", "Test")
    _git(repo, "checkout", "-q", "-b", CANONICAL)
    state = state if state is not None else {
        "worker_lanes": {
            "core": {"branch": "claude/social-bots-windows-core-host",
                     "activity": "assigned_v07_001",
                     "assignment": "build the bounded host worker"},
        },
        "lead_review": {"review_id": "LEAD-038"},
        "runtime_scope": {"autonomous_bots": ["social-a", "social-b", "social-c"]},
        "public_actions": {"no_further_live_model_calls": True},
    }
    (repo / "social-bots" / "STATE.json").write_text(json.dumps(state, indent=2),
                                                     encoding="utf-8")
    if directions is not None:
        d = repo / "social-bots" / "directions"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{directions['lane']}.json").write_text(json.dumps(directions, indent=2),
                                                      encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "canonical state")
    return repo


class DirectionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_direction_is_read_from_git_without_gh_or_a_token(self):
        """Plain git show against the canonical branch is the whole transport."""
        repo = make_repo(self.tmp)
        lead = direction_mod.consume("windows-core", repo, fetch=False)
        self.assertEqual(lead.source, direction_mod.SOURCE_STATE_FALLBACK)
        self.assertEqual(lead.direction_id, "LEAD-038")
        self.assertFalse(lead.halt)
        self.assertEqual(lead.assignment, "build the bounded host worker")

    def test_exact_canonical_sha_is_recorded(self):
        """An audit must be able to say which coordination state a session acted on."""
        repo = make_repo(self.tmp)
        expected = _git(repo, "rev-parse", CANONICAL).stdout.strip()
        lead = direction_mod.consume("windows-core", repo, fetch=False)
        self.assertEqual(lead.canonical_sha, expected)
        self.assertTrue(lead.raw_digest.startswith("sha256:"))

    def test_machine_readable_directions_file_wins_over_state_fallback(self):
        """When the lead writes a directions file, it is authoritative for that lane."""
        repo = make_repo(self.tmp, directions={
            "schema_version": 1, "lane": "windows-core", "direction_id": "LEAD-039",
            "halt": False, "assignment": "finish SB-V07-001", "artifacts": ["SB-V07-001"],
            "bots": ["social-a"], "live_model_calls_authorized": False})
        lead = direction_mod.consume("windows-core", repo, fetch=False)
        self.assertEqual(lead.source, direction_mod.SOURCE_DIRECTIONS_FILE)
        self.assertEqual(lead.direction_id, "LEAD-039")
        self.assertEqual(lead.artifacts, ["SB-V07-001"])

    def test_frozen_lane_activity_is_read_as_a_halt(self):
        """A lane the lead froze must not claim work on its next scheduled session."""
        repo = make_repo(self.tmp, state={
            "worker_lanes": {"canary": {"branch": "claude/social-bots-v04-live-canary",
                                        "activity": "frozen_authorization_consumed",
                                        "assignment": "preserve evidence only"}},
            "lead_review": {"review_id": "LEAD-038"},
            "runtime_scope": {"autonomous_bots": ["social-a"]},
            "public_actions": {"no_further_live_model_calls": True}})
        lead = direction_mod.consume("v04-live-canary", repo, fetch=False)
        self.assertTrue(lead.halt)

    def test_live_model_calls_are_not_authorized_by_default(self):
        """Absent an explicit grant, a consumed direction never authorizes a model call."""
        repo = make_repo(self.tmp)
        self.assertFalse(direction_mod.consume("windows-core", repo, fetch=False)
                         .live_model_calls_authorized)

    def test_failed_fetch_degrades_honestly_instead_of_failing(self):
        """An offline host reads the last known ref and records fetch_ok=false."""
        repo = make_repo(self.tmp)
        lead = direction_mod.consume("windows-core", repo, fetch=True)
        self.assertFalse(lead.fetch_ok)          # no 'origin' remote exists here
        self.assertIsNotNone(lead.fetch_error)
        self.assertIsNotNone(lead.canonical_sha)

    def test_missing_canonical_branch_raises(self):
        """With no canonical ref at all, a session cannot pretend it read direction."""
        repo = self.tmp / "bare"
        repo.mkdir()
        _git(repo.parent, "init", "-q", str(repo))
        _git(repo, "config", "user.email", "t@example.invalid")
        _git(repo, "config", "user.name", "T")
        with self.assertRaises(direction_mod.DirectionError):
            direction_mod.consume("windows-core", repo, fetch=False)

    def test_acknowledgement_records_what_was_consumed(self):
        """The lead can see, from the repo alone, which SHA a session acted on."""
        repo = make_repo(self.tmp)
        lead = direction_mod.consume("windows-core", repo, fetch=False)
        path = direction_mod.acknowledge(lead, session_id="s-1", invocation_id="inv-1",
                                         root=self.tmp / "reports")
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["session_id"], "s-1")
        self.assertEqual(payload["direction"]["canonical_sha"], lead.canonical_sha)
        self.assertIn("not agreement", payload["acknowledgement_means"])


class InvocationReceiptTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_receipt_opens_incomplete_and_closes_terminal(self):
        """A crash mid-unit leaves 'incomplete', never a missing or success record."""
        inv = invocation_mod.start(session_id="s-1", lane="l", branch="b", home=self.tmp)
        opened = json.loads(inv.path.read_text(encoding="utf-8"))
        self.assertEqual(opened["status"], invocation_mod.STATUS_INCOMPLETE)
        self.assertIsNone(opened["exit_code"])
        inv.update(claim_outcome=invocation_mod.CLAIM_CLAIMED, work_outcome="no_action")
        closed = inv.close(exit_code=0)
        self.assertEqual(closed["status"], invocation_mod.STATUS_COMPLETE)
        self.assertEqual(closed["exit_code"], 0)
        self.assertIsNotNone(closed["duration_seconds"])

    def test_a_crashed_invocation_is_visible_in_the_audit(self):
        """An abandoned open receipt is reported, not silently reclaimed."""
        invocation_mod.start(session_id="s-crash", lane="l", branch="b", home=self.tmp)
        inv = invocation_mod.start(session_id="s-restart", lane="l", branch="b",
                                   home=self.tmp)
        inv.update(claim_outcome=invocation_mod.CLAIM_CLAIMED)
        inv.close(exit_code=0)
        audit = invocation_mod.audit(self.tmp)
        self.assertEqual(audit["total_invocations"], 2)
        self.assertEqual(audit["incomplete"], 1)
        self.assertEqual(audit["complete"], 1)
        self.assertEqual(audit["distinct_sessions"], 2)

    def test_a_receipt_without_a_route_decision_is_counted_as_such(self):
        """``live_model_call`` alone means nothing; the route decision is the evidence.

        An earlier version asserted ``live_model_call is False`` on a bare
        receipt, which was tautological — the field was a constant and nothing
        ever set it True. The audit now reports receipts that carry no route
        decision, so a bare receipt cannot pass for a checked one.
        """
        inv = invocation_mod.start(session_id="s-1", lane="l", branch="b", home=self.tmp)
        record = inv.close(exit_code=0)
        self.assertEqual(record["reasoning_route"], {})
        self.assertEqual(invocation_mod.audit(self.tmp)["receipts_without_a_route_decision"], 1)

    def test_a_refused_live_route_is_counted_distinctly_from_a_permitted_one(self):
        """The audit must distinguish 'no live call' from 'never checked'."""
        inv = invocation_mod.start(session_id="s-2", lane="l", branch="b", home=self.tmp)
        inv.update(reasoning_route={"mode": "claude-cli", "live_route_requested": True,
                                    "permitted": False, "reason": "fixture"},
                   live_model_call=False)
        inv.close(exit_code=6)
        audit = invocation_mod.audit(self.tmp)
        self.assertEqual(audit["live_routes_refused"], 1)
        self.assertEqual(audit["live_model_calls"], 0)
        self.assertEqual(audit["receipts_without_a_route_decision"], 0)

    def test_index_records_both_phases(self):
        """The index carries an open and a close row so crashes are countable."""
        inv = invocation_mod.start(session_id="s-1", lane="l", branch="b", home=self.tmp)
        inv.close(exit_code=3)
        rows = [json.loads(line) for line in
                (invocation_mod.invocations_dir(self.tmp) / "index.jsonl")
                .read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertEqual([r["phase"] for r in rows], ["open", "close"])
        self.assertEqual(rows[1]["exit_code"], 3)


class ClaimOneTest(unittest.TestCase):
    """At most one task per invocation, with no probe-then-acquire race."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.prior_home = os.environ.get("SBOTS_HOME")
        os.environ["SBOTS_HOME"] = self.tmp

    def tearDown(self):
        if self.prior_home is None:
            os.environ.pop("SBOTS_HOME", None)
        else:
            os.environ["SBOTS_HOME"] = self.prior_home

    def test_only_the_first_claimable_task_runs(self):
        """Three candidates, one invocation: exactly one unit executes."""
        result, tried = worker_once.claim_one(["social-a", "social-b", "social-c"],
                                              require_adaptive=None)
        self.assertIsNotNone(result)
        self.assertEqual(result["bot"], "social-a")
        self.assertEqual([t["result"] for t in tried], ["claimed"])

    def test_a_held_task_is_skipped_and_the_next_is_claimed(self):
        """No-overlap is a skip, not a wait and not a contention failure."""
        leasing.acquire("cycle:social-a", "other-worker", ttl_seconds=600)
        result, tried = worker_once.claim_one(["social-a", "social-b"],
                                              require_adaptive=None)
        self.assertEqual(result["bot"], "social-b")
        self.assertEqual([t["result"] for t in tried], ["lease_held", "claimed"])
        self.assertEqual(tried[0]["holder"], "other-worker")

    def test_all_tasks_held_claims_nothing(self):
        """When every candidate is live-held, the invocation claims none."""
        for bot in ("social-a", "social-b"):
            leasing.acquire(f"cycle:{bot}", "other-worker", ttl_seconds=600)
        result, tried = worker_once.claim_one(["social-a", "social-b"],
                                              require_adaptive=None)
        self.assertIsNone(result)
        self.assertEqual([t["result"] for t in tried], ["lease_held", "lease_held"])


class WorkerOnceEndToEndTest(unittest.TestCase):
    """One process invocation, end to end, with no live model call."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = make_repo(self.tmp)
        self.home = self.tmp / "home"
        self.reports = self.tmp / "reports"
        self.prior_home = os.environ.get("SBOTS_HOME")
        os.environ["SBOTS_HOME"] = str(self.home)

    def tearDown(self):
        if self.prior_home is None:
            os.environ.pop("SBOTS_HOME", None)
        else:
            os.environ["SBOTS_HOME"] = self.prior_home

    def _run(self, *extra, session_id="s-inv-1", bots="social-a"):
        # The entrypoint prints its receipt summary; capture it so test output
        # stays readable. The durable receipt, not stdout, is the evidence.
        with contextlib.redirect_stdout(io.StringIO()):
            return worker_once.main([
                "--lane", "windows-core", "--branch", "claude/test-branch",
                "--bots", bots, "--repo-root", str(self.repo),
                "--session-id", session_id,
                "--skip-fetch", "--allow-deterministic", "--home", str(self.home),
                "--report-root", str(self.reports), *extra])

    def test_a_successful_invocation_leaves_one_heartbeat_and_one_receipt(self):
        """The two independent durable traces every scheduled session must leave."""
        self.assertEqual(self._run(), worker_once.EXIT_OK)
        log = sh.read_log("windows-core", self.reports)
        self.assertEqual(len(log), 1)
        self.assertEqual(log[0]["cadence_mode"], "SESSION_ONCE")
        audit = invocation_mod.audit(self.home)
        self.assertEqual(audit["total_invocations"], 1)
        self.assertEqual(audit["complete"], 1)
        self.assertEqual(audit["claims"][invocation_mod.CLAIM_CLAIMED], 1)

    def test_the_heartbeat_records_the_canonical_sha_it_consumed(self):
        """Direction is consumed before the heartbeat so the attestation is real."""
        self._run()
        expected = _git(self.repo, "rev-parse", CANONICAL).stdout.strip()
        record = sh.latest("windows-core", self.reports)
        self.assertEqual(record["canonical_seen_sha"], expected)
        self.assertEqual(record["lead_review_seen"], "LEAD-038")

    def test_repeated_invocations_produce_a_sequence_of_sessions(self):
        """Recurring liveness is repeated bounded invocations, each with its own pair."""
        for i in range(3):
            self.assertEqual(self._run(session_id=f"s-inv-{i}"), worker_once.EXIT_OK)
        self.assertEqual(len(sh.read_log("windows-core", self.reports)), 3)
        audit = invocation_mod.audit(self.home)
        self.assertEqual(audit["complete"], 3)
        self.assertEqual(audit["distinct_sessions"], 3)
        # Every receipt carries a real route decision, so "no live call" is a
        # checked fact rather than an unset field.
        self.assertEqual(audit["receipts_without_a_route_decision"], 0)
        self.assertEqual(audit["live_model_calls"], 0)

    def test_reusing_a_session_id_is_refused(self):
        """A reused session id would forge a second heartbeat for one session."""
        self.assertEqual(self._run(session_id="s-dup"), worker_once.EXIT_OK)
        self.assertEqual(self._run(session_id="s-dup"), worker_once.EXIT_FAILURE)
        self.assertEqual(len(sh.read_log("windows-core", self.reports)), 1)
        receipts = invocation_mod.read_all(self.home)
        failed = [r for r in receipts if r["exit_code"] == worker_once.EXIT_FAILURE]
        self.assertEqual(len(failed), 1)
        self.assertEqual(failed[0]["work_outcome"], "duplicate_session_heartbeat")

    def test_no_overlap_exits_three_and_still_writes_both_traces(self):
        """A fully contended invocation is benign but still fully evidenced."""
        leasing.acquire("cycle:social-a", "other-worker", ttl_seconds=600)
        self.assertEqual(self._run(), worker_once.EXIT_NO_OVERLAP)
        self.assertEqual(len(sh.read_log("windows-core", self.reports)), 1)
        audit = invocation_mod.audit(self.home)
        self.assertEqual(audit["claims"][invocation_mod.CLAIM_NO_OVERLAP], 1)

    def test_halted_lane_exits_five_and_claims_nothing(self):
        """A frozen lane runs, records, and stands down without touching a task."""
        repo = make_repo(self.tmp / "frozen", state={
            "worker_lanes": {"core": {"branch": "claude/social-bots-windows-core-host",
                                      "activity": "frozen_evidence_only",
                                      "assignment": "preserve evidence only"}},
            "lead_review": {"review_id": "LEAD-038"},
            "runtime_scope": {"autonomous_bots": ["social-a"]},
            "public_actions": {"no_further_live_model_calls": True}})
        with contextlib.redirect_stdout(io.StringIO()):
            code = worker_once.main([
                "--lane", "windows-core", "--branch", "b", "--bots", "social-a",
                "--repo-root", str(repo), "--session-id", "s-halt", "--skip-fetch",
                "--allow-deterministic", "--home", str(self.home),
                "--report-root", str(self.reports)])
        self.assertEqual(code, worker_once.EXIT_HALTED)
        self.assertEqual(invocation_mod.audit(self.home)["claims"][
            invocation_mod.CLAIM_HALTED], 1)
        record = sh.latest("windows-core", self.reports)
        self.assertEqual(record["blocker"], "lane halted by lead direction")

    def test_direction_is_acknowledged_for_the_session(self):
        """Every invocation records the direction it consumed, for the lead to read."""
        self._run(session_id="s-ack")
        ack = json.loads((self.reports / "worker-reports" / "windows-core" /
                          "DIRECTION_ACK.json").read_text(encoding="utf-8"))
        self.assertEqual(ack["session_id"], "s-ack")
        self.assertFalse(ack["direction"]["live_model_calls_authorized"])


if __name__ == "__main__":
    unittest.main()
