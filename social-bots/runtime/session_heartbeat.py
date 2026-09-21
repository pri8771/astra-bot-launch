"""SB-V07-001 — durable SESSION_ONCE worker-session heartbeat.

Owner policy (HEARTBEAT_ASSIGNMENT_PROTOCOL.md, LEAD-038):

    ONE FRESH WORKER SESSION = ONE HEARTBEAT.

There is no recurring in-session heartbeat, no soak and no daemon. A session
emits exactly one durable record after it has synced and read current
coordination, then works normally.

Why this module exists
----------------------
The previous heartbeat helper (``bin/worker_heartbeat.py``) implements the
superseded timed cadence (BOOTSTRAP_15M / HOURLY with ``next_due_at``). It is
kept for backward compatibility with already-committed lane logs, but new
sessions use this module, which:

* writes **local durable evidence first** — a plain append-only JSONL ledger plus
  a latest-state JSON file under ``worker-reports/<lane>/``. No network, no
  ``gh``, no GitHub API and no subprocess is required, so a session on a host
  without GitHub transport still produces valid heartbeat evidence;
* enforces one-session-one-heartbeat structurally: a second call for the same
  ``session_id`` is refused (``DuplicateSessionHeartbeat``) instead of silently
  appending a second record. A loop cannot manufacture liveness;
* refuses to backfill: ``emit`` re-stamps ``started_at`` from the real clock and
  re-stamps the contract fields (``schema_version``, ``cadence_mode``,
  ``session_status``), so a caller cannot hand in a forged timestamp or relabel a
  record as a different cadence;
* is the per-invocation unit the V0.7 recurring-liveness argument is built from.
  Recurring liveness is the SEQUENCE of independently OS-scheduled sessions, each
  with one of these records plus its invocation receipt — never a chat kept awake.

This module makes no acceptance claim. A heartbeat proves a session started, read
coordination and began work. It proves nothing about correctness.
"""
from __future__ import annotations

import json
import os
import platform
import re
import socket
import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 3
CADENCE_MODE = "SESSION_ONCE"
SESSION_STATUS_STARTED = "STARTED"

# Repo-relative root: .../social-bots
ROOT = Path(__file__).resolve().parent.parent

HEARTBEAT_FILENAME = "HEARTBEAT.json"
LOG_FILENAME = "HEARTBEAT_LOG.jsonl"
PROGRESS_FILENAME = "CURRENT_PROGRESS.md"


# A lane names a directory under worker-reports/. Validated, because an
# unvalidated lane is a path-traversal write out of the reports root.
_LANE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


class UnsafeLane(ValueError):
    """Raised when a lane name is not a safe single directory component."""


class CorruptHeartbeatLog(Exception):
    """Raised when a lane ledger cannot be read at all."""


class DuplicateSessionHeartbeat(Exception):
    """Raised when a session_id already has a heartbeat in the durable log.

    This is the structural enforcement of ONE SESSION = ONE HEARTBEAT: the second
    emit for a session is an error, not an extra record.
    """


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def check_lane(lane: str) -> str:
    """Validate a lane name, or raise ``UnsafeLane``."""
    if not isinstance(lane, str) or not _LANE_RE.match(lane):
        raise UnsafeLane(
            f"lane {lane!r} is not a safe directory component; a lane may not "
            f"traverse out of the worker-reports root")
    return lane


def lane_dir(lane: str, root: str | Path | None = None) -> Path:
    """Durable per-lane report directory (``worker-reports/<lane>/``)."""
    base = Path(root) if root is not None else ROOT
    return base / "worker-reports" / check_lane(lane)


def new_session_id(prefix: str = "s") -> str:
    """A fresh, collision-resistant session id for this worker session."""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}-{stamp}-{uuid.uuid4().hex[:8]}"


def runtime_identity() -> dict:
    """Non-secret host/runtime identification.

    Deliberately coarse: hostname, OS/release family, python version and pid. No
    usernames, paths, network addresses, tokens or environment values.
    """
    try:
        host = socket.gethostname()
    except OSError:                                  # pragma: no cover - defensive
        host = "unknown"
    return {
        "host": host[:64],
        "platform": platform.system(),
        "platform_release": platform.release()[:64],
        "python": platform.python_version(),
        "pid": os.getpid(),
    }


