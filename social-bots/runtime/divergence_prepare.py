"""SB-V04-002/004 — PREPARE-ONLY adaptive divergence matrix.

This module builds, hashes, isolation-checks and reports on the conservative
five-call divergence matrix defined in ``V04_DIVERGENCE_ACCEPTANCE_PLAN.md``.

It does **not** make a model call. Preparing the matrix is explicitly authorized
now; executing it is not. ``execute_batch`` exists and is complete, but its first
action is to consult ``authorization.authorize``, which fails closed before any
provider is constructed while no canonical lead manifest exists.

The matrix
----------
One frozen evidence snapshot ``E1`` and a second materially different snapshot
``E2``. Objective, pending count, duplication state, prior hypotheses and policy
posture are held constant across every case::

    P0  social-a                   + E1     persona baseline
    P1  social-b                   + E1     persona-only variant
    P2  social-c                   + E1     persona-only variant
    P3  cultural/Primandir         + E1     persona-only variant (cultural)
    E0  social-a                   + E2     evidence-only variant

    required comparisons: P0|P1, P0|P2, P0|P3 (persona) and P0|E0 (evidence)

What is hashed
--------------
Per case, SHA-256 over three distinct things, because they answer three
different audit questions:

``evidence_bytes_sha256`` / ``evidence_receipt_sha256``
    What was captured from the outside world, and the capture receipt proving
    how. Binds the matrix to real evidence rather than a reconstruction.
``context_sha256``
    The bounded context projection used for receipt matching and single-variable
    comparison (``reasoning_receipt.bounded_context``).
``prompt_sha256`` / ``prompt_context_sha256``
    The exact production prompt string, and the exact bounded facts embedded in
    it. This is the layer that closes a real hole: the digest projection omits
    the signal summary, so two cases could share a ``context_sha256`` while
    sending different bytes to the model. Isolation is asserted on BOTH layers.

Honesty boundary
----------------
Preparation proves design, not causation. A prepared matrix is engineering
evidence. Final SB-V04-002/SB-V04-004 acceptance requires the five real adaptive
invocations, which require a fresh owner authorization plus the lead manifest.
Snapshots carry an explicit ``provenance_label``; anything not ``live-capture``
marks the whole prepared matrix ``acceptance_eligible = False`` and is labeled
engineering-only in every artifact this module writes.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path

from . import authorization, reasoning_cli
from .reasoning import ReasoningContext, ReasoningProposal, validate_proposal
from .reasoning_receipt import (
    ReceiptError,
    bounded_context,
    context_digest,
    differing_variables,
    proposal_divergence,
    proposal_from_receipt,
    validate_receipt,
)

MATRIX_SCHEMA_VERSION = "v1"

LIVE_CAPTURE = "live-capture"
ENGINEERING_FIXTURE = "engineering-fixture"

# The artifact/run identity a live batch would have to be authorized against.
BATCH_ARTIFACTS = ("SB-V04-002", "SB-V04-004")

# (case_id, persona_slot, evidence_id, role)
CASE_SPECS = (
    ("P0", "baseline", "E1", "persona-baseline"),
    ("P1", "variant_b", "E1", "persona-only-variant"),
    ("P2", "variant_c", "E1", "persona-only-variant"),
    ("P3", "cultural", "E1", "persona-only-variant-cultural"),
    ("E0", "baseline", "E2", "evidence-only-variant"),
)

# (case_a, case_b, the single variable that may differ)
REQUIRED_COMPARISONS = (
    ("P0", "P1", "persona"),
    ("P0", "P2", "persona"),
    ("P0", "P3", "persona"),
    ("P0", "E0", "evidence"),
)

PERSONA_SLOTS = ("baseline", "variant_b", "variant_c", "cultural")


class MatrixError(Exception):
    """Raised when a matrix is malformed, non-isolated, or internally inconsistent."""


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _sha256_text(text: str) -> str:
    return _sha256_bytes(text.encode("utf-8"))


def _sha256_json(obj) -> str:
    return _sha256_text(json.dumps(obj, sort_keys=True, separators=(",", ":")))


def _atomic_write_text(path: Path, text: str) -> None:
    """Write via temp + fsync + replace.

    A prepared matrix is immutable and ``write_prepared`` refuses to overwrite,
    so a half-written file from a crash would be unrecoverable without deleting
    evidence. Either the whole artifact exists or none of it does.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(text)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


