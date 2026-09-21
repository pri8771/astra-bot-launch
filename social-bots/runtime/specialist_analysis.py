"""SB-S23-004 — analyst and reviewer specialist adapters.

Two bounded roles with typed result schemas (``V20_TO_V23_IMPLEMENTATION_SPEC.md``
§5 S23-004 row):

``AnalystSpecialist`` -> ``AnalysisResult/1``
    Turns the evidence the parent placed in the sandbox (``inputs/`` and
    ``context/``: ``ResearchResult/1`` and ``EvidenceCapture/1`` files) into
    findings that each cite resolvable evidence ids. Deterministic default: one
    finding per ``ok`` evidence capture with ``confidence=None`` (unknown is not
    zero). An optional ``BudgetedProvider`` may add findings, but a finding whose
    evidence ids do not resolve is moved to ``unsupported_claims``, never kept.

``ReviewerSpecialist`` -> ``ReviewResult/1``
    An integrity review of the input bundle: every finding must cite resolvable
    evidence; every draft claim must cite resolvable evidence AND be covered by
    a finding on that evidence; a draft must be ``DRAFT_UNPUBLISHED``. The
    reviewer records the sha256 of every file it reviewed so the parent
    (SB-S23-006) can prove it changed nothing. A provider may add issues but can
    never flip a deterministic ``FAIL`` to ``PASS``; on a deterministic ``PASS``
    provider issues yield ``NEEDS_EVIDENCE`` (a model may ask, not assert).

Write boundary
--------------
Both adapters work through ``RestrictedView``: a sandbox view whose ``write``
accepts exactly one path (the role's own result file) and raises
``WriteDenied`` for anything else, including ``inputs/`` and ``context/``. The
adapters never hold the raw ``Sandbox`` write path. Any ``WriteDenied`` during a
run yields a ``FAILED`` result; input bytes are untouched.

Neither adapter imports ``pipeline``, ``decision``, ``factcheck``, state or
content stores; ``effect_attempts`` is 0 by construction. No network, no model
call in the default path.
"""
from __future__ import annotations

import json
from typing import Any

from .jsonstore import now_iso
from .specialist_budget import BudgetedProvider, Deadline, DeadlineExceeded, SpawnGuard, \
    ToolDenied, ChildSpawnDenied, WorkerLedger
from .specialist_contract import WorkerContract, WorkerResult, validate_contract
from .specialist_sandbox import Sandbox, SandboxError

ANALYSIS_SCHEMA = "AnalysisResult/1"
REVIEW_SCHEMA = "ReviewResult/1"
ANALYST_RESULT_PATH = "outputs/analyst_result.json"
REVIEWER_RESULT_PATH = "outputs/reviewer_result.json"
SOURCE_REF = "runtime.specialist_analysis/1"
DRAFT_UNPUBLISHED = "DRAFT_UNPUBLISHED"
INPUT_PREFIXES = ("inputs/", "context/")

PASS, FAIL, NEEDS_EVIDENCE = "PASS", "FAIL", "NEEDS_EVIDENCE"
_FAIL_KINDS = frozenset({"unsupported_finding", "unsupported_claim", "uncovered_claim",
                         "draft_status", "malformed_draft", "malformed_analysis"})


class AdapterError(Exception):
    pass


class RoleMismatch(AdapterError):
    pass


class WriteDenied(SandboxError):
    """The adapter tried to write somewhere other than its own result file."""


# --------------------------------------------------------------------------- #
# Restricted sandbox view
# --------------------------------------------------------------------------- #
class RestrictedView:
    """Read-only over the sandbox except for exactly one result path."""

    def __init__(self, sandbox: Sandbox, allowed_result_path: str):
        self._sb = sandbox
        self.allowed = allowed_result_path

    @property
    def contract(self) -> WorkerContract:
        return self._sb.contract

    def read(self, rel: str) -> bytes:
        return self._sb.read(rel)

    def list(self) -> list[str]:
        return self._sb.list()

    def sha256(self, rel: str) -> str:
        return self._sb.sha256(rel)

    def context_failed(self) -> bool:
        return self._sb.context_failed()

    def write(self, rel: str, data) -> Any:
        if rel != self.allowed:
            raise WriteDenied(f"{rel!r} is not this adapter's result path {self.allowed!r}")
        return self._sb.write(rel, data)


