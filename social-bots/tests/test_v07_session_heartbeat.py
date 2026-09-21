"""SB-V07-001 — the durable SESSION_ONCE heartbeat.

Owner policy: ONE FRESH WORKER SESSION = ONE HEARTBEAT. These tests protect the
three properties that make that rule meaningful rather than aspirational: the
durable write needs no GitHub transport, a session cannot emit twice, and a
skipped Issue comment is recorded truthfully instead of being claimed.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import session_heartbeat as sh  # noqa: E402


def make(session_id="s-test-0001", lane="test-lane", **overrides):
    fields = dict(
        session_id=session_id, lane=lane, branch="claude/test-branch",
        current_artifact="SB-V07-001", canonical_seen_sha="deadbee",
        lead_review_seen="LEAD-038", notes="unit test")
    fields.update(overrides)
    return sh.SessionHeartbeat(**fields)


class DurableWriteTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())

    def test_emit_writes_both_the_ledger_and_the_latest_view(self):
        """A heartbeat lands in the append-only log and in HEARTBEAT.json."""
        record = sh.emit(make(), root=self.root)
        lane_dir = sh.lane_dir("test-lane", self.root)
        log = sh.read_log("test-lane", self.root)
        self.assertEqual(len(log), 1)
        self.assertEqual(log[0]["session_id"], "s-test-0001")
        latest = json.loads((lane_dir / sh.HEARTBEAT_FILENAME).read_text(encoding="utf-8"))
        self.assertEqual(latest, record)

    def test_cadence_and_status_are_the_session_once_contract(self):
        """New sessions must carry SESSION_ONCE/STARTED, not a legacy timed cadence."""
        record = sh.emit(make(), root=self.root)
        self.assertEqual(record["cadence_mode"], "SESSION_ONCE")
        self.assertEqual(record["session_status"], "STARTED")
        self.assertEqual(record["schema_version"], sh.SCHEMA_VERSION)

    def test_required_fields_are_present(self):
        """The protocol's minimum heartbeat fields must all be recorded."""
        record = sh.emit(make(), root=self.root)
        for field in ("schema_version", "session_id", "lane", "branch", "started_at",
                      "session_status", "current_artifact", "canonical_seen_sha",
                      "lead_review_seen", "runtime", "notes"):
            self.assertIn(field, record)
        self.assertTrue(record["started_at"].endswith("Z"))

    def test_runtime_identity_carries_no_secrets(self):
        """Host identification is coarse: no user, path, address or env value."""
        record = sh.emit(make(), root=self.root)
        self.assertEqual(set(record["runtime"]),
                         {"host", "platform", "platform_release", "python", "pid"})

    def test_started_at_is_stamped_from_the_real_clock_at_emit(self):
        """No backfill: a supplied timestamp is overwritten, not honoured.

        An earlier version of this test asserted a TypeError for a kwarg that
        does not exist under any implementation, so it passed against a fully
        backfillable class. This one changes the value and checks the result.
        """
        record = sh.emit(make(started_at="1999-01-01T00:00:00Z"), root=self.root)
        self.assertNotEqual(record["started_at"], "1999-01-01T00:00:00Z")
        self.assertEqual(sh.read_log("test-lane", self.root)[0]["started_at"],
                         record["started_at"])

    def test_a_second_heartbeat_for_one_session_is_refused(self):
        """ONE SESSION = ONE HEARTBEAT is structural: the second emit raises."""
        sh.emit(make(), root=self.root)
        with self.assertRaises(sh.DuplicateSessionHeartbeat):
            sh.emit(make(), root=self.root)
        self.assertEqual(len(sh.read_log("test-lane", self.root)), 1)

    def test_distinct_sessions_append_distinct_records(self):
        """Recurring liveness is a sequence of sessions, each with its own record."""
        for i in range(3):
            sh.emit(make(session_id=f"s-test-{i:04d}"), root=self.root)
        log = sh.read_log("test-lane", self.root)
        self.assertEqual([r["session_id"] for r in log],
                         ["s-test-0000", "s-test-0001", "s-test-0002"])
        self.assertEqual(sh.latest("test-lane", self.root)["session_id"], "s-test-0002")

    def test_legacy_records_without_session_ids_do_not_block_new_sessions(self):
        """Pre-existing schema-2 lane logs must not be invalidated or rewritten."""
        lane_dir = sh.lane_dir("test-lane", self.root)
        lane_dir.mkdir(parents=True, exist_ok=True)
        (lane_dir / sh.LOG_FILENAME).write_text(
            json.dumps({"schema_version": 2, "lane": "test-lane", "sequence": 1}) + "\n",
            encoding="utf-8")
        sh.emit(make(), root=self.root)
        log = sh.read_log("test-lane", self.root)
        self.assertEqual(len(log), 2)
        self.assertEqual(log[0]["schema_version"], 2)

    def test_new_session_id_is_unique(self):
        """Generated ids must not collide, or the duplicate guard would misfire."""
        ids = {sh.new_session_id() for _ in range(200)}
        self.assertEqual(len(ids), 200)


class IssueVisibilityTest(unittest.TestCase):
    """The GitHub comment is visibility only and must never gate the durable write."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp())

    def test_durable_write_succeeds_with_no_github_transport(self):
        """Missing gh is recorded as a skip reason; the heartbeat still lands."""
        heartbeat = make()
        # What a host without gh produces, recorded rather than hidden.
        heartbeat.issue_comment_posted = False
        heartbeat.issue_comment_skipped_reason = "gh CLI not found on PATH"
        record = sh.emit(heartbeat, root=self.root)
        self.assertFalse(record["issue_comment_posted"])
        self.assertIn("gh", record["issue_comment_skipped_reason"])
        self.assertEqual(len(sh.read_log("test-lane", self.root)), 1)

    def test_failed_post_never_raises_and_never_claims_success(self):
        """Any gh failure returns (False, reason) rather than propagating."""
        class Proc:
            returncode = 1
            stderr = "gh: not authenticated"

        posted, reason = sh.post_issue_comment(
            make().to_record(), runner=lambda cmd, text: Proc())
        self.assertFalse(posted)
        self.assertIn("not authenticated", reason)

    def test_raising_transport_is_swallowed_into_a_reason(self):
        """A transport that throws must not take down the session."""
        def runner(cmd, text):
            raise OSError("boom")

        posted, reason = sh.post_issue_comment(make().to_record(), runner=runner)
        self.assertFalse(posted)
        self.assertIn("OSError", reason)

    def test_successful_post_is_reported(self):
        """A genuinely successful comment is recorded as posted."""
        class Proc:
            returncode = 0
            stderr = ""

        captured = {}

        def runner(cmd, text):
            captured["cmd"], captured["text"] = cmd, text
            return Proc()

        posted, reason = sh.post_issue_comment(make().to_record(), issue=3, runner=runner)
        self.assertTrue(posted)
        self.assertIsNone(reason)
        self.assertIn("3", captured["cmd"])
        self.assertIn("s-test-0001", captured["text"])

    def test_comment_body_states_the_session_facts(self):
        """The visibility comment must carry the same facts as the durable record."""
        body = sh.issue_comment_body(make().to_record())
        for fragment in ("SESSION_ONCE", "s-test-0001", "test-lane", "LEAD-038", "deadbee"):
            self.assertIn(fragment, body)


if __name__ == "__main__":
    unittest.main()
