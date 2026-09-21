"""Bounded, resumable, no-overlap Claude worker.

Executes ONE bounded work unit per invocation:
  1. read coordination/work state;
  2. acquire exactly one atomic task lease (reject overlap);
  3. do useful work (one autonomy cycle);
  4. verify the result;
  5. write a sanitized receipt;
  6. update heartbeat + state from the *actual* process;
  7. release/renew the lease;
  8. exit cleanly.

It never keeps an expensive model conversation alive doing nothing. A scheduler
entry is not proof this ran — only the receipts + heartbeat this code writes are.
"""
from __future__ import annotations

import os
import socket
import uuid

from . import leasing, receipts, decision
from .heartbeat import Heartbeat
from .jsonstore import now_iso


def _worker_id() -> str:
    return f"w-{socket.gethostname()[:8]}-{os.getpid()}-{uuid.uuid4().hex[:6]}"


def runtime_task_id(bot: str) -> str:
    """Lease key for a runtime cycle.

    The exclusion boundary is the RUNTIME (bot), NOT the (bot, persona) pair.
    A runtime's SHARED ``bot_state.json`` (process/health counters, recovery,
    observation fingerprint) is written by every persona cycle on that runtime,
    so two personas on one runtime must not mutate it concurrently. Keying the
    lease by ``bot`` means a second persona-cycle on the same runtime is rejected
    (no-overlap) while one is in flight — one writer per runtime state at a time.
    Each persona also keeps its own PRIVATE ``persona-<id>.json`` (consumed-signal
    ledger, hypotheses, working set) and isolated experiment/content/memory
    *namespaces*; serializing on the runtime protects the shared file and keeps
    the per-persona files single-writer too (SB-V03-005).
    """
    return f"cycle:{bot}"


def run_one_unit(task_id: str, bot: str, persona_id: str, *,
                 host_alias: str = "local", worker_id: str | None = None,
                 ttl_seconds: int = 120, source_ref: str = "social-bots/runtime") -> dict:
    """Run a single bounded unit. Returns a summary dict.

    Raises ``leasing.LeaseHeld`` if another live worker owns the task — callers
    treat that as the no-overlap rejection (choose another task or exit).
    """
    worker_id = worker_id or _worker_id()
    hb = Heartbeat(worker_id=worker_id, host_alias=host_alias, source_ref=source_ref)
    hb.beat(status="starting", current_task_id=task_id, next_safe_action="acquire_lease")

    # (2) acquire lease atomically; overlap raises LeaseHeld to the caller.
    lease = leasing.acquire(task_id, worker_id, host_alias, ttl_seconds)
    fence = leasing.Fence(lease)   # active-cycle ownership guard (fencing token)
    hb.beat(status="leased", lease_id=lease.lease_id,
            next_safe_action="reconcile_or_work" if lease.reconcile_required else "work")

    start = receipts.write_receipt(
        bot, "start", task_id, worker_id, lease.lease_id,
        {"persona": persona_id, "fence_generation": lease.generation,
         "took_over_from": lease.took_over_from,
         "reconcile_required": lease.reconcile_required, "started_at": now_iso()})

    try:
        # (2b) reconcile prior owner's uncertain external effects before new work.
        reconciled = None
        if lease.reconcile_required:
            reconciled = _reconcile(bot)
            hb.beat(status="reconciled", next_safe_action="work")

        # (3) useful work: one autonomy cycle. Renew lease around the work, and
        # pass the fence so the cycle's durable commit is refused if this worker
        # loses ownership (lease expiry + takeover) before it commits.
        leasing.renew(lease)
        hb.beat(status="working", next_safe_action="verify")
        record = decision.run_cycle(bot, persona_id, fence=fence)

        # (4) verify already embedded in the decision record.
        verified = bool(record.get("verify", {}).get("verified"))
        outcome = record.get("outcome", "no_action")
        withheld = bool(record.get("verify", {}).get("withheld"))

        # (5) finish receipt — records the TRUTHFUL outcome. A withheld candidate
        # produces a withheld receipt, never a success one.
        fin = receipts.write_receipt(
            bot, "finish", task_id, worker_id, lease.lease_id,
            {"persona": persona_id, "cycle": record.get("cycle"),
             "fence_generation": lease.generation,
             "chosen_action": record.get("chosen", {}).get("action"),
             "provider_recommended": record.get("policy", {}).get("provider_recommended"),
             "policy_selected": record.get("policy", {}).get("policy_selected"),
             "outcome": outcome, "withheld": withheld,
             "candidate_succeeded": outcome == "candidate_created",
             "verified": verified, "reconciled": reconciled})

        # (6) heartbeat from the actual process.
        hb.beat(status="done", last_receipt=os.path.basename(fin),
                next_safe_action="release_lease")

        # (7) release the lease.
        released = leasing.release(lease)
        return {"worker_id": worker_id, "task_id": task_id, "bot": bot,
                "persona": persona_id, "lease_id": lease.lease_id,
                "took_over_from": lease.took_over_from,
                "chosen_action": record.get("chosen", {}).get("action"),
                "outcome": outcome, "withheld": withheld,
                "verified": verified, "lease_released": released,
                "start_receipt": os.path.basename(start),
                "finish_receipt": os.path.basename(fin),
                "heartbeat_beats": hb.beats}
    except leasing.FenceLost as exc:
        # Lost the fence mid-cycle (lease expired + another worker took over).
        # Stand down truthfully: NO durable success was committed by us, and we
        # must NOT delete the new owner's lease. The receipt records fence loss,
        # never candidate success.
        receipts.write_receipt(
            bot, "failure", task_id, worker_id, lease.lease_id,
            {"persona": persona_id, "outcome": "fence_lost",
             "candidate_succeeded": False,
             "fence_generation": lease.generation,
             "on_disk_generation": (exc.on_disk or {}).get("generation"),
             "on_disk_owner": (exc.on_disk or {}).get("worker_id"),
             "detail": "lease expired during active cycle; another worker took "
                       "over; this worker committed nothing"})
        hb.beat(status="fenced_out", next_safe_action="exit")
        released = leasing.release(lease)  # no-op: release only removes OUR lease
        return {"worker_id": worker_id, "task_id": task_id, "bot": bot,
                "persona": persona_id, "lease_id": lease.lease_id,
                "fence_generation": lease.generation,
                "outcome": "fence_lost", "withheld": False, "verified": False,
                "committed": False, "lease_released": released,
                "took_over_by_generation": (exc.on_disk or {}).get("generation"),
                "start_receipt": os.path.basename(start),
                "heartbeat_beats": hb.beats}
    except Exception as exc:  # noqa: BLE001 — record any failure as a receipt.
        receipts.write_receipt(
            bot, "failure", task_id, worker_id, lease.lease_id,
            {"persona": persona_id, "error_type": type(exc).__name__, "error": str(exc)[:300]})
        hb.beat(status="failed", next_safe_action="release_lease")
        leasing.release(lease)
        raise


def _reconcile(bot: str) -> dict:
    """External-effect reconciliation stub with a real, honest check.

    Because publishing is disabled, the only external-effect surface is the
    (unpublished) publish queue. We assert nothing was published without
    authorization, then declare the takeover safe.
    """
    from . import pipeline
    q = pipeline.publish_queue(bot)
    unauthorized_published = [e for e in q if e.get("published") and not e.get("publish_authorized")]
    return {"queue_items": len(q),
            "unauthorized_published": len(unauthorized_published),
            "safe": len(unauthorized_published) == 0}