# --------------------------------------------------------------------------- #
# Input bundle
# --------------------------------------------------------------------------- #
class Bundle:
    """Parsed JSON inputs (``inputs/`` + ``context/``) with an evidence index."""

    def __init__(self, view: RestrictedView):
        self.docs: list[tuple[str, dict]] = []
        self.unreadable: list[dict] = []
        self.reviewed_sha256: dict[str, str] = {}
        self.evidence: dict[str, dict] = {}           # evidence_id -> {"ref", "path"}
        for rel in view.list():
            if not rel.startswith(INPUT_PREFIXES):
                continue
            self.reviewed_sha256[rel] = view.sha256(rel)
            if not rel.endswith(".json"):
                continue
            try:
                doc = json.loads(view.read(rel).decode("utf-8"))
            except (UnicodeDecodeError, ValueError) as exc:
                self.unreadable.append({"path": rel, "error": f"{type(exc).__name__}: {exc}"})
                continue
            if not isinstance(doc, dict):
                self.unreadable.append({"path": rel, "error": "not a JSON object"})
                continue
            self.docs.append((rel, doc))
            self._index_evidence(rel, doc)

    def _index_evidence(self, rel: str, doc: dict) -> None:
        schema = doc.get("schema")
        if schema == "EvidenceCapture/1":
            ref = doc.get("evidence_ref") or {}
            receipt = doc.get("receipt") or {}
            if isinstance(ref, dict) and ref.get("evidence_id") and receipt.get("status") == "ok":
                self.evidence.setdefault(ref["evidence_id"], {"ref": ref, "path": rel})
        elif schema == "ResearchResult/1":
            for ref in doc.get("evidence_refs") or []:
                if isinstance(ref, dict) and ref.get("evidence_id") and ref.get("status") == "ok":
                    self.evidence.setdefault(ref["evidence_id"], {"ref": ref, "path": rel})

    def by_schema(self, schema: str) -> list[tuple[str, dict]]:
        return [(p, d) for p, d in self.docs if d.get("schema") == schema]

    def resolves(self, ids: Any) -> list[str]:
        if not isinstance(ids, list):
            return []
        return [i for i in ids if isinstance(i, str) and i in self.evidence]


def _ids_of(refs: Any) -> list[str]:
    """Evidence ids from a list of ref dicts or bare ids."""
    out: list[str] = []
    if not isinstance(refs, list):
        return out
    for r in refs:
        if isinstance(r, dict) and isinstance(r.get("evidence_id"), str):
            out.append(r["evidence_id"])
        elif isinstance(r, str):
            out.append(r)
    return out


def _confidence(v: Any) -> float | None:
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return None
    return float(v) if 0.0 <= v <= 1.0 else None


# --------------------------------------------------------------------------- #
# Shared run scaffolding
# --------------------------------------------------------------------------- #
class _Base:
    role = ""
    result_path = ""
    schema = ""

    def _prepare(self, contract, sandbox, provider, deadline, ledger):
        if getattr(contract, "role", None) != self.role:
            raise RoleMismatch(f"{type(self).__name__} runs role {self.role!r}, "
                               f"contract role is {getattr(contract, 'role', None)!r}")
        errs = validate_contract(contract)
        if errs:
            raise AdapterError("invalid contract: " + "; ".join(errs))
        if sandbox.contract.worker_id != contract.worker_id:
            raise AdapterError("sandbox belongs to a different worker")
        if provider is not None and (not isinstance(provider, BudgetedProvider)
                                     or provider.contract.worker_id != contract.worker_id):
            raise AdapterError("provider must be a BudgetedProvider for this worker")
        ledger = ledger or (provider.ledger if provider is not None else WorkerLedger.for_contract(contract))
        return RestrictedView(sandbox, self.result_path), ledger, deadline or Deadline(contract)

    def _finish(self, contract, ledger, started, state, outputs, evidence_refs, limitations,
                error, source_ref) -> WorkerResult:
        return WorkerResult(
            worker_id=contract.worker_id, parent_run_id=contract.parent_run_id,
            bot=contract.bot, persona=contract.persona, role=contract.role,
            started_at=started, finished_at=now_iso(), source_ref=source_ref, result=state,
            outputs=list(outputs), evidence_refs=list(evidence_refs),
            calls_used=ledger.calls_used, effect_attempts=ledger.effect_attempts,
            limitations=list(limitations), cleanup_status="PENDING",
            provenance=contract.provenance, error=error)

    def _propose(self, provider, contract, payload, limitations) -> dict | None:
        if provider is None:
            return None
        try:
            out = provider.propose({"persona": contract.persona, "bot": contract.bot,
                                    "objective": contract.objective, **payload})
        except DeadlineExceeded:
            raise
        except Exception as exc:                            # noqa: BLE001 - recorded
            limitations.append(f"provider unavailable: {type(exc).__name__}: {exc}")
            return None
        if not isinstance(out, dict):
            limitations.append("provider proposal ignored: not a dict")
            return None
        return out


