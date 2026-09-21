"""SB-S23-006 — parent result validator / integrator.

The parent runtime validates, accepts/rejects and integrates specialist outputs.
No child ever mutates parent private state; adoption is the ONLY path from a
specialist's scratch into a persona namespace, and it is a deterministic,
fenced, receipted copy (``V20_TO_V23_IMPLEMENTATION_SPEC.md`` §5 S23-006 row,
§0.6).

Pieces
------
``verify(result, contract, sandbox) -> list[str]``
    ``specialist_contract.validate_result`` plus: sandbox identity, result state
    adoptable (only ``COMPLETED``), context not failed, every declared output
    exists in scratch with a matching sha256 and a matching in-file ``schema``,
    a ``ReviewResult`` whose ``reviewed_sha256`` still matches the reviewed
    inputs (proof the reviewer changed nothing), a ``DraftResult`` whose
    candidate is ``DRAFT_UNPUBLISHED``. Any error => REJECT.
``adopt(result, contract, sandbox, *, bot, persona, fence=None, keep=None)``
    Precondition ``verify() == []`` and scope match, else ``IntegrationError``
    with nothing written. Inside one ``leasing.Fence.fenced_commit`` (when a
    fence is given): ``Sandbox.retire(keep=...)`` copies the kept outputs to
    ``receipts/<bot>/specialists/<worker_id>/`` with an ``INDEX.json``, then a
    sanitized receipt is written through ``runtime.receipts.write_receipt``.
    A lost fence runs none of it (scratch stays for a later ``reject``).
``reject(result, contract, sandbox, reasons)``
    Writes a failure receipt and retires the scratch with ``keep=[]``. Parent
    state is untouched; the only trace is the truthful receipt.
``integrate_into(kind, adopted)``
    Deterministic mapping table from an adopted output to a value the parent
    may use: ``ResearchResult/1`` -> evidence refs; ``DraftResult/1`` -> the
    candidate draft (status ``DRAFT_UNPUBLISHED`` preserved, else error);
    ``AnalysisResult/1`` / ``ReviewResult/1`` / ``MediaBriefResult/1`` -> a
    reference to the kept file only. It RETURNS a value; it never writes
    ``PersonaState`` / ``RuntimeState`` / content / experiments.

Receipt kinds
-------------
``runtime.receipts.write_receipt`` (Cursor-owned, unmodified) accepts only
``start|finish|failure``. Adoption uses ``finish`` and rejection ``failure``,
with ``detail["specialist"]`` carrying the decision; the receipt ``task_id`` is
``specialist:<worker_id>``, the same key SB-S23-008 leases.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

from . import receipts
from .jsonstore import now_iso
from .specialist_contract import WorkerContract, WorkerResult, validate_result
from .specialist_sandbox import Sandbox, SandboxError, kept_dir, INDEX_FILE

SCHEMA_VERSION = 1
DRAFT_UNPUBLISHED = "DRAFT_UNPUBLISHED"
ADOPTED, REJECTED = "ADOPTED", "REJECTED"
KNOWN_SCHEMAS = ("ResearchResult/1", "EvidenceCapture/1", "AnalysisResult/1", "ReviewResult/1",
                 "DraftResult/1", "MediaBriefResult/1")


class IntegrationError(Exception):
    pass


@dataclass(frozen=True)
class AdoptionReceipt:
    worker_id: str
    parent_run_id: str
    bot: str
    persona: str
    role: str
    decision: str
    receipt_path: str
    at: str
    outputs: list = field(default_factory=list)      # [{"schema","path","sha256","kept_path"}]
    evidence_refs: list = field(default_factory=list)
    reasons: list = field(default_factory=list)
    schema_version: int = SCHEMA_VERSION

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class RejectionReceipt:
    worker_id: str
    parent_run_id: str
    bot: str
    persona: str
    role: str
    decision: str
    receipt_path: str
    at: str
    reasons: list = field(default_factory=list)
    cleanup_status: str = "PENDING"
    schema_version: int = SCHEMA_VERSION

    def as_dict(self) -> dict:
        return asdict(self)


def _load_json(sandbox: Sandbox, rel: str) -> dict | None:
    try:
        doc = json.loads(sandbox.read(rel).decode("utf-8"))
    except (SandboxError, UnicodeDecodeError, ValueError):
        return None
    return doc if isinstance(doc, dict) else None


# --------------------------------------------------------------------------- #
# verify
# --------------------------------------------------------------------------- #
def verify(result: Any, contract: Any, sandbox: Any) -> list[str]:
    errs = validate_result(result, contract)
    if errs:
        return errs
    if not isinstance(sandbox, Sandbox):
        return ["sandbox is not a Sandbox"]
    if sandbox.contract.worker_id != contract.worker_id:
        return [f"sandbox belongs to {sandbox.contract.worker_id}, not {contract.worker_id}"]
    if result.result != "COMPLETED":
        errs.append(f"result state {result.result!r} is not adoptable")
    try:
        if sandbox.context_failed():
            errs.append("bounded context failed to materialize; result cannot be adopted")
    except SandboxError as exc:
        return errs + [f"sandbox unusable: {exc}"]

    for i, out in enumerate(result.outputs):
        rel = out["path"]
        try:
            actual = sandbox.sha256(rel)
        except SandboxError as exc:
            errs.append(f"outputs[{i}] {rel!r} is missing or escapes the sandbox: {exc}")
            continue
        if actual != out["sha256"]:
            errs.append(f"outputs[{i}] {rel!r} sha256 changed after it was declared")
            continue
        if not rel.endswith(".json"):
            continue
        doc = _load_json(sandbox, rel)
        if doc is None:
            errs.append(f"outputs[{i}] {rel!r} is not a JSON object")
            continue
        if doc.get("schema") != out["schema"]:
            errs.append(f"outputs[{i}] {rel!r} declares schema {out['schema']!r} but the file "
                        f"says {doc.get('schema')!r}")
            continue
        if doc.get("schema") == "ReviewResult/1":
            reviewed = doc.get("reviewed_sha256")
            if not isinstance(reviewed, dict):
                errs.append(f"outputs[{i}] ReviewResult has no reviewed_sha256")
            else:
                for path, digest in reviewed.items():
                    try:
                        now = sandbox.sha256(path)
                    except SandboxError:
                        errs.append(f"outputs[{i}] reviewed input {path!r} is gone")
                        continue
                    if now != digest:
                        errs.append(f"outputs[{i}] reviewed input {path!r} changed after review")
        if doc.get("schema") == "DraftResult/1":
            cand = doc.get("candidate")
            if not isinstance(cand, dict) or cand.get("status") != DRAFT_UNPUBLISHED:
                errs.append(f"outputs[{i}] DraftResult candidate is not {DRAFT_UNPUBLISHED}")
    return errs


# --------------------------------------------------------------------------- #
# adopt / reject
# --------------------------------------------------------------------------- #
def _run(fence, commit):
    return commit() if fence is None else fence.fenced_commit(commit)


def _detail(result: WorkerResult, contract: WorkerContract, decision: str, reasons: list[str],
            outputs: list[dict]) -> dict:
    return {
        "specialist": {
            "decision": decision, "worker_id": contract.worker_id,
            "parent_run_id": contract.parent_run_id, "bot": contract.bot,
            "persona": contract.persona, "role": contract.role,
            "objective": contract.objective, "result": result.result,
            "calls_used": result.calls_used, "effect_attempts": result.effect_attempts,
            "outputs": outputs, "evidence_refs": result.evidence_refs,
            "limitations": result.limitations, "reasons": reasons,
            "source_ref": result.source_ref, "provenance": result.provenance,
            "error": result.error,
        }
    }


def adopt(result: WorkerResult, contract: WorkerContract, sandbox: Sandbox, *, bot: str,
          persona: str, fence=None, keep: list[str] | None = None) -> AdoptionReceipt:
    """Adopt a verified result: kept outputs -> receipts tree, receipt written,
    scratch retired — all inside the fence. Nothing is written on any error."""
    if bot != contract.bot or persona != contract.persona:
        raise IntegrationError(
            f"adoption scope {bot!r}/{persona!r} does not match the contract's "
            f"{contract.bot!r}/{contract.persona!r}")
    errs = verify(result, contract, sandbox)
    if errs:
        raise IntegrationError("result not adoptable: " + "; ".join(errs))
    declared = {o["path"]: o for o in result.outputs}
    keep_list = list(keep) if keep is not None else list(declared)
    unknown = [k for k in keep_list if k not in declared]
    if unknown:
        raise IntegrationError(f"keep names undeclared outputs {unknown}")
    dest_root = kept_dir(contract)

    def commit() -> AdoptionReceipt:
        status = sandbox.retire(keep=keep_list)
        if status != "RETIRED":
            raise IntegrationError(f"sandbox retire returned {status}; nothing adopted")
        outputs = [{**declared[k], "kept_path": str(dest_root / k)} for k in keep_list]
        at = now_iso()
        path = receipts.write_receipt(
            contract.bot, "finish", f"specialist:{contract.worker_id}", contract.parent_run_id,
            None, _detail(result, contract, ADOPTED, [], outputs))
        return AdoptionReceipt(
            worker_id=contract.worker_id, parent_run_id=contract.parent_run_id, bot=contract.bot,
            persona=contract.persona, role=contract.role, decision=ADOPTED,
            receipt_path=str(path), at=at, outputs=outputs,
            evidence_refs=list(result.evidence_refs))

    return _run(fence, commit)


def reject(result: WorkerResult, contract: WorkerContract, sandbox: Sandbox,
           reasons: list[str]) -> RejectionReceipt:
    """Record a truthful failure receipt and retire the scratch keeping nothing."""
    if not isinstance(sandbox, Sandbox) or sandbox.contract.worker_id != contract.worker_id:
        raise IntegrationError("sandbox does not belong to this contract")
    if not isinstance(result, WorkerResult) or result.worker_id != contract.worker_id:
        raise IntegrationError("result does not belong to this contract")
    reasons = [str(r) for r in (reasons or [])] or ["rejected by parent"]
    at = now_iso()
    path = receipts.write_receipt(
        contract.bot, "failure", f"specialist:{contract.worker_id}", contract.parent_run_id,
        None, _detail(result, contract, REJECTED, reasons, list(result.outputs)))
    cleanup = sandbox.retire(keep=[])
    return RejectionReceipt(
        worker_id=contract.worker_id, parent_run_id=contract.parent_run_id, bot=contract.bot,
        persona=contract.persona, role=contract.role, decision=REJECTED,
        receipt_path=str(path), at=at, reasons=reasons, cleanup_status=cleanup)


# --------------------------------------------------------------------------- #
# integrate_into — a value for the parent; never a write
# --------------------------------------------------------------------------- #
def _kept_doc(adopted: AdoptionReceipt, schema: str) -> tuple[dict, dict]:
    for out in adopted.outputs:
        if out.get("schema") == schema:
            p = Path(out["kept_path"])
            try:
                doc = json.loads(p.read_bytes().decode("utf-8"))
            except (OSError, UnicodeDecodeError, ValueError) as exc:
                raise IntegrationError(f"kept output {p} unreadable: {exc}") from exc
            if not isinstance(doc, dict) or doc.get("schema") != schema:
                raise IntegrationError(f"kept output {p} is not a {schema}")
            return out, doc
    raise IntegrationError(f"adopted receipt has no {schema} output")


def integrate_into(kind: str, adopted: AdoptionReceipt) -> dict:
    if not isinstance(adopted, AdoptionReceipt) or adopted.decision != ADOPTED:
        raise IntegrationError("integrate_into needs an ADOPTED AdoptionReceipt")
    if kind not in KNOWN_SCHEMAS:
        raise IntegrationError(f"unknown output schema {kind!r}")
    out, doc = _kept_doc(adopted, kind)
    base = {"schema": kind, "worker_id": adopted.worker_id, "persona": adopted.persona,
            "bot": adopted.bot, "kept_path": out["kept_path"], "sha256": out["sha256"]}
    if kind == "ResearchResult/1":
        return {**base, "evidence_refs": [r for r in doc.get("evidence_refs", [])
                                          if isinstance(r, dict) and r.get("status") == "ok"]}
    if kind == "DraftResult/1":
        cand = doc.get("candidate")
        if not isinstance(cand, dict) or cand.get("status") != DRAFT_UNPUBLISHED:
            raise IntegrationError(f"draft candidate status must be {DRAFT_UNPUBLISHED}")
        return {**base, "candidate": dict(cand), "claims": list(doc.get("claims", []))}
    # Analysis / Review / MediaBrief / EvidenceCapture: attached by reference only.
    return base
