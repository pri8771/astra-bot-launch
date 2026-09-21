"""SB-S23-003 — research specialist adapter.

A bounded researcher that turns ``source_candidate`` input artifacts into
``EvidenceRef`` / ``CaptureReceipt``-shaped files (``CROSS_LANE_INTERFACES.md``
§1 / §2) inside its own sandbox — and nothing else.

Boundaries (``V20_TO_V23_IMPLEMENTATION_SPEC.md`` §5 S23-003 row, §5.3)
-----------------------------------------------------------------------
* Captures go through a ``Collector`` protocol. The default ``FixtureCollector``
  performs no network I/O and labels everything ``provenance="fixture"``. A
  network-capable collector (a bridge over ``runtime.collector.Collector``) is a
  later LIVE artifact with its own manifest; this module does not import
  ``runtime.collector`` and cannot reach the network.
* A receipt that claims a non-fixture provenance from a fixture capture mode is
  treated as forged: it is recorded as ``failed``, never as evidence.
* Failed / empty / partial captures are recorded truthfully under ``unresolved``
  (CROSS_LANE §2: failed evidence cannot support a claim). They never become
  ``evidence_refs``.
* An optional provider must already be a ``specialist_budget.BudgetedProvider``
  (S23-007). It may only rank/summarize captured evidence; any evidence id it
  invents is dropped and noted in ``limitations``. Its calls are counted in the
  shared ledger. Default runs are fully deterministic.
* Every write goes through ``Sandbox.write`` (S23-002), so containment holds.
  The adapter never imports ``pipeline``, ``decision``, ``content_dir`` or any
  publish/enqueue path; ``effect_attempts`` is 0 by construction.
* Deadline (S23-007) is checked between steps; exceeding it yields
  ``TIMED_OUT`` with only fully written files listed in ``outputs``.
"""
from __future__ import annotations

import hashlib
import uuid
from typing import Any, Protocol

from .jsonstore import now_iso
from .specialist_budget import (BudgetedProvider, Deadline, DeadlineExceeded, SpawnGuard,
                                ToolDenied, ChildSpawnDenied, WorkerLedger)
from .specialist_contract import WorkerContract, WorkerResult, validate_contract
from .specialist_sandbox import Sandbox, SandboxError

ROLE = "researcher"
RESULT_SCHEMA = "ResearchResult/1"
EVIDENCE_SCHEMA = "EvidenceCapture/1"
SOURCE_REF = "runtime.specialist_research/1"
COLLECTOR_NAME = "sbots.specialist-fixture-collector"
COLLECTOR_VERSION = "1.0.0"

STATUS_OK, STATUS_EMPTY, STATUS_PARTIAL, STATUS_FAILED = "ok", "empty", "partial", "failed"
CAPTURE_STATUSES = (STATUS_OK, STATUS_EMPTY, STATUS_PARTIAL, STATUS_FAILED)
# Mirrors runtime.collector's provenance vocabulary without importing it.
PROVENANCES = ("trusted_operational", "verified_untrusted", "fixture", "unverified")
MODE_FIXTURE, MODE_LIVE = "fixture", "live"


class AdapterError(Exception):
    pass


class RoleMismatch(AdapterError):
    pass


# --------------------------------------------------------------------------- #
# Collector protocol + fixture
# --------------------------------------------------------------------------- #
class Collector(Protocol):
    def capture(self, ref: dict) -> dict: ...      # returns a CaptureReceipt-shaped dict


def _source_of(ref: dict) -> str | None:
    for k in ("url", "source", "source_id"):
        v = ref.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def canonical_source_id(source: str) -> str:
    return "src-" + hashlib.sha256(source.strip().encode()).hexdigest()[:16]