# --------------------------------------------------------------------------- #
# Analyst
# --------------------------------------------------------------------------- #
class AnalystSpecialist(_Base):
    role = "analyst"
    result_path = ANALYST_RESULT_PATH
    schema = ANALYSIS_SCHEMA

    def run(self, contract: WorkerContract, sandbox: Sandbox, *, provider: BudgetedProvider | None = None,
            deadline: Deadline | None = None, ledger: WorkerLedger | None = None,
            source_ref: str = SOURCE_REF) -> WorkerResult:
        view, ledger, deadline = self._prepare(contract, sandbox, provider, deadline, ledger)
        started = now_iso()
        limitations: list[str] = []
        outputs: list[dict] = []
        fin = lambda state, refs=(), err=None: self._finish(          # noqa: E731
            contract, ledger, started, state, outputs, refs, limitations, err, source_ref)
        try:
            if view.context_failed():
                return fin("FAILED", err="bounded context could not be materialized")
            SpawnGuard.assert_tool_allowed(contract, "write_scratch")
            SpawnGuard.assert_tool_allowed(contract, "read_scratch_inputs")
        except (ToolDenied, ChildSpawnDenied) as exc:
            return fin("FAILED", err=f"tool not granted: {exc}")
        except SandboxError as exc:
            return fin("FAILED", err=f"sandbox unusable: {exc}")

        findings: list[dict] = []
        unsupported: list[str] = []
        try:
            deadline.check()
            bundle = Bundle(view)
            for u in bundle.unreadable:
                limitations.append(f"unreadable input {u['path']}: {u['error']}")
            if not bundle.evidence:
                limitations.append("no evidence inputs")
            for eid, entry in bundle.evidence.items():
                ref = entry["ref"]
                findings.append({
                    "statement": f"Source {ref.get('url') or ref.get('source_id')} was captured "
                                 f"(content sha256 {str(ref.get('content_hash'))[:12]})",
                    "evidence_refs": [ref], "confidence": None,
                    "uncertainty": ["deterministic placeholder finding; no model analysis"],
                })
            deadline.check()
            proposal = self._propose(provider, contract, {"evidence_ids": sorted(bundle.evidence)}, limitations)
            if proposal is not None:
                for f in proposal.get("findings") or []:
                    if not isinstance(f, dict) or not isinstance(f.get("statement"), str):
                        limitations.append("provider finding ignored: malformed")
                        continue
                    ids = bundle.resolves(_ids_of(f.get("evidence_ids") or f.get("evidence_refs")))
                    if not ids:
                        unsupported.append(f["statement"])
                        continue
                    findings.append({
                        "statement": f["statement"],
                        "evidence_refs": [bundle.evidence[i]["ref"] for i in ids],
                        "confidence": _confidence(f.get("confidence")),
                        "uncertainty": [u for u in (f.get("uncertainty") or []) if isinstance(u, str)],
                    })
                for s in proposal.get("unsupported_claims") or []:
                    if isinstance(s, str):
                        unsupported.append(s)
            deadline.check()
        except DeadlineExceeded as exc:
            limitations.append("time budget exceeded")
            return fin("TIMED_OUT", err=str(exc))
        except SandboxError as exc:
            return fin("FAILED", err=f"sandbox refused: {exc}")

        doc = {"schema": ANALYSIS_SCHEMA, "worker_id": contract.worker_id,
               "objective": contract.objective, "findings": findings,
               "unsupported_claims": unsupported, "limitations": limitations,
               "inputs_reviewed": bundle.reviewed_sha256, "provenance": contract.provenance}
        try:
            view.write(self.result_path, doc)
            outputs.append({"schema": ANALYSIS_SCHEMA, "path": self.result_path,
                            "sha256": view.sha256(self.result_path)})
        except SandboxError as exc:
            return fin("FAILED", err=f"result write refused: {exc}")
        cited = {r["evidence_id"]: r for f in findings for r in f["evidence_refs"]}
        return fin("COMPLETED", refs=list(cited.values()))


