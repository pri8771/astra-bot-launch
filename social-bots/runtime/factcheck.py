"""Claim-to-source factual support review (SB-V05-002).

The accepted V0.3 fact check only asked "is a source URL present?". This module
answers the harder, correct question: **is each material factual claim actually
supported by captured evidence?**

Design principles
-----------------
- A *claim* is classified: factual / opinion / creative. Only factual claims are
  subject to evidence support; opinions and creative framing are not gated.
- Support is computed from explicit, stance-tagged bindings to *verified*
  capture receipts (SB-V05-001), never guessed. Each binding preserves the
  evidence's source URL, retrieval timestamp and content hash.
- A binding only counts if the current capture receipt is verified AND its
  content hash still matches the hash recorded when the claim was reviewed. A
  changed source hash invalidates stale support until re-review.
- A URL being present is NOT support: a claim bound only to unrelated evidence is
  UNSUPPORTED.
- A required factual claim that is not SUPPORTED (or PARTIAL) withholds the
  candidate.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict

# Claim kinds.
FACTUAL = "factual"
OPINION = "opinion"
CREATIVE = "creative"

# Binding stances (how a piece of evidence relates to a claim).
SUPPORTS = "supports"
PARTIAL_STANCE = "partial"
REFUTES = "refutes"
UNRELATED = "unrelated"

# Support statuses (packet vocabulary).
SUPPORTED = "SUPPORTED"
PARTIAL = "PARTIAL"
UNSUPPORTED = "UNSUPPORTED"
CONFLICTED = "CONFLICTED"
UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Claim:
    id: str
    text: str
    kind: str = FACTUAL
    required: bool = True


@dataclass(frozen=True)
class EvidenceRef:
    """A reference to a captured evidence receipt, with the facts needed to
    detect staleness. ``content_hash`` is the hash recorded at review time."""
    receipt_id: str
    source_url: str
    content_hash: str
    retrieved_at: str


@dataclass(frozen=True)
class ClaimBinding:
    claim_id: str
    stance: str
    evidence: EvidenceRef
    note: str = ""


def evidence_ref_from_receipt(receipt) -> EvidenceRef:
    """Build an EvidenceRef from a verified SB-V05-001 capture receipt."""
    if not receipt.is_verified_capture():
        raise ValueError("cannot bind a claim to an unverified capture receipt")
    return EvidenceRef(
        receipt_id=receipt.receipt_id,
        source_url=receipt.source_url,
        content_hash=receipt.content_hash,
        retrieved_at=receipt.retrieved_at,
    )


def _binding_valid(b: ClaimBinding, current_hashes: dict) -> tuple[bool, str]:
    """A binding is valid iff the receipt is currently verified and its content
    hash is unchanged since the claim was reviewed."""
    current = current_hashes.get(b.evidence.receipt_id)
    if current is None:
        return False, "evidence-unverified-or-missing"
    if current != b.evidence.content_hash:
        return False, "stale-hash-changed"
    return True, "valid"


@dataclass
class ClaimResult:
    claim_id: str
    kind: str
    required: bool
    status: str
    used_evidence: list = field(default_factory=list)   # EvidenceRef dicts
    stale_evidence: list = field(default_factory=list)   # {ref, reason}
    reason: str = ""

    def as_dict(self) -> dict:
        return asdict(self)


def assess_claim(claim: Claim, bindings: list[ClaimBinding],
                 current_hashes: dict) -> ClaimResult:
    """Determine a claim's support status from its (valid, non-stale) bindings."""
    mine = [b for b in bindings if b.claim_id == claim.id]

    # Opinion / creative claims are not evidence-gated.
    if claim.kind in (OPINION, CREATIVE):
        return ClaimResult(claim.id, claim.kind, claim.required, status="UNKNOWN",
                           reason=f"{claim.kind} framing is not an evidence-gated claim")

    valid, stale = [], []
    for b in mine:
        ok, why = _binding_valid(b, current_hashes)
        (valid if ok else stale).append((b, why))

    stale_refs = [{"evidence": asdict(b.evidence), "reason": why} for b, why in stale]

    if not valid:
        status = UNKNOWN if not mine else UNSUPPORTED
        reason = ("no evidence bound" if not mine
                  else "all bound evidence is stale/unverified; re-review required")
        return ClaimResult(claim.id, claim.kind, claim.required, status,
                           stale_evidence=stale_refs, reason=reason)

    stances = {b.stance for b, _ in valid}
    supporting = [asdict(b.evidence) for b, _ in valid
                  if b.stance in (SUPPORTS, PARTIAL_STANCE)]

    has_pos = bool(stances & {SUPPORTS, PARTIAL_STANCE})
    has_neg = REFUTES in stances

    if has_pos and has_neg:
        status, reason = CONFLICTED, "supporting and refuting evidence conflict"
    elif SUPPORTS in stances:
        status, reason = SUPPORTED, "supported by verified evidence"
    elif PARTIAL_STANCE in stances:
        status, reason = PARTIAL, "only partial support in verified evidence"
    elif has_neg:
        status, reason = UNSUPPORTED, "verified evidence refutes the claim"
    else:  # only UNRELATED bindings — URL present but nothing backs the claim
        status, reason = UNSUPPORTED, "bound evidence does not support the claim"

    return ClaimResult(claim.id, claim.kind, claim.required, status,
                       used_evidence=supporting or [asdict(b.evidence) for b, _ in valid],
                       stale_evidence=stale_refs, reason=reason)


# A required factual claim must reach one of these to allow the candidate.
_PASSING = {SUPPORTED, PARTIAL}


@dataclass
class FactReview:
    passed: bool
    status: str                       # overall
    withheld_reason: str
    claim_results: list               # ClaimResult dicts

    def as_dict(self) -> dict:
        return asdict(self)


def review_claims(claims: list[Claim], bindings: list[ClaimBinding],
                  current_hashes: dict) -> FactReview:
    """Review all claims; withhold if any REQUIRED FACTUAL claim is unsupported.

    ``current_hashes`` maps receipt_id -> the receipt's *current* content hash
    (or None/absent if it is no longer a verified capture). This is what lets a
    changed source hash invalidate previously-recorded support.
    """
    results = [assess_claim(c, bindings, current_hashes) for c in claims]

    failing = [
        r for r in results
        if r.kind == FACTUAL and r.required and r.status not in _PASSING
    ]
    if failing:
        ids = ", ".join(f"{r.claim_id}:{r.status}" for r in failing)
        return FactReview(
            passed=False, status="WITHHELD",
            withheld_reason=f"required factual claim(s) not supported: {ids}",
            claim_results=[r.as_dict() for r in results],
        )
    return FactReview(passed=True, status="OK", withheld_reason="",
                      claim_results=[r.as_dict() for r in results])
