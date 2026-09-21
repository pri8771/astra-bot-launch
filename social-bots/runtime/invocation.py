"""SB-V07-001 — per-invocation receipts for OS-scheduled bounded worker sessions.

The V0.7 liveness argument is a SEQUENCE of independently scheduled, bounded
worker sessions — never a chat kept awake. Each invocation must leave two
independent durable traces:

* one ``SESSION_ONCE`` heartbeat (``runtime.session_heartbeat``), and
* one **invocation receipt**, written here.

The two answer different questions. The heartbeat says *a session started and
read current coordination*. The receipt says *what that invocation actually did*:
which task it claimed (or why it claimed none), what the bounded unit decided,
how long it took, and the exit code the scheduler will see.

Crash behaviour is the point of the two-phase write
---------------------------------------------------
``open_invocation`` writes an ``incomplete`` receipt BEFORE any work, and
``close_invocation`` rewrites it as terminal. A process killed mid-unit therefore
leaves a receipt that truthfully says ``status: "incomplete"`` rather than leaving
no trace at all or, worse, a success record. Counting only terminal receipts is
what makes "N real invocations happened" a checkable claim: an incomplete receipt
is visible evidence of a crash, and a restart writes a NEW invocation id rather
than reusing the dead one.

A receipt records outcomes; it never grants authority and never asserts
acceptance. ``live_model_call`` is recorded on every receipt and is ``False`` for
all V0.7 host engineering, so a reader can confirm no spend occurred.
"""
from __future__ import annotations

import json
import os
import platform
import socket
import time
import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1

# How a task claim ended. Each is a legitimate, non-failure outcome except the
# last: a scheduler must not treat no-overlap or halt as an error.
CLAIM_CLAIMED = "claimed"
CLAIM_NO_OVERLAP = "no_overlap"          # every candidate was held by a live worker
CLAIM_NONE_AVAILABLE = "none_available"  # no candidate tasks were configured
CLAIM_HALTED = "halted_by_direction"     # lead direction told this lane to stand down
CLAIM_ERROR = "error"

STATUS_INCOMPLETE = "incomplete"
STATUS_COMPLETE = "complete"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def invocations_dir(home: str | Path | None = None) -> Path:
    """Durable invocation-receipt directory under the runtime data root."""
    base = Path(home) if home is not None else Path(
        os.environ.get("SBOTS_HOME", str(Path(__file__).resolve().parent.parent)))
    d = base / "invocations"
    d.mkdir(parents=True, exist_ok=True)
    return d


def new_invocation_id() -> str:
    return (datetime.now(timezone.utc).strftime("inv-%Y%m%dT%H%M%SZ-")
            + uuid.uuid4().hex[:8])


def scheduler_hint() -> str:
    """Best-effort, non-secret guess at what launched this process.

    Only well-known scheduler marker variables are inspected, and only for
    presence. Values are never read or recorded. ``unknown`` is a normal and
    honest answer — this is a convenience label, not evidence.
    """
    markers = (
        ("systemd", ("INVOCATION_ID", "JOURNAL_STREAM")),
        ("launchd", ("XPC_SERVICE_NAME",)),
        ("windows-task-scheduler", ("SBOTS_SCHEDULER_WINDOWS",)),
        ("manual-or-shell", ("SBOTS_SCHEDULER_MANUAL",)),
    )
    for name, env_names in markers:
        if any(os.environ.get(e) for e in env_names):
            return name
    return "unknown"


def runtime_identity() -> dict:
    try:
        host = socket.gethostname()
    except OSError:                                   # pragma: no cover - defensive
        host = "unknown"
    return {
        "host": host[:64],
        "platform": platform.system(),
        "platform_release": platform.release()[:64],
        "python": platform.python_version(),
        "pid": os.getpid(),
    }