# --------------------------------------------------------------------------- #
# Evidence snapshots
# --------------------------------------------------------------------------- #
@dataclass
class EvidenceSnapshot:
    """One frozen evidence capture, bound to its raw bytes and capture receipt.

    ``provenance_label`` is the honesty switch. Only ``live-capture`` snapshots
    can ever back an acceptance claim; an ``engineering-fixture`` snapshot makes
    the whole prepared matrix explicitly engineering-only.
    """

    snapshot_id: str
    signal: dict
    raw_bytes_sha256: str
    receipt: dict
    captured_at: str
    provenance_label: str = ENGINEERING_FIXTURE

    @staticmethod
    def from_bytes(snapshot_id: str, signal: dict, raw: bytes, receipt: dict,
                   *, provenance_label: str = ENGINEERING_FIXTURE,
                   captured_at: str | None = None) -> "EvidenceSnapshot":
        return EvidenceSnapshot(
            snapshot_id=snapshot_id,
            signal=dict(signal),
            raw_bytes_sha256=_sha256_bytes(raw),
            receipt=dict(receipt),
            captured_at=captured_at or _now_iso(),
            provenance_label=provenance_label,
        )

    @property
    def receipt_sha256(self) -> str:
        return _sha256_json(self.receipt)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["receipt_sha256"] = self.receipt_sha256
        return data


# --------------------------------------------------------------------------- #
# Prepared cases
# --------------------------------------------------------------------------- #
@dataclass
class PreparedCase:
    case_id: str
    role: str
    persona_slot: str
    persona_id: str
    evidence_id: str
    bounded_context: dict
    context_sha256: str
    prompt: str
    prompt_sha256: str
    prompt_context: dict
    prompt_context_sha256: str
    evidence_bytes_sha256: str
    evidence_receipt_sha256: str
    evidence_provenance: str

    def to_dict(self, *, include_prompt: bool = True) -> dict:
        data = asdict(self)
        if not include_prompt:
            # The full prompt is large and identical in structure across cases;
            # the digests remain, so an audit can still re-derive and compare it.
            data.pop("prompt")
        return data


def _context_for(persona: dict, snapshot: EvidenceSnapshot, *, objective: str,
                 pending_count: int, is_duplicate: bool, prior_hypotheses: int,
                 draft: dict) -> ReasoningContext:
    return ReasoningContext(
        persona=persona,
        objective=objective,
        top_signal=snapshot.signal,
        pending_count=pending_count,
        is_duplicate=is_duplicate,
        draft=draft,
        state_summary={"hypotheses": prior_hypotheses},
    )


@dataclass
class PreparedMatrix:
    """The immutable, hashed, isolation-checked five-case matrix."""

    schema_version: str
    run_scope: str
    lane: str
    artifacts: list[str]
    prepared_at: str
    objective: str
    held_constant: dict
    provider_config: dict
    provider_config_sha256: str
    cases: list[PreparedCase]
    snapshots: list[dict]
    acceptance_eligible: bool
    engineering_only_reasons: list[str] = field(default_factory=list)

    def case(self, case_id: str) -> PreparedCase:
        for c in self.cases:
            if c.case_id == case_id:
                return c
        raise MatrixError(f"no case {case_id!r} in prepared matrix")

    def to_dict(self, *, include_prompt: bool = False) -> dict:
        return {
            "schema_version": self.schema_version,
            "run_scope": self.run_scope,
            "lane": self.lane,
            "artifacts": list(self.artifacts),
            "prepared_at": self.prepared_at,
            "objective": self.objective,
            "held_constant": self.held_constant,
            "provider_config": self.provider_config,
            "provider_config_sha256": self.provider_config_sha256,
            "planned_call_count": len(self.cases),
            "required_comparisons": [list(c) for c in REQUIRED_COMPARISONS],
            "cases": [c.to_dict(include_prompt=include_prompt) for c in self.cases],
            "snapshots": self.snapshots,
            "acceptance_eligible": self.acceptance_eligible,
            "engineering_only_reasons": list(self.engineering_only_reasons),
            "live_execution_performed": False,
            "note": ("PREPARE-ONLY artifact. No adaptive/model provider was "
                     "constructed or invoked while building this matrix."),
        }


