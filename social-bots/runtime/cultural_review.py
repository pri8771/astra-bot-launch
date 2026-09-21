"""Cultural-review evidence binding (SB-R07-053 / SB-V05-004).

Cultural personas require an attributable named review bound to the exact
candidate, the evidence/source set used, and a reviewer identity+version.
Missing, failed, or unknown reviews WITHHOLD the candidate. Callers cannot
self-grant an ACCEPTED cultural pass without a complete binding record.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Iterable

from .jsonstore import now_iso

ACCEPTED = "ACCEPTED"
WITHHELD = "WITHHELD"
FAILED = "FAILED"
UNKNOWN = "UNKNOWN"

_PASSING = {ACCEPTED}
_FAIL_CLOSED = {WITHHELD, FAILED, UNKNOWN, None, ""}


@dataclass(frozen=True)
class CulturalReviewBinding:
    """Attributable cultural-review evidence record.

    Required fields bind the review to one candidate + evidence set + reviewer.
    ``status`` must be an explicit decision; absent/unknown fails closed.
    """
    candidate_id: str
    reviewer_id: str
    reviewer_version: str
    evidence_refs: tuple
    status: str
    rationale: str = ""
    reviewed_at: str = ""
    policy_ref: str = "persona.source_requirements.named_reviewer"
    advertising_disallowed: bool = True

    def as_dict(self) -> dict:
        d = asdict(self)
        d["evidence_refs"] = list(self.evidence_refs)
        return d


def _normalize_refs(refs: Iterable | None) -> tuple:
    out = []
    for r in refs or ():
        if isinstance(r, str) and r.strip():
            out.append(r.strip())
        elif isinstance(r, dict) and (r.get("receipt_id") or r.get("url") or r.get("source_url")):
            out.append(r.get("receipt_id") or r.get("url") or r.get("source_url"))
    return tuple(out)


def make_binding(*, candidate_id: str, reviewer_id: str, reviewer_version: str,
                 evidence_refs, status: str, rationale: str = "",
                 reviewed_at: str | None = None,
                 policy_ref: str = "persona.source_requirements.named_reviewer"
                 ) -> CulturalReviewBinding:
    """Construct a binding; does not itself grant operational acceptance."""
    return CulturalReviewBinding(
        candidate_id=candidate_id,
        reviewer_id=reviewer_id,
        reviewer_version=reviewer_version,
        evidence_refs=_normalize_refs(evidence_refs),
        status=(status or UNKNOWN).upper(),
        rationale=rationale or "",
        reviewed_at=reviewed_at or now_iso(),
        policy_ref=policy_ref,
        advertising_disallowed=True,
    )


def binding_from_candidate(candidate: dict) -> CulturalReviewBinding | None:
    """Load a CulturalReviewBinding from candidate fields if present."""
    raw = candidate.get("cultural_review_binding")
    if raw is None:
        return None
    if isinstance(raw, CulturalReviewBinding):
        return raw
    if not isinstance(raw, dict):
        return None
    try:
        return CulturalReviewBinding(
            candidate_id=raw.get("candidate_id") or candidate.get("content_id") or "",
            reviewer_id=raw.get("reviewer_id") or "",
            reviewer_version=raw.get("reviewer_version") or "",
            evidence_refs=_normalize_refs(raw.get("evidence_refs") or []),
            status=(raw.get("status") or UNKNOWN).upper(),
            rationale=raw.get("rationale") or "",
            reviewed_at=raw.get("reviewed_at") or now_iso(),
            policy_ref=raw.get("policy_ref") or "persona.source_requirements.named_reviewer",
            advertising_disallowed=bool(raw.get("advertising_disallowed", True)),
        )
    except Exception:
        return None


def validate_binding(binding: CulturalReviewBinding | None, *,
                     candidate_id: str, required_reviewer: str | None,
                     source_refs: list | tuple) -> tuple[bool, str, str]:
    """Return ``(passed, status, reason)`` for a cultural review binding.

    Fail closed when:
    - no binding is present;
    - required named reviewer is missing from persona policy;
    - binding reviewer_id does not match the persona's named_reviewer;
    - reviewer_version is empty;
    - candidate_id mismatches;
    - evidence_refs empty or do not cover candidate source_refs;
    - status is FAILED / WITHHELD / UNKNOWN / missing;
    - advertising_disallowed is somehow flipped off (contract invariant).
    """
    if not required_reviewer:
        return False, WITHHELD, "no named cultural reviewer bound on persona policy"

    if binding is None:
        return False, UNKNOWN, "cultural review binding missing; fail closed"

    if not binding.reviewer_id or not binding.reviewer_version:
        return False, UNKNOWN, "cultural reviewer identity/version incomplete"

    if binding.reviewer_id != required_reviewer:
        return False, FAILED, (
            f"binding reviewer {binding.reviewer_id!r} does not match "
            f"persona named_reviewer {required_reviewer!r}")

    if not binding.candidate_id or binding.candidate_id != candidate_id:
        return False, FAILED, "cultural review not bound to this candidate_id"

    if not binding.evidence_refs:
        return False, UNKNOWN, "cultural review has no evidence_refs"

    sources = {s for s in (source_refs or []) if s}
    if sources and not sources.issubset(set(binding.evidence_refs)):
        return False, FAILED, "cultural review evidence_refs omit candidate source_refs"

    if not binding.advertising_disallowed:
        return False, FAILED, "cultural review must disallow disguised advertising"

    status = (binding.status or UNKNOWN).upper()
    if status in _FAIL_CLOSED or status not in _PASSING:
        return False, status if status in {FAILED, WITHHELD, UNKNOWN} else UNKNOWN, (
            f"cultural review status={status}; fail closed")

    return True, ACCEPTED, (
        f"named reviewer {binding.reviewer_id}@{binding.reviewer_version} "
        f"accepted over {len(binding.evidence_refs)} evidence ref(s)")


def evaluate_cultural_review(persona: dict, candidate: dict) -> dict:
    """Pipeline-facing cultural review with evidence binding (SB-R07-053)."""
    sr = persona.get("source_requirements", {}) or {}
    required = (persona.get("kind") == "cultural"
                or bool(sr.get("cultural_review_required")))
    if not required:
        return {"check": "cultural", "required": False, "passed": True,
                "status": "NOT_REQUIRED",
                "reason": "not a cultural persona",
                "binding": None}

    required_reviewer = sr.get("named_reviewer")
    candidate_id = candidate.get("content_id") or ""
    source_refs = list(candidate.get("source_refs") or [])
    binding = binding_from_candidate(candidate)
    passed, status, reason = validate_binding(
        binding,
        candidate_id=candidate_id,
        required_reviewer=required_reviewer,
        source_refs=source_refs,
    )
    return {
        "check": "cultural",
        "required": True,
        "passed": passed,
        "status": status,
        "reason": reason,
        "binding": binding.as_dict() if binding is not None else None,
        "required_reviewer": required_reviewer,
        "candidate_id": candidate_id,
        "source_refs": source_refs,
    }
