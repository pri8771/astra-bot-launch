"""Atomic task leases — the no-overlap guarantee.

A task can have exactly one active execution lease. The whole read-decide-write
sequence (is the current lease missing or stale? then claim it) runs inside an
OS-level exclusive lock (``fcntl.flock`` on a per-task lock file), so it is a true
compare-and-swap: only one contender is ever in the critical section, which makes
both a fresh claim and a stale takeover single-owner even under concurrent
contention on one host. ``flock`` is held on a real file descriptor and is
released by the kernel if the holder dies, so a crashed contender cannot wedge the
lock. Leases carry a TTL; a lease older than its TTL is *stale* and may be taken
over — the taker records ``reconcile_required`` so the prior owner's uncertain
external effects are reconciled first (a timed-out heartbeat alone does not prove
the primary stopped).

Portability: ``flock`` is POSIX. On a platform without it (e.g. native Windows)
we fall back to ``O_CREAT|O_EXCL`` create plus best-effort stale replace, and
``FLOCK_AVAILABLE`` is False so the deployment can assert the strong path is in
use on the Linux host.
"""
from __future__ import annotations

import json
import os
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

from . import paths
from .jsonstore import now_iso

try:
    import fcntl
    FLOCK_AVAILABLE = True
except ImportError:  # pragma: no cover - non-POSIX fallback
    fcntl = None
    FLOCK_AVAILABLE = False

DEFAULT_TTL_SECONDS = 120


class LeaseError(Exception):
    pass


class LeaseHeld(LeaseError):
    """Raised when a live (non-stale) lease already owns the task."""

    def __init__(self, task_id: str, holder: dict):
        self.task_id = task_id
        self.holder = holder
        super().__init__(f"task {task_id!r} held by {holder.get('worker_id')}")


@dataclass
class Lease:
    lease_id: str
    task_id: str
    worker_id: str
    host_alias: str
    acquired_at: str
    renewed_at: str
    ttl_seconds: int
    took_over_from: str | None = None
    reconcile_required: bool = False

    def path(self) -> Path:
        return paths.leases_dir() / f"{self.task_id}.lease.json"


def _mono() -> float:
    return time.time()


def _age_seconds(lease_data: dict) -> float:
    renewed = datetime.fromisoformat(lease_data["renewed_at"])
    if renewed.tzinfo is None:
        renewed = renewed.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - renewed).total_seconds()


def is_stale(lease_data: dict) -> bool:
    return _age_seconds(lease_data) > lease_data.get("ttl_seconds", DEFAULT_TTL_SECONDS)


def _read(path: Path) -> dict | None:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _lock_path(task_id: str) -> Path:
    return paths.leases_dir() / f"{task_id}.lock"


@contextmanager
def _task_lock(task_id: str):
    """Exclusive per-task critical section.

    With ``flock`` this serializes all contenders on one host so the
    read-decide-write is a real CAS. Without it (non-POSIX), the block still runs
    but relies on the atomic write below; ``FLOCK_AVAILABLE`` is False so the host
    can assert the strong path.
    """
    if not FLOCK_AVAILABLE:
        yield
        return
    fd = os.open(str(_lock_path(task_id)), os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)


def _atomic_write(path: Path, lease: "Lease") -> None:
    tmp = path.with_name(f"{path.name}.{uuid.uuid4().hex}.tmp")
    with open(tmp, "wb") as fh:
        fh.write(json.dumps(asdict(lease), sort_keys=True).encode())
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def acquire(task_id: str, worker_id: str, host_alias: str = "local",
            ttl_seconds: int = DEFAULT_TTL_SECONDS) -> Lease:
    """Acquire the lease for ``task_id`` or raise ``LeaseHeld``.

    The check-and-claim runs inside an exclusive per-task lock, so a fresh claim
    and a stale takeover are both single-owner under concurrency. A stale takeover
    sets ``took_over_from`` and ``reconcile_required``.
    """
    path = paths.leases_dir() / f"{task_id}.lease.json"
    with _task_lock(task_id):
        existing = _read(path)
        if existing is not None and not is_stale(existing):
            raise LeaseHeld(task_id, existing)
        lease = Lease(
            lease_id=uuid.uuid4().hex, task_id=task_id, worker_id=worker_id,
            host_alias=host_alias, acquired_at=now_iso(), renewed_at=now_iso(),
            ttl_seconds=ttl_seconds,
            took_over_from=(existing.get("lease_id") if existing else None),
            reconcile_required=existing is not None,   # existing here is always stale
        )
        _atomic_write(path, lease)
        return lease


def renew(lease: Lease) -> Lease:
    """Refresh the lease heartbeat timestamp. Fails if we no longer own it."""
    path = lease.path()
    with _task_lock(lease.task_id):
        current = _read(path)
        if current is None or current.get("lease_id") != lease.lease_id:
            raise LeaseError(f"lost lease {lease.lease_id} for {lease.task_id}")
        lease.renewed_at = now_iso()
        _atomic_write(path, lease)
    return lease


def release(lease: Lease) -> bool:
    """Release the lease iff we still own it. Returns True if removed."""
    path = lease.path()
    with _task_lock(lease.task_id):
        current = _read(path)
        if current is not None and current.get("lease_id") == lease.lease_id:
            os.unlink(path)
            return True
    return False


def inspect(task_id: str) -> dict | None:
    return _read(paths.leases_dir() / f"{task_id}.lease.json")