def build_matrix(*, personas: dict[str, dict], snapshots: dict[str, EvidenceSnapshot],
                 objective: str, run_scope: str, lane: str,
                 pending_count: int = 0, is_duplicate: bool = False,
                 prior_hypotheses: int = 0, draft: dict | None = None,
                 provider_config: dict | None = None) -> PreparedMatrix:
    """Build the five prepared cases with their bounded contexts, prompts and hashes.

    ``personas`` is keyed by the slots in ``PERSONA_SLOTS``. ``snapshots`` must
    contain ``E1`` and ``E2``. Nothing is invoked; nothing is written.
    """
    missing_slots = [s for s in PERSONA_SLOTS if s not in personas]
    if missing_slots:
        raise MatrixError(f"missing persona slots {missing_slots}")
    missing_snaps = [s for s in ("E1", "E2") if s not in snapshots]
    if missing_snaps:
        raise MatrixError(f"missing evidence snapshots {missing_snaps}")

    draft = draft if draft is not None else {}
    held_constant = {
        "objective": objective,
        "pending_count": pending_count,
        "is_duplicate": is_duplicate,
        "prior_hypotheses": prior_hypotheses,
        "allowed_actions_vocabulary": list(reasoning_cli.ACTION_VOCAB),
        "public_effect_allowed": False,
        "policy_posture": "adaptive-required, fail-closed, no public effect",
    }
    provider_config = provider_config or {
        "provider_mode": "claude-cli",
        "provider_id": "claude-code-subscription-v1",
        "auth_route": "existing-subscription",
        "anthropic_api_key_expected_absent": True,
        "injected_runner": False,
        "model": None,
        "timeout_s": reasoning_cli.DEFAULT_TIMEOUT_S,
        "retry_allowed": False,
    }

    cases: list[PreparedCase] = []
    for case_id, slot, evidence_id, role in CASE_SPECS:
        persona = personas[slot]
        snapshot = snapshots[evidence_id]
        ctx = _context_for(persona, snapshot, objective=objective,
                           pending_count=pending_count, is_duplicate=is_duplicate,
                           prior_hypotheses=prior_hypotheses, draft=draft)
        bounded = bounded_context(ctx)
        prompt = reasoning_cli.build_prompt(ctx)
        prompt_ctx = reasoning_cli.prompt_context(ctx)
        cases.append(PreparedCase(
            case_id=case_id, role=role, persona_slot=slot,
            persona_id=persona.get("id"), evidence_id=evidence_id,
            bounded_context=bounded,
            context_sha256=context_digest(bounded),
            prompt=prompt,
            prompt_sha256=_sha256_text(prompt),
            prompt_context=prompt_ctx,
            prompt_context_sha256=_sha256_json(prompt_ctx),
            evidence_bytes_sha256=snapshot.raw_bytes_sha256,
            evidence_receipt_sha256=snapshot.receipt_sha256,
            evidence_provenance=snapshot.provenance_label,
        ))

    reasons: list[str] = []
    for sid in ("E1", "E2"):
        if snapshots[sid].provenance_label != LIVE_CAPTURE:
            reasons.append(
                f"snapshot {sid} provenance is {snapshots[sid].provenance_label!r}, "
                f"not {LIVE_CAPTURE!r}: engineering-only, not acceptance evidence")

    matrix = PreparedMatrix(
        schema_version=MATRIX_SCHEMA_VERSION,
        run_scope=run_scope, lane=lane, artifacts=list(BATCH_ARTIFACTS),
        prepared_at=_now_iso(), objective=objective, held_constant=held_constant,
        provider_config=provider_config,
        provider_config_sha256=_sha256_json(provider_config),
        cases=cases,
        snapshots=[snapshots["E1"].to_dict(), snapshots["E2"].to_dict()],
        acceptance_eligible=not reasons,
        engineering_only_reasons=reasons,
    )
    # A matrix that is not isolated is not a matrix; refuse to hand one back.
    verify_isolation(matrix)
    return matrix


# --------------------------------------------------------------------------- #
# Single-variable isolation, checked on BOTH layers.
# --------------------------------------------------------------------------- #
def _prompt_payload_differences(a: dict, b: dict) -> set[str]:
    """Top-level keys that differ in the exact bounded facts sent to the model."""
    return {k for k in set(a) | set(b) if a.get(k) != b.get(k)}