class FixtureCollector:
    """No-network collector: ``sources`` maps a url/source id to content.

    ``raise_for`` lists sources for which ``capture`` raises (to exercise the
    adapter's failure handling). Everything it returns is ``provenance="fixture"``.
    """

    def __init__(self, sources: dict[str, Any] | None = None, *, raise_for=(),
                 forge_provenance: str | None = None):
        self.sources = dict(sources or {})
        self.raise_for = set(raise_for)
        self.forge_provenance = forge_provenance      # adversarial tests only
        self.calls = 0

    def capture(self, ref: dict) -> dict:
        self.calls += 1
        source = _source_of(ref) or ""
        if source in self.raise_for:
            raise RuntimeError(f"fixture collector failure for {source!r}")
        rid = f"cap-{uuid.uuid4().hex[:12]}"
        base = {
            "receipt_id": rid, "source_url": source, "canonical_id": canonical_source_id(source),
            "retrieved_at": now_iso(), "capture_mode": MODE_FIXTURE, "transport_trusted": False,
            "collector_name": COLLECTOR_NAME, "collector_version": COLLECTOR_VERSION,
            "fetcher_name": "fixture", "http_status": None, "final_url": source,
            "provenance": self.forge_provenance or "fixture", "partial": False,
        }
        if not source or source not in self.sources:
            return {**base, "status": STATUS_FAILED, "content_hash": None, "content_bytes": None,
                    "error": "fixture has no such source", "extraction_status": "not_attempted",
                    "extraction_error": None, "extracted": {}}
        content = self.sources[source]
        if isinstance(content, dict):
            import json
            raw = json.dumps(content, sort_keys=True).encode("utf-8")
        elif isinstance(content, str):
            raw = content.encode("utf-8")
        else:
            raw = bytes(content)
        if not raw:
            return {**base, "status": STATUS_EMPTY, "content_hash": None, "content_bytes": 0,
                    "error": None, "extraction_status": "empty", "extraction_error": None,
                    "extracted": {}}
        try:
            text = raw.decode("utf-8")
            extraction = {"status": "ok", "error": None, "extracted": {"text": text[:2000]}}
        except UnicodeDecodeError:
            extraction = {"status": "failed", "error": "not utf-8", "extracted": {}}
        return {**base, "status": STATUS_OK, "content_hash": hashlib.sha256(raw).hexdigest(),
                "content_bytes": len(raw), "error": None,
                "extraction_status": extraction["status"],
                "extraction_error": extraction["error"], "extracted": extraction["extracted"]}


def _failed_receipt(source: str | None, error: str) -> dict:
    return {"receipt_id": f"cap-{uuid.uuid4().hex[:12]}", "source_url": source or "",
            "canonical_id": canonical_source_id(source or ""), "retrieved_at": now_iso(),
            "status": STATUS_FAILED, "capture_mode": MODE_FIXTURE, "transport_trusted": False,
            "collector_name": "n/a", "collector_version": "n/a", "fetcher_name": "n/a",
            "content_hash": None, "content_bytes": None, "http_status": None,
            "final_url": None, "provenance": "unverified", "error": error, "partial": False,
            "extraction_status": "not_attempted", "extraction_error": None, "extracted": {}}


def validate_receipt(receipt: Any) -> list[str]:
    """Reject malformed or forged receipts before they can become evidence."""
    if not isinstance(receipt, dict):
        return ["receipt is not a dict"]
    errs: list[str] = []
    if receipt.get("status") not in CAPTURE_STATUSES:
        errs.append(f"status must be one of {CAPTURE_STATUSES}")
    if receipt.get("provenance") not in PROVENANCES:
        errs.append(f"provenance must be one of {PROVENANCES}")
    mode = receipt.get("capture_mode")
    if mode not in (MODE_FIXTURE, MODE_LIVE):
        errs.append("capture_mode must be 'fixture' or 'live'")
    elif mode == MODE_FIXTURE and receipt.get("provenance") not in ("fixture", "unverified"):
        # "unverified" makes no trust claim; anything stronger from a fixture is forged.
        errs.append("a fixture capture cannot claim non-fixture provenance (forged)")
    if receipt.get("provenance") == "trusted_operational" and not receipt.get("transport_trusted"):
        errs.append("trusted_operational provenance requires a trusted transport")
    if receipt.get("status") == STATUS_OK and not isinstance(receipt.get("content_hash"), str):
        errs.append("an ok capture needs a content_hash")
    if not isinstance(receipt.get("receipt_id"), str) or not receipt.get("receipt_id"):
        errs.append("receipt_id is required")
    return errs