@dataclass
class SessionHeartbeat:
    """One durable worker-session heartbeat record."""

    session_id: str
    lane: str
    branch: str
    current_artifact: str
    canonical_seen_sha: str | None = None
    lead_review_seen: str | None = None
    head_sha: str | None = None
    blocker: str | None = None
    notes: str = ""
    schema_version: int = SCHEMA_VERSION
    cadence_mode: str = CADENCE_MODE
    session_status: str = SESSION_STATUS_STARTED
    started_at: str = field(default_factory=now_iso)
    runtime: dict = field(default_factory=runtime_identity)
    issue_comment_posted: bool = False
    issue_comment_skipped_reason: str | None = None

    def to_record(self) -> dict:
        return asdict(self)


def read_log(lane: str, root: str | Path | None = None) -> list[dict]:
    """Read the append-only durable heartbeat ledger for a lane.

    A line that does not parse is surfaced as ``{"_unparseable": True, ...}``
    rather than raised or dropped. Raising would wedge the lane permanently after
    one torn append; dropping would hide it. Surfacing keeps the ledger usable
    and keeps the damage visible to an audit.
    """
    path = lane_dir(lane, root) / LOG_FILENAME
    if not path.exists():
        return []
    out: list[dict] = []
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CorruptHeartbeatLog(f"cannot read {path}: {exc}") from exc
    for number, line in enumerate(content.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            out.append({"_unparseable": True, "line_number": number,
                        "error": str(exc), "raw_prefix": line[:120]})
            continue
        out.append(record if isinstance(record, dict) else
                   {"_unparseable": True, "line_number": number,
                    "error": "line is not a JSON object"})
    return out


def session_ids(lane: str, root: str | Path | None = None) -> set[str]:
    """Session ids that already have a durable heartbeat in this lane."""
    return {
        str(rec.get("session_id"))
        for rec in read_log(lane, root)
        if rec.get("session_id")
    }


def lanes_present(root: str | Path | None = None) -> list[str]:
    """Lane directories that currently hold a heartbeat ledger."""
    base = (Path(root) if root is not None else ROOT) / "worker-reports"
    if not base.is_dir():
        return []
    return sorted(d.name for d in base.iterdir()
                  if d.is_dir() and (d / LOG_FILENAME).exists()
                  and _LANE_RE.match(d.name))


def find_session(session_id: str, root: str | Path | None = None) -> str | None:
    """The lane whose ledger already holds ``session_id``, if any.

    One session = one heartbeat is a claim about the SESSION, not about a lane.
    Checking only the target lane would let the same session id emit once per
    lane, so every lane ledger is checked.
    """
    for lane in lanes_present(root):
        if session_id in session_ids(lane, root):
            return lane
    return None


def _append_jsonl(path: Path, record: dict) -> None:
    """Durably append one record (flush + fsync so a crash cannot lose it)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, sort_keys=True, ensure_ascii=False)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, sort_keys=True, ensure_ascii=False)
        fh.write("\n")
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def emit(heartbeat: SessionHeartbeat, root: str | Path | None = None) -> dict:
    """Append exactly one durable heartbeat for this session and refresh latest state.

    Order matters: the append-only ledger is written FIRST, so a crash between the
    two writes leaves the durable history correct (``HEARTBEAT.json`` is a derived
    convenience view, never the source of truth).

    Raises ``DuplicateSessionHeartbeat`` if this ``session_id`` already emitted.
    """
    directory = lane_dir(heartbeat.lane, root)
    existing_lane = find_session(heartbeat.session_id, root)
    if existing_lane is not None:
        raise DuplicateSessionHeartbeat(
            f"session {heartbeat.session_id!r} already has a durable heartbeat in "
            f"lane {existing_lane!r}; ONE SESSION = ONE HEARTBEAT")
    # Re-stamp the fields that define the contract, so a caller cannot backfill a
    # timestamp or relabel a record as a different schema/cadence/status.
    heartbeat.started_at = now_iso()
    heartbeat.schema_version = SCHEMA_VERSION
    heartbeat.cadence_mode = CADENCE_MODE
    heartbeat.session_status = SESSION_STATUS_STARTED
    record = heartbeat.to_record()
    _append_jsonl(directory / LOG_FILENAME, record)
    _write_json(directory / HEARTBEAT_FILENAME, record)
    return record


def latest(lane: str, root: str | Path | None = None) -> dict | None:
    """The most recent durable heartbeat record for a lane (from the ledger)."""
    log = read_log(lane, root)
    return log[-1] if log else None


# --------------------------------------------------------------------------- #
# Optional Issue #3 visibility. Best-effort ONLY: it must never gate, delay or
# invalidate the durable heartbeat above, and it never fabricates a comment.
# --------------------------------------------------------------------------- #
def issue_comment_body(record: dict) -> str:
    """Concise human-readable session-start line for the Issue #3 progress feed."""
    parts = [
        f"**Session heartbeat** ({CADENCE_MODE}) — lane `{record.get('lane')}`",
        "",
        f"- session_id: `{record.get('session_id')}`",
        f"- branch: `{record.get('branch')}`",
        f"- started_at: {record.get('started_at')}",
        f"- current_artifact: {record.get('current_artifact')}",
        f"- canonical_seen_sha: `{record.get('canonical_seen_sha')}`",
        f"- lead_review_seen: {record.get('lead_review_seen')}",
    ]
    if record.get("blocker"):
        parts.append(f"- blocker: {record['blocker']}")
    if record.get("notes"):
        parts.append(f"- notes: {record['notes']}")
    return "\n".join(parts)


ISSUE_POST_FILENAME = "HEARTBEAT_ISSUE_POSTS.jsonl"


def record_issue_post(record: dict, *, issue: int = 3, repo: str | None = None,
                      root: str | Path | None = None, runner=None) -> dict:
    """Attempt the visibility comment AFTER the durable write, and log the result.

    The durable ledger is append-only and must not be rewritten, so the outcome
    of the post goes in a sidecar ledger beside it. This ordering matters: an
    earlier version posted first, so a refused duplicate heartbeat still produced
    an Issue comment announcing a heartbeat that was never written.
    """
    posted, reason = post_issue_comment(record, issue=issue, repo=repo, runner=runner)
    row = {
        "session_id": record.get("session_id"),
        "lane": record.get("lane"),
        "attempted_at": now_iso(),
        "issue": issue,
        "posted": posted,
        "skipped_reason": reason,
        "note": ("visibility only; the durable heartbeat in HEARTBEAT_LOG.jsonl is "
                 "the evidence and is never rewritten to match this"),
    }
    _append_jsonl(lane_dir(record["lane"], root) / ISSUE_POST_FILENAME, row)
    return row


def post_issue_comment(record: dict, issue: int = 3, repo: str | None = None,
                       runner=None) -> tuple[bool, str | None]:
    """Best-effort one-comment Issue visibility via ``gh``.

    Returns ``(posted, skipped_reason)``. Every failure path — ``gh`` absent, not
    authenticated, non-zero exit, exception — returns ``(False, reason)`` and is
    recorded truthfully. It never raises and never claims a comment it did not
    make. ``runner`` is an injection seam so tests exercise both paths without a
    network call.
    """
    import shutil
    import subprocess

    argv = ["gh", "issue", "comment", str(issue), "--body-file", "-"]
    if repo:
        argv += ["--repo", repo]
    body = issue_comment_body(record)

    if runner is None:
        if shutil.which("gh") is None:
            return False, "gh CLI not found on PATH"

        def runner(cmd, text):                        # noqa: ANN001 - local seam
            return subprocess.run(cmd, input=text, capture_output=True,
                                  text=True, timeout=60)

    try:
        proc = runner(argv, body)
    except Exception as exc:                          # noqa: BLE001 - never block work
        return False, f"gh invocation failed: {type(exc).__name__}"
    if getattr(proc, "returncode", 1) != 0:
        detail = (getattr(proc, "stderr", "") or "").strip().splitlines()
        return False, f"gh exit {proc.returncode}: {detail[-1][:160] if detail else 'no stderr'}"
    return True, None