_VARIABLE_TO_PROMPT_KEY = {"persona": "persona", "evidence": "signal"}


def isolation_report(matrix: PreparedMatrix) -> dict:
    """Per-comparison isolation evidence, plus a whole-matrix verdict.

    Two independent checks per comparison:

    * digest layer — exactly the expected variable differs in the bounded context
      projection (this is the layer the acceptance metric compares on);
    * prompt layer — exactly the corresponding key differs in the bounded facts
      actually embedded in the production prompt.

    Both must hold. The prompt layer catches a difference the digest projection
    cannot see (for example a changed signal summary), which would otherwise let a
    "persona-only" comparison silently vary the evidence too.
    """
    comparisons = []
    all_isolated = True
    for case_a, case_b, expected in REQUIRED_COMPARISONS:
        a, b = matrix.case(case_a), matrix.case(case_b)
        digest_diff = differing_variables(a.bounded_context, b.bounded_context)
        prompt_diff = _prompt_payload_differences(a.prompt_context, b.prompt_context)
        expected_prompt_key = _VARIABLE_TO_PROMPT_KEY[expected]
        digest_ok = digest_diff == {expected}
        prompt_ok = prompt_diff == {expected_prompt_key}
        isolated = digest_ok and prompt_ok
        all_isolated = all_isolated and isolated
        comparisons.append({
            "comparison": f"{case_a}|{case_b}",
            "expected_variable": expected,
            "isolated": isolated,
            "digest_layer": {
                "ok": digest_ok,
                "differing_variables": sorted(digest_diff),
                "context_sha256_a": a.context_sha256,
                "context_sha256_b": b.context_sha256,
            },
            "prompt_layer": {
                "ok": prompt_ok,
                "differing_keys": sorted(prompt_diff),
                "expected_key": expected_prompt_key,
                "prompt_sha256_a": a.prompt_sha256,
                "prompt_sha256_b": b.prompt_sha256,
            },
        })
    # Every case must be a distinct call: two identical contexts would make one of
    # the five invocations redundant and silently weaken the matrix.
    digests = [c.context_sha256 for c in matrix.cases]
    distinct_contexts = len(set(digests)) == len(digests)
    return {
        "all_isolated": all_isolated and distinct_contexts,
        "distinct_contexts": distinct_contexts,
        "case_count": len(matrix.cases),
        "comparisons": comparisons,
    }


def verify_isolation(matrix: PreparedMatrix) -> dict:
    """Raise ``MatrixError`` unless every required comparison is single-variable."""
    report = isolation_report(matrix)
    if not report["all_isolated"]:
        broken = [c["comparison"] for c in report["comparisons"] if not c["isolated"]]
        detail = f"non-isolated comparisons {broken}" if broken else \
            "two or more cases share an identical bounded context"
        raise MatrixError(f"single-variable isolation violated: {detail}")
    return report


# --------------------------------------------------------------------------- #
# Receipt validation + material-divergence reporting.
# --------------------------------------------------------------------------- #
def _proposal_for_case(matrix: PreparedMatrix, case_id: str, receipt: dict
                       ) -> tuple[ReasoningProposal | None, list[str]]:
    """Validate a receipt, bind it to its case by digest, rebuild its proposal."""
    errs = validate_receipt(receipt)
    if errs:
        return None, [f"{case_id}: invalid receipt: " + "; ".join(errs)]
    case = matrix.case(case_id)
    if receipt.get("context_digest") != case.context_sha256:
        return None, [f"{case_id}: receipt context_digest {receipt.get('context_digest')!r} "
                      f"does not bind to the prepared case context {case.context_sha256!r}"]
    try:
        proposal = proposal_from_receipt(receipt)
    except ReceiptError as exc:
        return None, [f"{case_id}: receipt could not be replayed: {exc}"]
    perrs = validate_proposal(proposal)
    if perrs:
        return None, [f"{case_id}: reconstructed proposal failed schema validation: "
                      + "; ".join(perrs)]
    return proposal, []


