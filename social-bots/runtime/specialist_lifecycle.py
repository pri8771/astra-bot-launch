"""SB-S23-008 — specialist lifecycle: CREATE -> ASSIGN -> RUN -> RETURN -> VERIFY
-> ADOPT/REJECT -> RETIRE, with a lease per worker and concurrent execution.

``run_specialist`` composes the V2.3 specialist slices into one bounded
lifecycle (``V20_TO_V23_IMPLEMENTATION_SPEC.md`` §5 S23-008 row):

CREATE   validate_contract; SpawnGuard.assert_depth; refuse a worker id that
         already has a receipt or kept evidence (never reused); acquire
         ``leasing.acquire("specialist:<worker_id>")``; ``Sandbox.create``.
ASSIGN   materialize bounded context through the resolver; copy parent-supplied
         ``inputs`` into ``inputs/``. A ContextError => the adapter never runs.
RUN      ``adapter.run(contract, sandbox, provider=BudgetedProvider|None,
         deadline=Deadline(contract), ledger=WorkerLedger)``. An adapter that
         raises (including EffectDenied / ChildSpawnDenied / SandboxEscape)
         yields a synthetic FAILED result carrying the ledger's truthful counts.
RETURN   the WorkerResult is written to ``outputs/RESULT.json`` in scratch.
VERIFY   ``specialist_integrator.verify``.
ADOPT    ``specialist_integrator.adopt`` (fenced when a fence is given) or
REJECT   ``specialist_integrator.reject`` on any verify error / stage failure.
RETIRE   scratch retired inside adopt/reject; lease released; the record says
         whether ``leasing.inspect`` shows the lease gone.

Any stage failure => decision REJECTED, failure receipt, scratch retired with
``keep=[]``, lease released; parent state is never touched. ``run_concurrent``
runs independent lifecycles on a bounded thread pool (in-process; separate
process pools are a V3 option). Deterministic adapters only; a provider is
optional and must already be a ``BudgetedProvider``.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field, asdict
from typing import Any

from . import leasing, paths
from .jsonstore import now_iso, read_jsonl
from .specialist_budget import BudgetedProvider, Deadline, SpawnGuard, WorkerLedger, \
    ChildSpawnDenied
from .specialist_contract import WorkerContract, WorkerResult, validate_contract
from .specialist_integrator import IntegrationError, adopt, reject, verify
from .specialist_sandbox import (ContextError, DictContextResolver, Sandbox, SandboxError,
                                 kept_dir)

DEFAULT_MAX_WORKERS = 3          # matches planner_limits.max_workers default (spec §4)
ADOPTED, REJECTED = "ADOPTED", "REJECTED"
STAGES = ("CREATE", "ASSIGN", "RUN", "RETURN", "VERIFY", "ADOPT", "REJECT", "RETIRE")


class LifecycleError(Exception):
    pass


class WorkerIdReused(LifecycleError):
    pass


@dataclass
class LifecycleRecord:
    worker_id: str
    parent_run_id: str
    bot: str
    persona: str
    role: str
    stages: list = field(default_factory=list)
    decision: str | None = None
    receipt_ref: str | None = None
    cleanup_status: str | None = None
    lease_released: bool = False
    lease_gone: bool = False
    verify_errors: list = field(default_factory=list)
    result: dict | None = None
    started_at: str = field(default_factory=now_iso)
    finished_at: str | None = None
    schema_version: int = 1

    def stage(self, name: str, ok: bool, detail: str = "") -> None:
        self.stages.append({"stage": name, "at": now_iso(), "ok": ok, "detail": detail})

    def as_dict(self) -> dict:
        return asdict(self)


def lease_task_id(contract: WorkerContract) -> str:
    return f"specialist:{contract.worker_id}"


def worker_id_already_used(contract: WorkerContract) -> bool:
    """True when this worker id already left durable traces (kept evidence or a
    receipt). A retired worker id is never reused for a second lifecycle."""
    if kept_dir(contract).exists():
        return True
    idx = paths.receipts_dir(contract.bot) / "index.jsonl"
    task = lease_task_id(contract)
    return any(row.get("task_id") == task for row in read_jsonl(idx))


def _synthetic_failed(contract: WorkerContract, ledger: WorkerLedger, started: str, state: str,
                      error: str, source_ref: str) -> WorkerResult:
    return WorkerResult(
        worker_id=contract.worker_id, parent_run_id=contract.parent_run_id, bot=contract.bot,
        persona=contract.persona, role=contract.role, started_at=started, finished_at=now_iso(),
        source_ref=source_ref, result=state, outputs=[], evidence_refs=[],
        calls_used=ledger.calls_used, effect_attempts=ledger.effect_attempts,
        limitations=["lifecycle: adapter did not return a result"], cleanup_status="PENDING",
        provenance=contract.provenance, error=error)


def run_specialist(contract: WorkerContract, adapter: Any, *, resolver=None, provider=None,
                   inputs: dict[str, Any] | None = None, adapter_kwargs: dict | None = None,
                   lease: bool = True, fence=None, integrator_keep: list[str] | None = None,
                   deadline: Deadline | None = None, host_alias: str = "local",
                   source_ref: str = "runtime.specialist_lifecycle/1") -> LifecycleRecord:
    rec = LifecycleRecord(worker_id=getattr(contract, "worker_id", "?"),
                          parent_run_id=getattr(contract, "parent_run_id", "?"),
                          bot=getattr(contract, "bot", "?"), persona=getattr(contract, "persona", "?"),
                          role=getattr(contract, "role", "?"))
    held: leasing.Lease | None = None
    sandbox: Sandbox | None = None

    def release_lease() -> None:
        nonlocal held
        if held is not None:
            rec.lease_released = bool(leasing.release(held))
            held = None
        on_disk = leasing.inspect(lease_task_id(contract)) if isinstance(contract, WorkerContract) else None
        rec.lease_gone = on_disk is None or leasing.is_stale(on_disk)

    # ---------------- CREATE ----------------
    errs = validate_contract(contract)
    if errs:
        rec.stage("CREATE", False, "invalid contract: " + "; ".join(errs))
        rec.decision, rec.finished_at = REJECTED, now_iso()
        return rec
    try:
        SpawnGuard.assert_depth(contract)
        if worker_id_already_used(contract):
            raise WorkerIdReused(f"worker id {contract.worker_id} already has durable traces")
        if provider is not None and (not isinstance(provider, BudgetedProvider)
                                     or provider.contract.worker_id != contract.worker_id):
            raise LifecycleError("provider must be a BudgetedProvider for this worker")
        if lease:
            held = leasing.acquire(lease_task_id(contract), contract.parent_run_id,
                                   host_alias=host_alias,
                                   ttl_seconds=max(60, int(contract.time_budget_s) + 60))
        sandbox = Sandbox(contract)
        sandbox.create()
        rec.stage("CREATE", True, f"scratch {sandbox.root.name}; lease={'held' if held else 'none'}")
    except (ChildSpawnDenied, WorkerIdReused, LifecycleError, leasing.LeaseError, SandboxError) as exc:
        rec.stage("CREATE", False, f"{type(exc).__name__}: {exc}")
        if sandbox is not None and sandbox.status == "PENDING" and sandbox.root.exists():
            sandbox.retire(keep=[])
        release_lease()
        rec.decision, rec.finished_at = REJECTED, now_iso()
        return rec

    ledger = provider.ledger if provider is not None else WorkerLedger.for_contract(contract)
    started = now_iso()
    result: WorkerResult | None = None

    # ---------------- ASSIGN ----------------
    try:
        materialized = sandbox.materialize_context(resolver or DictContextResolver({}))
        for rel, data in (inputs or {}).items():
            sandbox.write(f"inputs/{rel}", data)
        rec.stage("ASSIGN", True, f"context refs: {len(materialized)}; inputs: {len(inputs or {})}")
    except (ContextError, SandboxError) as exc:
        rec.stage("ASSIGN", False, f"{type(exc).__name__}: {exc}")
        result = _synthetic_failed(contract, ledger, started, "FAILED",
                                   f"assign failed: {type(exc).__name__}: {exc}", source_ref)

    # ---------------- RUN ----------------
    if result is None:
        try:
            result = adapter.run(contract, sandbox, provider=provider,
                                 deadline=deadline or Deadline(contract), ledger=ledger,
                                 **(adapter_kwargs or {}))
            if not isinstance(result, WorkerResult):
                raise LifecycleError(f"adapter returned {type(result).__name__}, not WorkerResult")
            rec.stage("RUN", result.result == "COMPLETED", f"result={result.result}")
        except Exception as exc:                          # noqa: BLE001 - every fault is recorded
            rec.stage("RUN", False, f"{type(exc).__name__}: {exc}")
            result = _synthetic_failed(contract, ledger, started, "FAILED",
                                       f"adapter raised {type(exc).__name__}: {exc}", source_ref)

    # ---------------- RETURN ----------------
    try:
        sandbox.write("outputs/RESULT.json", result.as_dict())
        rec.stage("RETURN", True, "outputs/RESULT.json")
    except SandboxError as exc:
        rec.stage("RETURN", False, f"{type(exc).__name__}: {exc}")
    rec.result = result.as_dict()

    # ---------------- VERIFY ----------------
    errs = verify(result, contract, sandbox)
    rec.verify_errors = list(errs)
    rec.stage("VERIFY", not errs, "; ".join(errs) if errs else "ok")

    # ---------------- ADOPT / REJECT ----------------
    if not errs:
        try:
            receipt = adopt(result, contract, sandbox, bot=contract.bot, persona=contract.persona,
                            fence=fence, keep=integrator_keep)
            rec.decision, rec.receipt_ref = ADOPTED, receipt.receipt_path
            rec.stage("ADOPT", True, receipt.receipt_path)
        except (IntegrationError, leasing.FenceLost, SandboxError) as exc:
            rec.stage("ADOPT", False, f"{type(exc).__name__}: {exc}")
            errs = [f"adopt failed: {type(exc).__name__}: {exc}"]
    if errs and rec.decision is None:
        try:
            rej = reject(result, contract, sandbox, errs)
            rec.decision, rec.receipt_ref = REJECTED, rej.receipt_path
            rec.stage("REJECT", True, rej.receipt_path)
        except (IntegrationError, SandboxError) as exc:
            rec.decision = REJECTED
            rec.stage("REJECT", False, f"{type(exc).__name__}: {exc}")

    # ---------------- RETIRE ----------------
    if sandbox.status == "PENDING" and sandbox.root.exists():
        sandbox.retire(keep=[])
    rec.cleanup_status = sandbox.status
    release_lease()
    rec.stage("RETIRE", sandbox.status == "RETIRED" and rec.lease_gone,
              f"cleanup={sandbox.status}; lease_gone={rec.lease_gone}")
    rec.finished_at = now_iso()
    return rec


def run_concurrent(jobs: list[dict], *, max_workers: int = DEFAULT_MAX_WORKERS,
                   **common) -> list[LifecycleRecord]:
    """Run independent lifecycles on a bounded thread pool.

    Each job is ``{"contract": ..., "adapter": ..., "resolver"?, "provider"?,
    "inputs"?, "adapter_kwargs"?, "deadline"?}``. Results keep job order.
    """
    # Hard cap at DEFAULT_MAX_WORKERS (planner_limits default); a caller can only narrow.
    workers = max(1, min(int(max_workers or DEFAULT_MAX_WORKERS), DEFAULT_MAX_WORKERS))

    def one(job: dict) -> LifecycleRecord:
        kw = {**common, **{k: v for k, v in job.items() if k not in ("contract", "adapter")}}
        return run_specialist(job["contract"], job["adapter"], **kw)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(one, jobs))