@dataclass
class InvocationReceipt:
    invocation_id: str
    session_id: str
    lane: str
    branch: str
    started_at: str
    schema_version: int = SCHEMA_VERSION
    status: str = STATUS_INCOMPLETE
    scheduler: str = field(default_factory=scheduler_hint)
    runtime: dict = field(default_factory=runtime_identity)
    direction_id: str | None = None
    direction_source: str | None = None
    canonical_sha: str | None = None
    heartbeat_emitted: bool = False
    claim_outcome: str | None = None
    claimed_task: str | None = None
    claimed_bot: str | None = None
    candidates_tried: list = field(default_factory=list)
    work_outcome: str | None = None
    work_summary: dict = field(default_factory=dict)
    finished_at: str | None = None
    duration_seconds: float | None = None
    exit_code: int | None = None
    live_model_call: bool = False
    error: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, sort_keys=True, ensure_ascii=False)
        fh.write("\n")
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def _append_index(directory: Path, row: dict) -> None:
    path = directory / "index.jsonl"
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


class Invocation:
    """Two-phase invocation receipt: written incomplete, finalized on exit."""

    def __init__(self, receipt: InvocationReceipt, home: str | Path | None = None):
        self.receipt = receipt
        self.dir = invocations_dir(home)
        self._monotonic_start = time.monotonic()

    @property
    def path(self) -> Path:
        return self.dir / f"{self.receipt.invocation_id}.json"

    def open(self) -> "Invocation":
        _write_json(self.path, self.receipt.to_dict())
        _append_index(self.dir, {
            "invocation_id": self.receipt.invocation_id,
            "session_id": self.receipt.session_id,
            "lane": self.receipt.lane,
            "phase": "open",
            "recorded_at": self.receipt.started_at,
        })
        return self

    def update(self, **fields) -> "Invocation":
        for key, value in fields.items():
            setattr(self.receipt, key, value)
        return self

    def close(self, *, exit_code: int, error: str | None = None) -> dict:
        self.receipt.status = STATUS_COMPLETE
        self.receipt.exit_code = exit_code
        self.receipt.error = error
        self.receipt.finished_at = _now_iso()
        self.receipt.duration_seconds = round(time.monotonic() - self._monotonic_start, 3)
        data = self.receipt.to_dict()
        _write_json(self.path, data)
        _append_index(self.dir, {
            "invocation_id": self.receipt.invocation_id,
            "session_id": self.receipt.session_id,
            "lane": self.receipt.lane,
            "phase": "close",
            "status": self.receipt.status,
            "claim_outcome": self.receipt.claim_outcome,
            "work_outcome": self.receipt.work_outcome,
            "exit_code": exit_code,
            "recorded_at": self.receipt.finished_at,
        })
        return data


def start(*, session_id: str, lane: str, branch: str,
          home: str | Path | None = None, **fields) -> Invocation:
    """Open a new invocation receipt for this bounded session."""
    receipt = InvocationReceipt(
        invocation_id=new_invocation_id(), session_id=session_id, lane=lane,
        branch=branch, started_at=_now_iso(), **fields)
    return Invocation(receipt, home=home).open()


def read_all(home: str | Path | None = None) -> list[dict]:
    directory = invocations_dir(home)
    out: list[dict] = []
    for p in sorted(directory.glob("inv-*.json")):
        try:
            out.append(json.loads(p.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            out.append({"invocation_file": p.name, "unreadable": True})
    return out


def audit(home: str | Path | None = None) -> dict:
    """Truthful counts across all recorded invocations on this host.

    ``incomplete`` is reported rather than hidden: it is the durable signature of
    a crashed or killed invocation, and V0.7 crash/restart behaviour is proven by
    showing those records alongside the restart that followed.
    """
    rows = read_all(home)
    complete = [r for r in rows if r.get("status") == STATUS_COMPLETE]
    incomplete = [r for r in rows if r.get("status") == STATUS_INCOMPLETE]
    sessions = {r.get("session_id") for r in rows if r.get("session_id")}
    return {
        "total_invocations": len(rows),
        "complete": len(complete),
        "incomplete": len(incomplete),
        "distinct_sessions": len(sessions),
        "claims": {
            outcome: sum(1 for r in complete if r.get("claim_outcome") == outcome)
            for outcome in (CLAIM_CLAIMED, CLAIM_NO_OVERLAP, CLAIM_NONE_AVAILABLE,
                            CLAIM_HALTED, CLAIM_ERROR)
        },
        "live_model_calls": sum(1 for r in rows if r.get("live_model_call")),
        "note": ("one bounded session per invocation; recurring liveness is the "
                 "sequence of independently scheduled invocations, not this count "
                 "on its own"),
    }