def divergence_report(matrix: PreparedMatrix, receipts: dict[str, dict],
                      budget: "authorization.CallBudget | None" = None) -> dict:
    """Validate per-case receipts and report material divergence per comparison.

    Truthful by construction: a missing, invalid or non-binding receipt is
    recorded as such and the comparison is reported ``material = False`` with a
    reason. Nothing is rerun, and a failed comparison is never retried into a
    pass — that is the no-retry rule applied at the reporting layer.

    ``acceptance_evidence_eligible`` additionally requires ``budget``: a ledger
    showing that each case's context digest was actually reserved and returned a
    proposal under a named manifest. ``receipt_kind`` and ``provenance_label`` are
    self-declared strings in caller-supplied files, so on their own they prove
    nothing — anyone can write ``"sanitized-real-canary"`` into a JSON file.
    Without a budget the report says eligibility is unproven and why, rather than
    taking those labels at face value.
    """
    errors: list[str] = []
    proposals: dict[str, ReasoningProposal] = {}
    case_rows = []
    for case_id, _slot, _evidence_id, _role in CASE_SPECS:
        receipt = receipts.get(case_id)
        if receipt is None:
            errors.append(f"{case_id}: no receipt supplied")
            case_rows.append({"case": case_id, "receipt_present": False,
                              "receipt_kind": None, "valid": False})
            continue
        proposal, perrs = _proposal_for_case(matrix, case_id, receipt)
        if perrs:
            errors.extend(perrs)
        else:
            proposals[case_id] = proposal
        case_rows.append({
            "case": case_id,
            "receipt_present": True,
            "receipt_kind": receipt.get("receipt_kind"),
            "provider_id": receipt.get("provider_id"),
            "valid": proposal is not None,
            "recommended_action": proposal.recommended_action if proposal else None,
        })

    comparisons = []
    for case_a, case_b, expected in REQUIRED_COMPARISONS:
        if case_a not in proposals or case_b not in proposals:
            comparisons.append({
                "comparison": f"{case_a}|{case_b}", "variable": expected,
                "material": False,
                "reason": "one or both receipts are missing or invalid",
            })
            continue
        diff = proposal_divergence(proposals[case_a], proposals[case_b])
        diff.update({"comparison": f"{case_a}|{case_b}", "variable": expected,
                     "reason": None if diff["material"] else
                     "proposals are identical on recommended action, ranking and estimates"})
        comparisons.append(diff)

    kinds = {r.get("receipt_kind") for r in receipts.values() if isinstance(r, dict)}
    all_real = bool(receipts) and kinds == {"sanitized-real-canary"}
    all_material = bool(comparisons) and all(c["material"] for c in comparisons)

    # Bind every case to a consumed call slot that actually returned a proposal.
    binding: dict = {"checked": budget is not None, "unbound_cases": [],
                     "manifest_ids": []}
    if budget is None:
        binding["reason"] = ("no call-budget ledger supplied; receipt labels alone "
                             "cannot establish that any live call was made")
        all_bound = False
    else:
        slots = budget.slots()
        by_digest = {sl.get("context_digest"): sl for sl in slots
                     if sl.get("outcome") == "proposal_received"}
        unbound = [c.case_id for c in matrix.cases if c.context_sha256 not in by_digest]
        binding["unbound_cases"] = unbound
        binding["manifest_ids"] = sorted({sl.get("manifest_id") for sl in slots
                                          if sl.get("manifest_id")})
        binding["slots_consumed"] = budget.consumed()
        all_bound = not unbound
        if unbound:
            binding["reason"] = (f"no recorded call slot returned a proposal for "
                                 f"cases {unbound}")
    return {
        "run_scope": matrix.run_scope,
        "generated_at": _now_iso(),
        "cases": case_rows,
        "comparisons": comparisons,
        "errors": errors,
        "all_comparisons_material": all_material,
        "receipt_kinds": sorted(k for k in kinds if k),
        "all_receipts_real_adaptive": all_real,
        "call_slot_binding": binding,
        # The only combination that could back an empirical acceptance claim, and
        # even then acceptance is the lead's to grant, never this report's.
        "acceptance_evidence_eligible": bool(
            all_material and all_real and all_bound and not errors
            and matrix.acceptance_eligible),
        "acceptance_authority": "ChatGPT lead — this report never self-accepts",
    }


