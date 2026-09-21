"""SB-S23-005 — writer and media-brief specialist adapters.

Two bounded roles without any public-effect or account authority
(``V20_TO_V23_IMPLEMENTATION_SPEC.md`` §5 S23-005 row):

``WriterSpecialist`` -> ``DraftResult/1``
    Assembles an UNPUBLISHED draft candidate from the findings the parent placed
    in the sandbox (``AnalysisResult/1`` + evidence captures). Every claim in the
    draft carries the evidence refs of the finding it came from. An optional
    ``BudgetedProvider`` may rewrite prose; any provider-introduced claim without
    resolvable evidence is stripped and noted; a provider can never change the
    candidate ``status``.

``MediaBriefSpecialist`` -> ``MediaBriefResult/1``
    Produces a structured brief (format, shots/frames, alt text, sources) from
    the same inputs. Missing alt text is a limitation, never an empty string
    presented as alt text.

Candidate shape
---------------
``DraftResult.candidate`` is shape-compatible with the pipeline candidate draft
observed in ``runtime/pipeline.py::ideate`` at the implementation source
(keys: ``content_id, bot, persona, signal_id, angle, hook, body, source_refs,
signature_move, created_at, status``) so the parent can hand an ADOPTED draft to
the existing pipeline gates later. ``status`` is the constant
``DRAFT_UNPUBLISHED`` and is re-imposed after any provider rewrite; the pipeline
itself uses ``"ideated"`` for its own drafts, so a specialist draft is never
mistaken for a pipeline-ideated one.

Boundaries
----------
* Writes go through ``RestrictedView`` (S23-004): exactly one result file.
* No import of ``pipeline``, ``decision``, ``content_intelligence``,
  ``cultural_review``, ``experiment_engine``, state or content stores; nothing
  here can enqueue, publish, register an experiment or touch ``content_dir``.
  Platform formatting and cultural review remain Intelligence gates that run at
  adoption/pipeline time, not here.
* ``effect_attempts`` is 0 by construction; no network; no model call by default.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

from .jsonstore import now_iso
from .specialist_analysis import (Bundle, RestrictedView, AdapterError, RoleMismatch,
                                  _ids_of, _Base)
from .specialist_budget import BudgetedProvider, Deadline, DeadlineExceeded, SpawnGuard, \
    ToolDenied, ChildSpawnDenied, WorkerLedger
from .specialist_contract import WorkerContract, WorkerResult
from .specialist_sandbox import Sandbox, SandboxError

DRAFT_SCHEMA = "DraftResult/1"
MEDIA_SCHEMA = "MediaBriefResult/1"
WRITER_RESULT_PATH = "outputs/writer_result.json"
MEDIA_RESULT_PATH = "outputs/media_brief.json"
SOURCE_REF = "runtime.specialist_writer/1"
DRAFT_UNPUBLISHED = "DRAFT_UNPUBLISHED"

# Pipeline-compatible candidate keys (see module docstring). Kept as a tuple so
# tests can assert the shape and reviewers can diff it against pipeline.ideate.
CANDIDATE_KEYS = ("content_id", "bot", "persona", "signal_id", "angle", "hook", "body",
                  "source_refs", "signature_move", "created_at", "status")

__all__ = ["WriterSpecialist", "MediaBriefSpecialist", "AdapterError", "RoleMismatch",
           "DRAFT_SCHEMA", "MEDIA_SCHEMA", "CANDIDATE_KEYS", "DRAFT_UNPUBLISHED"]


def _findings(bundle: Bundle) -> list[dict]:
    """Findings from AnalysisResult/1 inputs whose evidence resolves in the bundle."""
    out: list[dict] = []
    for _path, doc in bundle.by_schema("AnalysisResult/1"):
        for f in doc.get("findings") or []:
            if not isinstance(f, dict) or not isinstance(f.get("statement"), str):
                continue
            ids = bundle.resolves(_ids_of(f.get("evidence_refs")))
            if ids:
                out.append({"statement": f["statement"],
                            "evidence_refs": [bundle.evidence[i]["ref"] for i in ids]})
    return out


def _content_id(worker_id: str, claims: list[dict]) -> str:
    basis = json.dumps([c["text"] for c in claims], sort_keys=True) + "|" + worker_id
    return "sdraft-" + hashlib.sha256(basis.encode()).hexdigest()[:12]


class WriterSpecialist(_Base):
    role = "writer"
    result_path = WRITER_RESULT_PATH
    schema = DRAFT_SCHEMA

    def run(self, contract: WorkerContract, sandbox: Sandbox, *, provider: BudgetedProvider | None = None,
            deadline: Deadline | None = None, ledger: WorkerLedger | None = None,
            source_ref: str = SOURCE_REF, platform_hint: str | None = None) -> WorkerResult:
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

        try:
            deadline.check()
            bundle = Bundle(view)
            for u in bundle.unreadable:
                limitations.append(f"unreadable input {u['path']}: {u['error']}")
            findings = _findings(bundle)
            claims = [{"text": f["statement"], "evidence_refs": f["evidence_refs"]} for f in findings]
            if not claims:
                limitations.append("no supported claims")
            hook = claims[0]["text"] if claims else ""
            body = "\n".join(c["text"] for c in claims)
            deadline.check()
            proposal = self._propose(provider, contract, {
                "claims": [c["text"] for c in claims],
                "evidence_ids": sorted(bundle.evidence), "platform_hint": platform_hint}, limitations)
            if proposal is not None:
                new_claims: list[dict] = []
                for c in proposal.get("claims") or []:
                    if not isinstance(c, dict) or not isinstance(c.get("text"), str):
                        limitations.append("provider claim ignored: malformed")
                        continue
                    ids = bundle.resolves(_ids_of(c.get("evidence_ids") or c.get("evidence_refs")))
                    if not ids:
                        limitations.append(f"provider claim stripped (no evidence): {c['text'][:60]!r}")
                        continue
                    new_claims.append({"text": c["text"],
                                       "evidence_refs": [bundle.evidence[i]["ref"] for i in ids]})
                if new_claims:
                    claims = new_claims
                if isinstance(proposal.get("hook"), str) and proposal["hook"].strip():
                    hook = proposal["hook"].strip()
                if isinstance(proposal.get("body"), str) and proposal["body"].strip():
                    body = proposal["body"].strip()
                if "status" in proposal or "candidate" in proposal:
                    limitations.append("provider attempted to set candidate status/shape: ignored")
            deadline.check()
        except DeadlineExceeded as exc:
            limitations.append("time budget exceeded")
            return fin("TIMED_OUT", err=str(exc))
        except SandboxError as exc:
            return fin("FAILED", err=f"sandbox refused: {exc}")

        source_refs = sorted({r.get("url") or r.get("source_id") for c in claims
                              for r in c["evidence_refs"] if r.get("url") or r.get("source_id")})
        candidate = {
            "content_id": _content_id(contract.worker_id, claims),
            "bot": contract.bot, "persona": contract.persona, "signal_id": None,
            "angle": contract.objective, "hook": hook, "body": body,
            "source_refs": source_refs, "signature_move": "specialist-draft",
            "created_at": now_iso(), "status": DRAFT_UNPUBLISHED,     # constant, re-imposed
        }
        doc = {"schema": DRAFT_SCHEMA, "worker_id": contract.worker_id, "candidate": candidate,
               "claims": claims, "platform_hint": platform_hint, "limitations": limitations,
               "inputs_reviewed": bundle.reviewed_sha256, "provenance": contract.provenance}
        try:
            view.write(self.result_path, doc)
            outputs.append({"schema": DRAFT_SCHEMA, "path": self.result_path,
                            "sha256": view.sha256(self.result_path)})
        except SandboxError as exc:
            return fin("FAILED", err=f"result write refused: {exc}")
        cited = {r["evidence_id"]: r for c in claims for r in c["evidence_refs"]}
        return fin("COMPLETED", refs=list(cited.values()))


class MediaBriefSpecialist(_Base):
    role = "media"
    result_path = MEDIA_RESULT_PATH
    schema = MEDIA_SCHEMA

    def run(self, contract: WorkerContract, sandbox: Sandbox, *, provider: BudgetedProvider | None = None,
            deadline: Deadline | None = None, ledger: WorkerLedger | None = None,
            source_ref: str = SOURCE_REF, fmt: str = "short-vertical") -> WorkerResult:
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

        try:
            deadline.check()
            bundle = Bundle(view)
            for u in bundle.unreadable:
                limitations.append(f"unreadable input {u['path']}: {u['error']}")
            findings = _findings(bundle)
            sources = [entry["ref"] for entry in bundle.evidence.values()]
            shots = [{"n": i + 1, "beat": f["statement"], "evidence_refs": f["evidence_refs"]}
                     for i, f in enumerate(findings)]
            if not shots:
                limitations.append("no supported findings to storyboard")
            alt_text: str | None = None
            deadline.check()
            proposal = self._propose(provider, contract, {
                "beats": [s["beat"] for s in shots], "format": fmt}, limitations)
            if proposal is not None:
                if isinstance(proposal.get("alt_text"), str) and proposal["alt_text"].strip():
                    alt_text = proposal["alt_text"].strip()
                extra = [s for s in (proposal.get("shots") or []) if isinstance(s, dict)
                         and isinstance(s.get("beat"), str)]
                for s in extra:
                    ids = bundle.resolves(_ids_of(s.get("evidence_ids") or s.get("evidence_refs")))
                    if not ids:
                        limitations.append(f"provider shot stripped (no evidence): {s['beat'][:60]!r}")
                        continue
                    shots.append({"n": len(shots) + 1, "beat": s["beat"],
                                  "evidence_refs": [bundle.evidence[i]["ref"] for i in ids]})
            if alt_text is None:
                limitations.append("alt text missing; supply before any accessible publication")
            deadline.check()
        except DeadlineExceeded as exc:
            limitations.append("time budget exceeded")
            return fin("TIMED_OUT", err=str(exc))
        except SandboxError as exc:
            return fin("FAILED", err=f"sandbox refused: {exc}")

        doc = {"schema": MEDIA_SCHEMA, "worker_id": contract.worker_id,
               "brief": {"format": fmt, "shots_or_frames": shots, "alt_text": alt_text,
                         "sources": sources, "status": DRAFT_UNPUBLISHED},
               "limitations": limitations, "inputs_reviewed": bundle.reviewed_sha256,
               "provenance": contract.provenance}
        try:
            view.write(self.result_path, doc)
            outputs.append({"schema": MEDIA_SCHEMA, "path": self.result_path,
                            "sha256": view.sha256(self.result_path)})
        except SandboxError as exc:
            return fin("FAILED", err=f"result write refused: {exc}")
        cited = {r["evidence_id"]: r for s in shots for r in s["evidence_refs"]}
        return fin("COMPLETED", refs=list(cited.values()))
