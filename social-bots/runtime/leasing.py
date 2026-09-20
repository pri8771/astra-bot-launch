"""Atomic task leases — the no-overlap guarantee.

A task can have exactly one active execution lease. Acquisition is atomic via
``open(..., O_CREAT | O_EXCL)`` on a single lease file, so two workers racing for
the same task cannot both win, even on the same host. Leases carry a TTL; a lease
older than its TTL is *stale* and may be taken over — but only after the caller
records that the previous owner's external effects need reconciliation
(``reconcile_required``), per the ACCOUNTS_CHANNELS lesson that a timed-out
heartbeat alone does not prove the primary stopped.
"""
from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

from . import paths
from .jsonstore import now_iso

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


def acquire(task_id: str, worker_id: str, host_alias: str = "local",
            ttl_seconds: int = DEFAULT_TTL_SECONDS) -> Lease:
    """Atomically acquire the lease for ``task_id`` or raise ``LeaseHeld``.

    A stale lease is taken over: the new lease records ``took_over_from`` and sets
    ``reconcile_required`` so the worker reconciles the prior owner's effects
    before producing new external effects.
    """
    path = paths.leases_dir() / f"{task_id}.lease.json"
    lease = Lease(
        lease_id=uuid.uuid4().hex,
        task_id=task_id,
        worker_id=worker_id,
        host_alias=host_alias,
        acquired_at=now_iso(),
        renewed_at=now_iso(),
        ttl_seconds=ttl_seconds,
    )
    payload = json.dumps(asdict(lease), sort_keys=True).encode()

    try:
        fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        with os.fdopen(fd, "wb") as fh:
            fh.write(payload)
            fh.flush()
            os.fsync(fh.fileno())
        return lease
    except FileExistsError:
        existing = _read(path)
        if existing is None:
            # Torn/partial file — treat as stale and retry once.
            existing = {"renewed_at": "1970-01-01T00:00:00+00:00", "ttl_seconds": 0}
        if not is_stale(existing):
            raise LeaseHeld(task_id, existing)
        # Stale takeover: overwrite atomically, fence the old owner.
        lease.took_over_from = existing.get("lease_id")
        lease.reconcile_required = True
        tmp = path.with_suffix(".takeover.tmp")
        with open(tmp, "wb") as fh:
            fh.write(json.dumps(asdict(lease), sort_keys=True).encode())
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
        return lease


def renew(lease: Lease) -> Lease:
    """Refresh the lease heartbeat timestamp. Fails if we no longer own it."""
    path = lease.path()
    current = _read(path)
    if current is None or current.get("lease_id") != lease.lease_id:
        raise LeaseError(f"lost lease {lease.lease_id} for {lease.task_id}")
    lease.renewed_at = now_iso()
    tmp = path.with_suffix(".renew.tmp")
    with open(tmp, "wb") as fh:
        fh.write(json.dumps(asdict(lease), sort_keys=True).encode())
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)
    return lease


def release(lease: Lease) -> bool:
    """Release the lease iff we still own it. Returns True if removed."""
    path = lease.path()
    current = _read(path)
    if current is not None and current.get("lease_id") == lease.lease_id:
        os.unlink(path)
        return True
    return False


def inspect(task_id: str) -> dict | None:
    return _read(paths.leases_dir() / f"{task_id}.lease.json")
