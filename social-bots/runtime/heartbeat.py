"""Process heartbeat — liveness proven only by the actual running worker.

A scheduler entry, a cron line, or a Markdown file is NOT proof a worker runs
(AUTONOMY_CONTRACT.md). The heartbeat file is meaningful only because
``beat()`` is called from inside the live worker process, carrying its real pid.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, asdict, field
from pathlib import Path

from . import paths
from .jsonstore import write_json, read_json, now_iso


@dataclass
class Heartbeat:
    worker_id: str
    host_alias: str = "local"
    pid: int = field(default_factory=os.getpid)
    lease_id: str | None = None
    started_at: str = field(default_factory=now_iso)
    heartbeat_at: str = field(default_factory=now_iso)
    current_task_id: str | None = None
    source_ref: str | None = None
    status: str = "starting"
    last_receipt: str | None = None
    next_safe_action: str | None = None
    beats: int = 0

    def path(self) -> Path:
        return paths.base() / "heartbeats" / f"{self.worker_id}.json"

    def beat(self, **updates) -> "Heartbeat":
        for k, v in updates.items():
            setattr(self, k, v)
        self.heartbeat_at = now_iso()
        self.beats += 1
        p = self.path()
        p.parent.mkdir(parents=True, exist_ok=True)
        write_json(p, asdict(self))
        return self


def read_heartbeat(worker_id: str) -> dict | None:
    p = paths.base() / "heartbeats" / f"{worker_id}.json"
    return read_json(p, default=None)