# --------------------------------------------------------------------------- #
# Reviewer
# --------------------------------------------------------------------------- #
class ReviewerSpecialist(_Base):
    role = "reviewer"
    result_path = REVIEWER_RESULT_PATH
    schema = REVIEW_SCHEMA

    @staticmethod
    def integrity_issues(bundle: Bundle) -> list[dict]:
        """Deterministic integrity review of a bundle. Pure; no writes."""
        issues: list[dict] = []
        finding_evidence: set[str] = set()
        for path, doc in bundle.by_schema("AnalysisResult/1"):
            findings = doc.get("findings")
            if not isinstance(findings, list):
                issues.append({"kind": "malformed_analysis", "detail": "findings missing", "ref": path})
                continue
            for i, f in enumerate(findings):
                ids = bundle.resolves(_ids_of((f or {}).get("evidence_refs"))) if isinstance(f, dict) else []
                if not ids:
                    issues.append({"kind": "unsupported_finding",
                                   "detail": f"finding {i} cites no resolvable evidence", "ref": path})
                finding_evidence.update(ids)
        for path, doc in bundle.by_schema("DraftResult/1"):
            cand = doc.get("candidate")
            if not isinstance(cand, dict):
                issues.append({"kind": "malformed_draft", "detail": "candidate missing", "ref": path})
                continue
            if cand.get("status") != DRAFT_UNPUBLISHED:
                issues.append({"kind": "draft_status",
                               "detail": f"candidate status {cand.get('status')!r} != {DRAFT_UNPUBLISHED}",
                               "ref": path})
            claims = doc.get("claims")
            if not isinstance(claims, list):
                issues.append({"kind": "malformed_draft", "detail": "claims missing", "ref": path})
                continue
            for i, c in enumerate(claims):
                ids = bundle.resolves(_ids_of((c or {}).get("evidence_refs"))) if isinstance(c, dict) else []
                if not ids:
                    issues.append({"kind": "unsupported_claim",
                                   "detail": f"claim {i} cites no resolvable evidence", "ref": path})
                elif not any(i_ in finding_evidence for i_ in ids):
                    issues.append({"kind": "uncovered_claim",
                                   "detail": f"claim {i} has no finding on its evidence", "ref": path})
        return issues

    def run(self, contract: WorkerContract, sandbox: Sandbox, *, provider: BudgetedProvider | None = None,
            deadline: Deadline | None = None, ledger: WorkerLedger | None = None,
            source_ref: str = SOURCE_REF) -> WorkerResult:
        view, ledger, deadline = self._prepare(contract, sandbox, provider, deadline, ledger)
        started = now_iso()
        limitations: list[str] = []
        outputs: list[dict] = []
        fin = lambda state, err=None: self._finish(                    # noqa: E731
            contract, ledger, started, state, outputs, [], limitations, err, source_ref)
        try:
            if view.context_failed():
                return fin("FAILED", err="bounded context could not be materialized")
            SpawnGuard.assert_tool_allowed(contract, "write_scratch")
            SpawnGuard.assert_tool_allowed(contract, "read_scratch_inputs")
        except (ToolDenied, ChildSpawnDenied) as exc:
            return fin("FAILED", err=f"tool not granted: {exc}")
        except SandboxError as exc:
            return fin("FAILED", err=f"sandbox unusable: {exc}")

        try:
            deadline.check()
            bundle = Bundle(view)
            for u in bundle.unreadable:
                limitations.append(f"unreadable input {u['path']}: {u['error']}")
            issues = self.integrity_issues(bundle)
            reviewable = bundle.by_schema("AnalysisResult/1") + bundle.by_schema("DraftResult/1")
            if not reviewable:
                verdict = NEEDS_EVIDENCE
                issues.append({"kind": "no_reviewable_input", "detail": "no AnalysisResult/DraftResult inputs",
                               "ref": None})
            elif any(i["kind"] in _FAIL_KINDS for i in issues):
                verdict = FAIL
            else:
                verdict = PASS
            deadline.check()
            proposal = self._propose(provider, contract, {
                "verdict_deterministic": verdict, "issues": issues,
                "reviewed": sorted(bundle.reviewed_sha256)}, limitations)
            if proposal is not None:
                added = 0
                for i in proposal.get("issues") or []:
                    if isinstance(i, dict) and isinstance(i.get("detail"), str):
                        issues.append({"kind": "provider_issue", "detail": i["detail"],
                                       "ref": i.get("ref") if isinstance(i.get("ref"), str) else None})
                        added += 1
                if proposal.get("verdict") == PASS and verdict == FAIL:
                    limitations.append("provider PASS ignored: deterministic integrity FAIL stands")
                if added and verdict == PASS:
                    verdict = NEEDS_EVIDENCE
                    limitations.append("provider raised issues on a deterministic PASS: NEEDS_EVIDENCE")
            deadline.check()
        except DeadlineExceeded as exc:
            limitations.append("time budget exceeded")
            return fin("TIMED_OUT", err=str(exc))
        except SandboxError as exc:
            return fin("FAILED", err=f"sandbox refused: {exc}")

        doc = {"schema": REVIEW_SCHEMA, "worker_id": contract.worker_id, "verdict": verdict,
               "issues": issues, "reviewed_sha256": bundle.reviewed_sha256,
               "limitations": limitations, "provenance": contract.provenance}
        try:
            view.write(self.result_path, doc)
            outputs.append({"schema": REVIEW_SCHEMA, "path": self.result_path,
                            "sha256": view.sha256(self.result_path)})
        except SandboxError as exc:
            return fin("FAILED", err=f"result write refused: {exc}")
        return fin("COMPLETED")