def evidence_ref_from_receipt(receipt: dict) -> dict:
    """CROSS_LANE §1 EvidenceRef derived from a receipt (the receipt stays the truth)."""
    return {
        "evidence_id": f"ev-{receipt['receipt_id']}",
        "source_id": receipt.get("canonical_id"),
        "url": receipt.get("source_url") or None,
        "captured_at": receipt.get("retrieved_at"),
        "content_hash": receipt.get("content_hash"),
        "provenance": receipt.get("provenance"),
        "collector_version": receipt.get("collector_version"),
        "status": receipt.get("status"),
    }


# --------------------------------------------------------------------------- #
# The adapter
# --------------------------------------------------------------------------- #
class ResearchSpecialist:
    role = ROLE

    def run(self, contract: WorkerContract, sandbox: Sandbox, *, collector: Collector | None = None,
            provider: BudgetedProvider | None = None, deadline: Deadline | None = None,
            ledger: WorkerLedger | None = None, source_ref: str = SOURCE_REF) -> WorkerResult:
        if getattr(contract, "role", None) != self.role:
            raise RoleMismatch(f"{type(self).__name__} runs role {self.role!r}, "
                               f"contract role is {getattr(contract, 'role', None)!r}")
        errs = validate_contract(contract)
        if errs:
            raise AdapterError("invalid contract: " + "; ".join(errs))
        if sandbox.contract.worker_id != contract.worker_id:
            raise AdapterError("sandbox belongs to a different worker")
        if provider is not None and not isinstance(provider, BudgetedProvider):
            raise AdapterError("provider must be wrapped by specialist_budget.BudgetedProvider")
        if provider is not None and provider.contract.worker_id != contract.worker_id:
            raise AdapterError("provider is budgeted for a different worker")

        ledger = ledger or (provider.ledger if provider is not None else WorkerLedger.for_contract(contract))
        deadline = deadline or Deadline(contract)
        collector = collector or FixtureCollector()
        started = now_iso()
        outputs: list[dict] = []
        evidence_refs: list[dict] = []
        unresolved: list[dict] = []
        limitations: list[str] = []
        summary: list[str] = []
        result_state = "COMPLETED"
        error: str | None = None

        def finish(state: str, err: str | None = None) -> WorkerResult:
            return WorkerResult(
                worker_id=contract.worker_id, parent_run_id=contract.parent_run_id,
                bot=contract.bot, persona=contract.persona, role=contract.role,
                started_at=started, finished_at=now_iso(), source_ref=source_ref,
                result=state, outputs=list(outputs), evidence_refs=list(evidence_refs),
                calls_used=ledger.calls_used, effect_attempts=ledger.effect_attempts,
                limitations=list(limitations), cleanup_status="PENDING",
                provenance=contract.provenance, error=err)

        # A sandbox whose context failed to materialize must not be worked in.
        try:
            if sandbox.context_failed():
                return finish("FAILED", "bounded context could not be materialized; see context/FAILED.json")
        except SandboxError as exc:
            return finish("FAILED", f"sandbox unusable: {exc}")

        try:
            SpawnGuard.assert_tool_allowed(contract, "write_scratch")
        except (ToolDenied, ChildSpawnDenied) as exc:
            return finish("FAILED", f"cannot produce outputs: {exc}")
        can_capture = True
        try:
            SpawnGuard.assert_tool_allowed(contract, "capture_source")
        except (ToolDenied, ChildSpawnDenied) as exc:
            can_capture = False
            limitations.append(f"capture_source not granted: {exc}")

        candidates = [a for a in contract.input_artifacts
                      if isinstance(a, dict) and a.get("kind") == "source_candidate"]
        if not candidates:
            limitations.append("no sources")

        try:
            for n, ref in enumerate(candidates):
                deadline.check()
                source = _source_of(ref)
                if not can_capture:
                    unresolved.append({"index": n, "source": source, "error": "capture_source not granted"})
                    continue
                try:
                    receipt = collector.capture(ref)
                except Exception as exc:                 # noqa: BLE001 - recorded, never hidden
                    receipt = _failed_receipt(source, f"{type(exc).__name__}: {exc}")
                verrs = validate_receipt(receipt)
                if verrs:
                    receipt = _failed_receipt(source, "invalid or forged receipt: " + "; ".join(verrs))
                ev = evidence_ref_from_receipt(receipt)
                rel = f"evidence/{n:03d}.json"
                sandbox.write(rel, {"schema": EVIDENCE_SCHEMA, "index": n, "input": ref,
                                    "evidence_ref": ev, "receipt": receipt})
                outputs.append({"schema": EVIDENCE_SCHEMA, "path": rel, "sha256": sandbox.sha256(rel)})
                if receipt["status"] == STATUS_OK:
                    evidence_refs.append(ev)
                    summary.append(f"captured {source} ({receipt.get('content_bytes')} bytes)")
                else:
                    unresolved.append({"index": n, "source": source, "status": receipt["status"],
                                       "error": receipt.get("error")})

            if provider is not None and evidence_refs:
                deadline.check()
                known = {e["evidence_id"] for e in evidence_refs}
                try:
                    proposal = provider.propose({
                        "persona": contract.persona, "bot": contract.bot,
                        "objective": contract.objective,
                        "evidence": [{"evidence_id": e["evidence_id"], "url": e["url"]}
                                     for e in evidence_refs]})
                except DeadlineExceeded:
                    raise
                except Exception as exc:                 # noqa: BLE001 - budget/scope/provider faults
                    limitations.append(f"provider unavailable: {type(exc).__name__}: {exc}")
                else:
                    ranked, prov_summary = _sanitize_proposal(proposal, known, limitations)
                    if ranked:
                        order = {eid: i for i, eid in enumerate(ranked)}
                        evidence_refs.sort(key=lambda e: order.get(e["evidence_id"], len(order)))
                    summary.extend(prov_summary)

            deadline.check()
        except DeadlineExceeded as exc:
            result_state, error = "TIMED_OUT", str(exc)
            limitations.append("time budget exceeded; partial evidence kept")
        except SandboxError as exc:
            return finish("FAILED", f"sandbox refused a write: {exc}")

        result_doc = {
            "schema": RESULT_SCHEMA, "worker_id": contract.worker_id, "objective": contract.objective,
            "result": result_state, "evidence_refs": evidence_refs, "summary": summary,
            "unresolved": unresolved, "captured": len(evidence_refs), "failed": len(unresolved),
            "limitations": limitations, "provenance": contract.provenance,
        }
        try:
            rel = "outputs/research_result.json"
            sandbox.write(rel, result_doc)
            outputs.append({"schema": RESULT_SCHEMA, "path": rel, "sha256": sandbox.sha256(rel)})
        except SandboxError as exc:
            return finish("FAILED", f"sandbox refused the result write: {exc}")
        return finish(result_state, error)


def _sanitize_proposal(proposal: Any, known: set[str], limitations: list[str]) -> tuple[list[str], list[str]]:
    """Keep only ranked ids the researcher actually captured; note anything invented."""
    if not isinstance(proposal, dict):
        limitations.append("provider proposal ignored: not a dict")
        return [], []
    ranked_in = proposal.get("ranked_evidence_ids") or []
    ranked = [r for r in ranked_in if isinstance(r, str) and r in known]
    dropped = [r for r in ranked_in if r not in ranked]
    if dropped:
        limitations.append(f"provider referenced uncaptured evidence ids (dropped): {dropped}")
    summ = [s for s in (proposal.get("summary") or []) if isinstance(s, str) and s.strip()]
    return ranked, summ[:20]