# --------------------------------------------------------------------------- #
# Immutable on-disk artifact.
# --------------------------------------------------------------------------- #
def write_prepared(matrix: PreparedMatrix, path: str | Path, *,
                   include_prompt: bool = False) -> Path:
    """Write the prepared matrix once. Refuses to overwrite (the artifact is immutable)."""
    path = Path(path)
    if path.exists():
        raise MatrixError(f"refusing to overwrite existing prepared matrix at {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = matrix.to_dict(include_prompt=include_prompt)
    payload["isolation"] = isolation_report(matrix)
    text = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    _atomic_write_text(path, text)
    return path


def load_prepared(path: str | Path, prompts_dir: str | Path | None = None
                  ) -> PreparedMatrix:
    """Rebuild a ``PreparedMatrix`` from a written artifact, for re-verification.

    ``prompts_dir`` supplies each case's exact prompt text so ``prompt_sha256``
    can be recomputed from bytes rather than trusted. Without it the prompt is
    left empty and only the context/prompt-context digests are re-derivable.
    """
    path = Path(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    prompts_dir = Path(prompts_dir) if prompts_dir is not None else None
    cases: list[PreparedCase] = []
    for row in payload["cases"]:
        prompt = row.get("prompt", "")
        if not prompt and prompts_dir is not None:
            candidate = prompts_dir / f"{row['case_id']}.prompt.txt"
            if candidate.exists():
                prompt = candidate.read_text(encoding="utf-8")
        cases.append(PreparedCase(prompt=prompt, **{
            k: row[k] for k in (
                "case_id", "role", "persona_slot", "persona_id", "evidence_id",
                "bounded_context", "context_sha256", "prompt_sha256",
                "prompt_context", "prompt_context_sha256", "evidence_bytes_sha256",
                "evidence_receipt_sha256", "evidence_provenance")}))
    return PreparedMatrix(
        schema_version=payload["schema_version"], run_scope=payload["run_scope"],
        lane=payload["lane"], artifacts=payload["artifacts"],
        prepared_at=payload["prepared_at"], objective=payload["objective"],
        held_constant=payload["held_constant"],
        provider_config=payload["provider_config"],
        provider_config_sha256=payload["provider_config_sha256"],
        cases=cases, snapshots=payload["snapshots"],
        acceptance_eligible=payload["acceptance_eligible"],
        engineering_only_reasons=payload.get("engineering_only_reasons", []))


def verify_written(path: str | Path, prompts_dir: str | Path | None = None) -> dict:
    """Independently re-derive every digest in a written matrix and re-check isolation.

    Recomputes each digest from the recorded content instead of trusting the
    recorded digest, so a hand-edited artifact fails verification.
    """
    matrix = load_prepared(path, prompts_dir)
    digest_errors: list[str] = []
    for case in matrix.cases:
        checks = [
            ("context_sha256", context_digest(case.bounded_context), case.context_sha256),
            ("prompt_context_sha256", _sha256_json(case.prompt_context),
             case.prompt_context_sha256),
        ]
        if case.prompt:
            checks.append(("prompt_sha256", _sha256_text(case.prompt), case.prompt_sha256))
        for name, recomputed, recorded in checks:
            if recomputed != recorded:
                digest_errors.append(
                    f"{case.case_id}: {name} recorded {recorded} but content hashes to "
                    f"{recomputed}")
    provider_digest = _sha256_json(matrix.provider_config)
    if provider_digest != matrix.provider_config_sha256:
        digest_errors.append("provider_config_sha256 does not match provider_config")
    prompt_verified = all(bool(c.prompt) for c in matrix.cases)
    if not prompt_verified:
        # The prompt file is the actual payload and the layer that closes the
        # summary hole. A verdict that ignored it would pass a matrix whose
        # prompt files had been edited to smuggle different evidence.
        digest_errors.append(
            "prompt bytes were not verified: pass the prompts directory so each "
            "case's exact prompt can be re-hashed from disk")
    # A batch must use one provider configuration; a per-case override would make
    # any observed divergence attributable to configuration, not to the variable.
    report = isolation_report(matrix)
    return {
        "path": str(path),
        "digests_verified": not digest_errors,
        "prompt_bytes_verified": prompt_verified,
        "digest_errors": digest_errors,
        "isolation": report,
        "verified": bool(not digest_errors and report["all_isolated"]),
    }


def write_prompts(matrix: PreparedMatrix, directory: str | Path) -> list[Path]:
    """Write each case's exact production prompt next to its digest, once."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for case in matrix.cases:
        p = directory / f"{case.case_id}.prompt.txt"
        if p.exists():
            raise MatrixError(f"refusing to overwrite existing prompt at {p}")
        _atomic_write_text(p, case.prompt)
        written.append(p)
    digests = directory / "PROMPT_DIGESTS.json"
    if digests.exists():
        raise MatrixError(f"refusing to overwrite existing digests at {digests}")
    _atomic_write_text(digests, json.dumps({
        c.case_id: {
            "prompt_sha256": c.prompt_sha256,
            "prompt_context_sha256": c.prompt_context_sha256,
            "context_sha256": c.context_sha256,
            "evidence_bytes_sha256": c.evidence_bytes_sha256,
            "evidence_receipt_sha256": c.evidence_receipt_sha256,
        } for c in matrix.cases
    }, indent=2, sort_keys=True) + "\n")
    written.append(digests)
    return written


# --------------------------------------------------------------------------- #
# Live execution — gated, budgeted, no-retry. Currently ALWAYS fails closed.
# --------------------------------------------------------------------------- #
def _execute_one_case(case: PreparedCase, provider, budget: authorization.CallBudget,
                      *, grant: authorization.ExecutionGrant, draft: dict,
                      persona: dict, objective: str, snapshot_signal: dict,
                      pending_count: int, is_duplicate: bool,
                      prior_hypotheses: int) -> dict:
    """Reserve a slot, invoke ONCE, record the outcome truthfully. Never retries.

    ATOMIC PRE-SPAWN ACCOUNTING: the slot is reserved before ``provider.propose``
    is called, so a crash mid-call still consumes the authorization. There is no
    except-and-retry branch anywhere in this function by design — an unavailable
    provider, a malformed envelope or a schema failure is an outcome, not a cue to
    try again.

    Not a public entry point: callers must go through ``execute_batch`` so the
    authorization gate cannot be skipped. Tests exercise this directly with an
    injected provider, which is engineering-only evidence.
    """
    # BIND FIRST. The context is rebuilt from caller-supplied personas/snapshots,
    # so without this check the batch could invoke something other than what was
    # prepared, hashed and isolation-checked — and the budget slot would still
    # record the prepared digest, making the ledger assert a call that never
    # happened. The whole isolation proof only means something if the thing
    # invoked is the thing prepared. Checked before reserving, so a mismatch
    # costs no authorization.
    ctx = ReasoningContext(
        persona=persona, objective=objective, top_signal=snapshot_signal,
        pending_count=pending_count, is_duplicate=is_duplicate, draft=draft,
        state_summary={"hypotheses": prior_hypotheses})
    actual_digest = context_digest(bounded_context(ctx))
    if actual_digest != case.context_sha256:
        raise MatrixError(
            f"{case.case_id}: refusing to invoke a context that does not match the "
            f"prepared case (prepared {case.context_sha256}, actual {actual_digest})")
    actual_prompt_digest = _sha256_json(reasoning_cli.prompt_context(ctx))
    if actual_prompt_digest != case.prompt_context_sha256:
        raise MatrixError(
            f"{case.case_id}: refusing to invoke a prompt payload that does not match "
            f"the prepared case (prepared {case.prompt_context_sha256}, actual "
            f"{actual_prompt_digest})")

    slot = budget.reserve(manifest_id=grant.manifest_id,
                          manifest_digest=grant.manifest_digest,
                          lane=grant.lane, artifact=grant.artifact,
                          context_digest=case.context_sha256)
    try:
        proposal = provider.propose(ctx)
    except Exception as exc:                          # noqa: BLE001 - outcome, not retry
        budget.record_outcome(slot, "provider_exception",
                              {"error_type": type(exc).__name__})
        return {"case": case.case_id, "slot": slot.slot, "outcome": "provider_exception",
                "proposal": None}
    if proposal is None:
        budget.record_outcome(slot, "provider_unavailable",
                              {"reason": getattr(provider, "reason", None)})
        return {"case": case.case_id, "slot": slot.slot,
                "outcome": "provider_unavailable", "proposal": None}
    errs = validate_proposal(proposal, ctx)
    if errs:
        budget.record_outcome(slot, "invalid_proposal", {"violations": errs[:10]})
        return {"case": case.case_id, "slot": slot.slot, "outcome": "invalid_proposal",
                "proposal": None, "violations": errs}
    budget.record_outcome(slot, "proposal_received", {
        "recommended_action": proposal.recommended_action,
        "provider_id": proposal.provider_id,
        "adaptive": proposal.adaptive,
    })
    return {"case": case.case_id, "slot": slot.slot, "outcome": "proposal_received",
            "proposal": proposal}


def execute_batch(matrix: PreparedMatrix, *, lane: str, artifact: str = "SB-V04-002",
                  personas: dict[str, dict] | None = None,
                  snapshots: dict[str, EvidenceSnapshot] | None = None,
                  provider_factory=None, manifest_dir: str | Path | None = None,
                  home: str | Path | None = None, draft: dict | None = None) -> dict:
    """Run the authorized five-call batch, or fail closed before spawning anything.

    The FIRST action is the authorization gate. With no canonical lead manifest on
    disk — the current and expected V0.4 state — this raises
    ``authorization.AuthorizationDenied`` before a provider is constructed, before
    a budget directory is touched and before any subprocess exists.

    Passing ``provider_factory`` sets ``injected_runner=True`` on the gate, which a
    manifest cannot waive: a real authorized batch must use the real provider.
    """
    grant = authorization.authorize(
        artifact=artifact, lane=lane, run_scope=matrix.run_scope,
        manifest_dir=manifest_dir, injected_runner=provider_factory is not None)

    if grant.max_calls < len(matrix.cases):
        raise authorization.AuthorizationDenied(
            f"manifest authorizes {grant.max_calls} calls but the matrix plans "
            f"{len(matrix.cases)}; refusing to execute a partial batch")

    if personas is None or snapshots is None:
        raise MatrixError("execute_batch requires the personas and snapshots the "
                          "matrix was built from, to rebuild exact contexts")

    budget = authorization.CallBudget(matrix.run_scope, grant.max_calls, home=home)
    provider = provider_factory() if provider_factory is not None else \
        reasoning_cli.ClaudeCodeReasoningProvider()

    results = []
    for case in matrix.cases:
        results.append(_execute_one_case(
            case, provider, budget, grant=grant, draft=draft or {},
            persona=personas[case.persona_slot], objective=matrix.objective,
            snapshot_signal=snapshots[case.evidence_id].signal,
            pending_count=matrix.held_constant["pending_count"],
            is_duplicate=matrix.held_constant["is_duplicate"],
            prior_hypotheses=matrix.held_constant["prior_hypotheses"]))
    return {"grant": asdict(grant), "results": results, "budget": budget.audit()}


def prepare_only_status(matrix: PreparedMatrix, *, lane: str,
                        manifest_dir: str | Path | None = None,
                        home: str | Path | None = None) -> dict:
    """The full prepare-only verdict: isolation, hashes, gate state and budget state.

    This is what the prepare CLI emits and what a worker report cites. It states
    plainly that no live execution occurred.
    """
    budget = authorization.CallBudget(matrix.run_scope, len(matrix.cases), home=home)
    gates = {
        art: authorization.gate_status(artifact=art, lane=lane,
                                       run_scope=matrix.run_scope,
                                       manifest_dir=manifest_dir)
        for art in BATCH_ARTIFACTS
    }
    return {
        "run_scope": matrix.run_scope,
        "lane": lane,
        "generated_at": _now_iso(),
        "planned_call_count": len(matrix.cases),
        "isolation": isolation_report(matrix),
        "case_digests": {
            c.case_id: {
                "context_sha256": c.context_sha256,
                "prompt_sha256": c.prompt_sha256,
                "prompt_context_sha256": c.prompt_context_sha256,
                "evidence_bytes_sha256": c.evidence_bytes_sha256,
                "evidence_receipt_sha256": c.evidence_receipt_sha256,
                "evidence_provenance": c.evidence_provenance,
            } for c in matrix.cases
        },
        "authorization_gate": gates,
        "live_execution_permitted": all(g["live_execution_permitted"] for g in gates.values()),
        "live_execution_performed": False,
        "call_budget": budget.audit(),
        "acceptance_eligible": matrix.acceptance_eligible,
        "engineering_only_reasons": list(matrix.engineering_only_reasons),
        "empirical_acceptance_state": (
            "BLOCKED_OWNER_AUTHORIZATION — SB-V04-002 and SB-V04-004 require five "
            "real adaptive invocations that are not authorized; this artifact "
            "prepares them and proves the gate holds, and claims nothing more"),
    }
