"""SB-V04-004 — sanitized adaptive-proposal RECEIPT seam.

This module is the clean acceptance seam that lets the V0.4 persona/evidence
divergence acceptance suite consume the **sanitized real adaptive receipt** that
the SB-V04-005 canary produces, and REPLAY it through the exact same adaptive
provider path the production engine uses — WITHOUT this (Core) lane making another
live model/provider call.

Why a receipt seam exists
-------------------------
Final V0.4 acceptance requires proof that the *adaptive* route (``adaptive=True``)
materially diverges for persona-only and evidence-only changes. The one authorized
live subscription invocation is reserved for SB-V04-005 (a different lane). So this
lane records nothing live; it consumes a sanitized receipt of that real proposal
and replays it deterministically. The replay:

* goes through ``ModelReasoningProvider`` (``adaptive=True``) via
  ``reasoning.register_model_callable`` — the same seam SB-R1C production wiring
  uses — so the engine's schema validation, authority wall, policy ranking and
  no-public-effect boundary all still apply unchanged;
* fails closed (returns ``None`` -> ``BLOCKED_REASONING_UNAVAILABLE``) when no
  receipt matches the context, so a missing/invalid receipt never fabricates
  adaptive output;
* never grants authority: a receipt is inert data. Any authority key anywhere in
  a receipt is rejected before it can be reconstructed into a proposal.

Honesty boundary
----------------
A receipt is tagged ``receipt_kind``:

* ``sanitized-real-canary`` — a sanitized capture of the real SB-V04-005 adaptive
  proposal. Only this kind may back a *final adaptive acceptance* claim.
* ``synthetic-seam-fixture`` — a hand-authored fixture used ONLY to exercise this
  seam's own machinery (load/validate/reject-authority/isolation/divergence). It
  is never real-model evidence and must never be represented as the canary.

This module does not fabricate, and cannot self-accept: it only loads, validates
and replays. No network, no subprocess, no spend.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .reasoning import (
    ACTION_VOCAB,
    Candidate,
    ReasoningContext,
    ReasoningProposal,
    _AUTHORITY_KEYS,
    validate_candidate,
)

RECEIPT_SCHEMA_VERSION = "v0.4"
REAL_CANARY_KIND = "sanitized-real-canary"
SEAM_FIXTURE_KIND = "synthetic-seam-fixture"
_ALLOWED_KINDS = (REAL_CANARY_KIND, SEAM_FIXTURE_KIND)

# Canonical intake location where Lane 3 drops the sanitized SB-V04-005 receipt(s).
# The acceptance suite auto-consumes real-canary receipts found here.
REAL_CANARY_RECEIPT_DIR = (
    Path(__file__).resolve().parent.parent / "acceptance" / "sb-v04-005-receipts"
)

_REQUIRED_ENVELOPE = (
    "schema_version", "receipt_kind", "provider_id", "adaptive",
    "generated_at", "context_digest", "context", "alternatives",
    "recommended_action", "uncertainties", "evidence_refs",
)
_REQUIRED_CONTEXT = (
    "persona", "objective", "signal", "pending_count",
    "is_duplicate", "prior_hypotheses",
)
_NUMERIC_ALT_FIELDS = (
    "expected_value", "expected_learning", "relevance", "confidence",
    "risk", "cost", "reversibility", "duplication_risk",
)

# Named independent variables of a single-signal reasoning cycle. The acceptance
# suite holds all-but-one of these constant to prove isolated divergence.
VARIABLES = ("persona", "evidence", "objective", "pending_count",
             "is_duplicate", "prior_hypotheses")


class ReceiptError(Exception):
    """Raised when a receipt is missing required structure or smuggles authority."""


# --------------------------------------------------------------------------- #
# Bounded context + digest. The receipt binds to the exact bounded context it was
# generated for, so replay matches by digest and the acceptance suite can check
# that exactly one independent variable differs between two contexts.
# --------------------------------------------------------------------------- #
def bounded_context(ctx: ReasoningContext) -> dict:
    """The inert, bounded projection of a context (mirrors the CLI provider)."""
    sig = ctx.top_signal or {}
    persona = ctx.persona or {}
    return {
        "persona": {
            "id": persona.get("id"),
            "kind": persona.get("kind"),
            "display_name": persona.get("display_name"),
        },
        "objective": ctx.objective,
        "signal": {
            "id": sig.get("id"),
            "title": sig.get("title"),
            "tags": sorted(sig.get("tags", []) or []),
            "provenance": sig.get("provenance"),
            "has_source": bool(sig.get("url") or sig.get("source")),
        },
        "pending_count": ctx.pending_count,
        "is_duplicate": ctx.is_duplicate,
        "prior_hypotheses": int((ctx.state_summary or {}).get("hypotheses", 0)),
    }


def context_digest(bounded: dict) -> str:
    """Stable digest of a bounded context block (order-independent)."""
    return "sha256:" + hashlib.sha256(
        json.dumps(bounded, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def differing_variables(bounded_a: dict, bounded_b: dict) -> set[str]:
    """Return the set of named independent variables that differ between contexts."""
    differ: set[str] = set()
    if bounded_a.get("persona") != bounded_b.get("persona"):
        differ.add("persona")
    if bounded_a.get("signal") != bounded_b.get("signal"):
        differ.add("evidence")
    for name in ("objective", "pending_count", "is_duplicate", "prior_hypotheses"):
        if bounded_a.get(name) != bounded_b.get(name):
            differ.add(name)
    return differ


def assert_single_variable(bounded_a: dict, bounded_b: dict, expected: str) -> None:
    """Assert exactly the ``expected`` variable differs; raise otherwise.

    This is the guard that makes a divergence test HONEST: it proves the two
    contexts are identical except for the one variable under test, so any observed
    proposal difference is attributable to that variable alone.
    """
    if expected not in VARIABLES:
        raise ReceiptError(f"unknown variable {expected!r}")
    differ = differing_variables(bounded_a, bounded_b)
    if differ != {expected}:
        raise ReceiptError(
            f"expected ONLY {expected!r} to differ, but differing variables are "
            f"{sorted(differ) or 'none'} (isolation violated)")


# --------------------------------------------------------------------------- #
# Receipt validation. A receipt must be inert, adaptive, schema-clean, and must
# not fabricate evidence refs or smuggle authority.
# --------------------------------------------------------------------------- #
def _find_authority_keys(obj) -> set[str]:
    """Recursively find any authority key anywhere in a receipt (defense-in-depth)."""
    found: set[str] = set()
    if isinstance(obj, dict):
        found |= _AUTHORITY_KEYS.intersection(obj.keys())
        for v in obj.values():
            found |= _find_authority_keys(v)
    elif isinstance(obj, list):
        for v in obj:
            found |= _find_authority_keys(v)
    return found


def _candidate_from_alt(alt: dict, signal: dict | None) -> Candidate:
    """Reconstruct a Candidate from a receipt alternative (inert payload only)."""
    action = alt.get("action")
    payload: dict = {}
    if action == "CREATE_CANDIDATE":
        # Attach only the inert signal reference the receipt was generated for, so
        # the reconstructed proposal satisfies the CREATE_CANDIDATE payload rule
        # WITHOUT the receipt supplying any executable payload of its own.
        payload = {"signal": signal or {"id": (alt.get("evidence_refs") or [None])[0]}}
    return Candidate(
        action=action,
        rationale=str(alt.get("rationale", "")),
        expected_value=alt.get("expected_value"),
        expected_learning=alt.get("expected_learning"),
        relevance=alt.get("relevance"),
        confidence=alt.get("confidence"),
        risk=alt.get("risk"),
        cost=alt.get("cost"),
        reversibility=alt.get("reversibility"),
        duplication_risk=alt.get("duplication_risk"),
        payload=payload,
    )


def validate_receipt(receipt: dict) -> list[str]:
    """Return a list of contract violations ([] means the receipt is valid)."""
    if not isinstance(receipt, dict):
        return [f"receipt is not an object: {type(receipt).__name__}"]
    errs: list[str] = []

    # Authority can never appear in a receipt, anywhere.
    smuggled = _find_authority_keys(receipt)
    if smuggled:
        errs.append(f"receipt smuggles authority keys {sorted(smuggled)}")

    for field in _REQUIRED_ENVELOPE:
        if field not in receipt:
            errs.append(f"missing envelope field {field!r}")
    if errs:
        return errs  # structural gaps make deeper checks unsafe

    if receipt["schema_version"] != RECEIPT_SCHEMA_VERSION:
        errs.append(f"schema_version {receipt['schema_version']!r} != {RECEIPT_SCHEMA_VERSION!r}")
    if receipt["receipt_kind"] not in _ALLOWED_KINDS:
        errs.append(f"receipt_kind {receipt['receipt_kind']!r} not in {_ALLOWED_KINDS}")
    if receipt["adaptive"] is not True:
        errs.append("adaptive must be True (a receipt only represents the adaptive route)")
    if not isinstance(receipt["provider_id"], str) or not receipt["provider_id"].strip():
        errs.append("provider_id must be a non-empty string")
    if not isinstance(receipt["uncertainties"], list):
        errs.append("uncertainties must be a list")

    ctx = receipt["context"]
    if not isinstance(ctx, dict):
        errs.append("context must be an object")
        return errs
    for field in _REQUIRED_CONTEXT:
        if field not in ctx:
            errs.append(f"context missing {field!r}")
    signal = ctx.get("signal") if isinstance(ctx.get("signal"), dict) else {}
    signal_id = signal.get("id")

    # context_digest must match the context block (integrity / anti-tamper).
    normalized = {
        "persona": ctx.get("persona"),
        "objective": ctx.get("objective"),
        "signal": {
            "id": signal.get("id"),
            "title": signal.get("title"),
            "tags": sorted(signal.get("tags", []) or []),
            "provenance": signal.get("provenance"),
            "has_source": bool(signal.get("has_source")),
        },
        "pending_count": ctx.get("pending_count"),
        "is_duplicate": ctx.get("is_duplicate"),
        "prior_hypotheses": ctx.get("prior_hypotheses"),
    }
    if receipt["context_digest"] != context_digest(normalized):
        errs.append("context_digest does not match context block")

    alts = receipt["alternatives"]
    if not isinstance(alts, list) or not alts:
        errs.append("alternatives must be a non-empty list")
        return errs

    actions: set[str] = set()
    for i, alt in enumerate(alts):
        if not isinstance(alt, dict):
            errs.append(f"alternative[{i}] is not an object")
            continue
        for f in _NUMERIC_ALT_FIELDS:
            if f not in alt:
                errs.append(f"alternative[{i}] ({alt.get('action')}) missing numeric {f!r}")
        # evidence refs may not fabricate: the only evidence in a single-signal
        # cycle is the context signal id.
        refs = alt.get("evidence_refs", [])
        if not isinstance(refs, list):
            errs.append(f"alternative[{i}] evidence_refs must be a list")
        else:
            bad = [r for r in refs if r != signal_id]
            if bad:
                errs.append(f"alternative[{i}] cites non-context evidence refs {bad}")
        cand = _candidate_from_alt(alt, signal)
        errs.extend(f"alternative[{i}]: {e}" for e in validate_candidate(cand))
        if cand.action in ACTION_VOCAB:
            actions.add(cand.action)

    recommended = receipt["recommended_action"]
    if recommended not in ACTION_VOCAB:
        errs.append(f"recommended_action {recommended!r} not in vocabulary")
    elif recommended not in actions:
        errs.append(f"recommended_action {recommended!r} not among alternatives")

    top_refs = receipt["evidence_refs"]
    if not isinstance(top_refs, list):
        errs.append("evidence_refs must be a list")
    else:
        bad = [r for r in top_refs if r != signal_id]
        if bad:
            errs.append(f"top-level evidence_refs cite non-context refs {bad}")
    return errs


def proposal_from_receipt(receipt: dict, ctx: ReasoningContext | None = None
                          ) -> ReasoningProposal:
    """Reconstruct an adaptive ReasoningProposal from a validated receipt.

    ``ctx`` (when replaying inside a live cycle) supplies the real inert signal +
    draft for a CREATE_CANDIDATE payload, mirroring the CLI provider. The returned
    proposal is re-validated by the engine (``reasoning.validate_proposal``) before
    it is ever scored or executed.
    """
    errs = validate_receipt(receipt)
    if errs:
        raise ReceiptError("; ".join(errs))
    live_signal = (ctx.top_signal if ctx is not None else None)
    live_draft = (ctx.draft if ctx is not None else None)
    receipt_signal = receipt["context"].get("signal") or {}
    alts: list[Candidate] = []
    for alt in receipt["alternatives"]:
        cand = _candidate_from_alt(alt, receipt_signal)
        if cand.action == "CREATE_CANDIDATE":
            cand.payload = {"signal": live_signal or receipt_signal,
                            "draft": live_draft if live_draft is not None else {}}
        alts.append(cand)
    return ReasoningProposal(
        alternatives=alts,
        recommended_action=receipt["recommended_action"],
        uncertainties=[str(u) for u in receipt["uncertainties"]],
        provider_id=receipt["provider_id"],
        adaptive=True,
    )


# --------------------------------------------------------------------------- #
# Replay callable — register with ``reasoning.register_model_callable`` and set
# ``SBOTS_REASONING=model`` to run the adaptive path end-to-end from receipts.
# --------------------------------------------------------------------------- #
class ReceiptReplay:
    """Policy-owned replay of already-recorded real receipts. Calls nothing.

    ``model_dispatch`` exempts this EXACT type from live accounting because it
    cannot perform a model call: it only returns the receipt whose context digest
    matches the live context, or ``None`` (fail closed). A subclass or a look-alike
    object is classified LIVE and refused without a grant.
    """

    def __init__(self, receipts: list[dict]):
        index: dict[str, dict] = {}
        for r in receipts:
            errs = validate_receipt(r)
            if errs:
                raise ReceiptError("cannot index invalid receipt: " + "; ".join(errs))
            index[r["context_digest"]] = r
        self._index = index

    @property
    def receipt_count(self) -> int:
        return len(self._index)

    def __call__(self, ctx: ReasoningContext) -> ReasoningProposal | None:
        digest = context_digest(bounded_context(ctx))
        receipt = self._index.get(digest)
        if receipt is None:
            return None
        return proposal_from_receipt(receipt, ctx)


def replay_callable(receipts: list[dict]) -> ReceiptReplay:
    """Build a model callable that returns the receipt matching a live context.

    Returns ``None`` (fail closed) when no receipt matches the context digest, so
    an unmatched cycle blocks rather than fabricating adaptive output.
    """
    return ReceiptReplay(receipts)


# --------------------------------------------------------------------------- #
# Divergence detection — a proposal materially diverges from another if the
# recommended action, the ranked order, or any per-alternative estimate differs.
# --------------------------------------------------------------------------- #
def _ranking(proposal: ReasoningProposal) -> list[str]:
    return [c.action for c in sorted(proposal.alternatives,
                                     key=lambda c: c.score(), reverse=True)]


def _estimate_map(proposal: ReasoningProposal) -> dict:
    return {c.action: (c.expected_value, c.expected_learning, c.relevance,
                       c.confidence, c.risk, c.cost, c.reversibility,
                       c.duplication_risk)
            for c in proposal.alternatives}


def proposal_divergence(a: ReasoningProposal, b: ReasoningProposal) -> dict:
    """Describe how two proposals differ; ``material`` is True if any dimension does."""
    recommended_changed = a.recommended_action != b.recommended_action
    ranking_changed = _ranking(a) != _ranking(b)
    estimates_changed = _estimate_map(a) != _estimate_map(b)
    return {
        "recommended_changed": recommended_changed,
        "ranking_changed": ranking_changed,
        "estimates_changed": estimates_changed,
        "material": recommended_changed or ranking_changed or estimates_changed,
        "recommended_a": a.recommended_action,
        "recommended_b": b.recommended_action,
        "ranking_a": _ranking(a),
        "ranking_b": _ranking(b),
    }


# --------------------------------------------------------------------------- #
# Loading real sanitized receipts from disk.
# --------------------------------------------------------------------------- #
def load_receipt(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        receipt = json.load(fh)
    errs = validate_receipt(receipt)
    if errs:
        raise ReceiptError(f"invalid receipt {path}: " + "; ".join(errs))
    return receipt


def load_real_canary_receipts(directory: str | Path | None = None) -> list[dict]:
    """Load all ``sanitized-real-canary`` receipts from the intake directory.

    Returns an empty list when the directory is absent or holds no real receipts
    (the expected state until SB-V04-005 has run) — callers treat empty as
    "adaptive acceptance pending the real canary", never as a pass.
    """
    directory = Path(directory) if directory is not None else REAL_CANARY_RECEIPT_DIR
    if not directory.is_dir():
        return []
    out: list[dict] = []
    for p in sorted(directory.glob("*.json")):
        receipt = load_receipt(p)
        if receipt.get("receipt_kind") == REAL_CANARY_KIND:
            out.append(receipt)
    return out


def build_receipt(*, bounded: dict, alternatives: list[dict], recommended_action: str,
                  uncertainties: list[str], provider_id: str, generated_at: str,
                  receipt_kind: str, proposal_id: str,
                  evidence_refs: list | None = None) -> dict:
    """Assemble a receipt dict with a correct context_digest.

    Used to sanitize a real SB-V04-005 proposal into a receipt, and (with
    ``receipt_kind=SEAM_FIXTURE_KIND``) to author seam fixtures in tests. It only
    assembles structure; the caller supplies already-sanitized content.
    """
    signal_id = (bounded.get("signal") or {}).get("id")
    return {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "receipt_kind": receipt_kind,
        "source_task": "SB-V04-005",
        "proposal_id": proposal_id,
        "provider_id": provider_id,
        "adaptive": True,
        "generated_at": generated_at,
        "context_digest": context_digest(bounded),
        "context": bounded,
        "alternatives": alternatives,
        "recommended_action": recommended_action,
        "uncertainties": list(uncertainties),
        "evidence_refs": evidence_refs if evidence_refs is not None else [signal_id],
    }
