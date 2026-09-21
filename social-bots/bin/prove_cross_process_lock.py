#!/usr/bin/env python3
"""Prove the lease/fence lock is exclusive across REAL OS PROCESSES.

The fencing unit tests run in one process with threads. This harness spawns
independent OS processes (``multiprocessing`` with the 'spawn' start method, so
each child is a fresh interpreter — not a shared-memory thread) that all contend
for the SAME task lease at the same instant. The guarantee under test:

  - exactly ONE process acquires the lease (single owner), and
  - every other process is rejected with ``LeaseHeld`` (no double ownership),
  - proven with ``fcntl.flock`` — the strong single-POSIX-host path.

This is genuine cross-process evidence, not a thread simulation. No network, no
external effect, no spend. Prints a JSON verdict to stdout; exit 0 iff the
single-owner invariant held.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _contend(task_id: str, worker_id: str, home: str, barrier, q) -> None:
    # Fresh interpreter (spawn): import inside the child and point at the shared home.
    os.environ["SBOTS_HOME"] = home
    from runtime import leasing  # noqa: E402
    barrier.wait()  # release all contenders as simultaneously as the OS allows
    try:
        lease = leasing.acquire(task_id, worker_id, ttl_seconds=300)
        q.put(("acquired", worker_id, lease.lease_id, lease.generation))
    except leasing.LeaseHeld:
        q.put(("held", worker_id, None, None))
    except Exception as exc:  # noqa: BLE001
        q.put(("error", worker_id, type(exc).__name__, str(exc)[:120]))


def run(n_processes: int = 8) -> dict:
    ctx = mp.get_context("spawn")
    home = tempfile.mkdtemp(prefix="sbots-xproc-")
    task_id = "cycle:social-a"
    barrier = ctx.Barrier(n_processes)
    q = ctx.Queue()
    procs = [ctx.Process(target=_contend,
                         args=(task_id, f"proc-{i}-{os.getpid()}", home, barrier, q))
             for i in range(n_processes)]
    for p in procs:
        p.start()
    for p in procs:
        p.join(timeout=30)

    results = []
    while not q.empty():
        results.append(q.get())
    acquired = [r for r in results if r[0] == "acquired"]
    held = [r for r in results if r[0] == "held"]
    errors = [r for r in results if r[0] == "error"]

    from runtime import leasing  # for FLOCK_AVAILABLE in the parent
    verdict = {
        "task_id": task_id,
        "processes_spawned": n_processes,
        "start_method": "spawn (independent interpreters)",
        "flock_available": leasing.FLOCK_AVAILABLE,
        "acquired_count": len(acquired),
        "held_count": len(held),
        "error_count": len(errors),
        "acquired_by": [r[1] for r in acquired],
        "errors": errors,
        # Single-owner invariant: exactly one acquired, the rest correctly rejected.
        "single_owner_ok": len(acquired) == 1 and len(errors) == 0
                           and len(held) == n_processes - 1,
    }
    return verdict


def main() -> int:
    verdict = run()
    print(json.dumps(verdict, indent=2, sort_keys=True))
    return 0 if verdict["single_owner_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
