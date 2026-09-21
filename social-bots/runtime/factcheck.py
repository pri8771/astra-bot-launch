"""Claim-to-source factual support review (SB-V05-002).

The accepted V0.3 fact check only asked "is a source URL present?". This module
answers the harder, correct question: **is each material factual claim actually
supported by captured evidence, as judged by an attributable assessor?**

SB-V05-002 repair contract (INTELLIGENCE_WAVE1 §2 + LEAD-014)
-----------------------------------------------------------
1. **The caller does not get to assert an operational ``stance=supports``.** A
   support stance is produced by a :class:`SupportAssessor` — an attributable
   assessor with an identity and version. A stance only counts as *operational*
   when it comes from an assessor whose class is registered as operational
   (``register_operational_assessor``). A caller-declared / fixture stance
   (:class:`ManualAssessor`) is retained but explicitly ``operational=False`` and
   never grants support for gating.
2. **Every support assessment binds** claim -> evidence excerpt/span/hash ->
   assessor identity/version -> support status.
3. **No operational assessor => UNKNOWN/WITHHELD.** A required factual claim
   backed only by non-operational assessments is withheld.
4. **Material claims are identified, not merely trusted from the caller.** A
   bounded, inspectable :class:`ClaimExtractor` scans the candidate text for
   material factual claims. Any material factual claim the caller did not
   enumerate is added and gated, so omitting a claim from the caller's bindings
   cannot bypass factual review.

Staleness (unchanged): a support assessment only counts if the current capture
receipt is verified AND its content hash still matches the hash recorded when the
claim was assessed. A changed source hash invalidates stale support until
re-review.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from typing import Protocol, runtime_checkable

# Claim kinds.
FACTUAL = "factual"
OPINION = "opinion"
CREATIVE = "creative"

# Assessment stances (how a piece of evidence relates to a claim).
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
    detect staleness. ``content_hash`` is the hash recorded at assessment time."""
    receipt_id: str
    source_url: str
    content_hash: str
    retrieved_at: str


@dataclass(frozen=True)
class EvidenceItem:
    """Caller-supplied *candidate* evidence for a claim.

    The caller may point at evidence (a captured receipt + the excerpt/span it
    believes is relevant), but the caller does NOT decide whether it supports the
    claim — that is the assessor's job.
    """
    ref: EvidenceRef
    excerpt: str
    span: tuple | None = None


@dataclass(frozen=True)
class SupportAssessment:
    """An assessor's judgement binding a claim to evidence.

    Binds: claim -> evidence excerpt/span/hash -> assessor identity/version ->
    support status. ``operational`` is set by the framework from the operational
    assessor registry, never by the assessor's own say-so alone.
    """
    claim_id: str
    stance: str
    evidence: EvidenceRef
    excerpt: str
    span: tuple | None
    assessor_name: str
    assessor_version: str
    operational: bool
    rationale: str = ""


# Backwards-compatible alias: a binding IS an assessor's assessment now.
ClaimBinding = SupportAssessment


# --------------------------------------------------------------------------- #
# Attributable support assessors.
# --------------------------------------------------------------------------- #
@runtime_checkable
class SupportAssessor(Protocol):
    name: str
    version: str
    operational: bool

    def assess(self, claim: Claim, item: EvidenceItem) -> str:
        """Return a stance (SUPPORTS / PARTIAL_STANCE / REFUTES / UNRELATED)."""
        ...


_OPERATIONAL_ASSESSOR_CLASSES: set[type] = set()


def register_operational_assessor(cls: type) -> type:
    """Register (and return) an assessor class as an operational assessor.

    Operational stance can only be produced by an explicitly registered
    assessor — a caller cannot make an assessment operational by merely setting
    ``operational = True`` on an ad-hoc object.
    """
    _OPERATIONAL_ASSESSOR_CLASSES.add(cls)
    return cls


def is_operational_assessor(assessor: object) -> bool:
    return (type(assessor) in _OPERATIONAL_ASSESSOR_CLASSES
            and bool(getattr(assessor, "operational", False)))


_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "at", "for",
    "is", "are", "was", "were", "be", "been", "it", "its", "this", "that",
    "these", "those", "when", "then", "than", "with", "as", "by", "from",
}


def _key_terms(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w for w in words if len(w) > 3 and w not in _STOPWORDS]


@register_operational_assessor
class KeywordSupportAssessor:
    """A deterministic, inspectable operational assessor.

    It is not a language model; it decides a stance by checking whether the
    claim's key terms appear in the cited evidence excerpt, and by detecting
    explicit refutation cues. It is deliberately simple and auditable — its
    rationale names exactly which terms/cues drove the stance. It is a real
    attributable assessor (identity + version), registered as operational.
    """
    name = "keyword-support-assessor"
    version = "1.0.0"
    operational = True

    _REFUTE_CUES = ("no evidence", "not supported", "is false", "refut",
                    "debunk", "myth", "disproven", "contradict")

    def assess(self, claim: Claim, item: EvidenceItem) -> str:
        text = (item.excerpt or "").lower()
        if any(cue in text for cue in self._REFUTE_CUES):
            return REFUTES
        terms = _key_terms(claim.text)
        if not terms:
            return UNRELATED
        hits = [t for t in terms if t in text]
        if len(hits) == len(terms):
            return SUPPORTS
        if hits:
            return PARTIAL_STANCE
        return UNRELATED


class ManualAssessor:
    """A fixture / test-only assessor that echoes a caller-declared stance.

    It is NOT registered as operational, so any assessment it produces is
    ``operational=False`` and cannot grant support for gating. This is how a
    caller-declared stance stays explicitly test-only.
    """
    name = "manual-fixture-assessor"
    version = "0.0.0-test"
    operational = False

    def __init__(self, stances: dict):
        # stances maps (claim_id, receipt_id) -> stance, or claim_id -> stance.
        self._stances = stances

    def assess(self, claim: Claim, item: EvidenceItem) -> str:
        key = (claim.id, item.ref.receipt_id)
        if key in self._stances:
            return self._stances[key]
        return self._stances.get(claim.id, UNRELATED)


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


def assess_bindings(claim: Claim, items: list[EvidenceItem],
                    assessor: SupportAssessor) -> list[SupportAssessment]:
    """Run ``assessor`` over each evidence item to produce support assessments.

    The stance comes from the assessor; ``operational`` is derived from the
    operational-assessor registry, not from the assessor's own attribute alone.
    """
    operational = is_operational_assessor(assessor)
    out = []
    for item in items:
        stance = assessor.assess(claim, item)
        out.append(SupportAssessment(
            claim_id=claim.id,
            stance=stance,
            evidence=item.ref,
            excerpt=item.excerpt,
            span=item.span,
            assessor_name=getattr(assessor, "name", "unknown"),
            assessor_version=getattr(assessor, "version", "unknown"),
            operational=operational,
            rationale=f"{getattr(assessor, 'name', 'unknown')} stance={stance}",
        ))
    return out


def _binding_valid(b: SupportAssessment, current_hashes: dict) -> tuple[bool, str]:
    """A binding is valid iff the receipt is currently verified and its content
    hash is unchanged since the claim was assessed."""
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
    used_evidence: list = field(default_factory=list)     # EvidenceRef dicts
    stale_evidence: list = field(default_factory=list)     # {evidence, reason}
    non_operational_evidence: list = field(default_factory=list)
    assessors: list = field(default_factory=list)          # attributions used
    reason: str = ""

    def as_dict(self) -> dict:
        return asdict(self)


# SB-V16-001 and other consumers refer to a claim's support result by this name.
ClaimSupportResult = ClaimResult


def assess_claim(claim: Claim, bindings: list[SupportAssessment],
                 current_hashes: dict) -> ClaimResult:
    """Determine a claim's support status from its *operational*, valid,
    non-stale assessments. Non-operational (fixture/manual) assessments never
    grant support."""
    mine = [b for b in bindings if b.claim_id == claim.id]

    # Opinion / creative claims are not evidence-gated.
    if claim.kind in (OPINION, CREATIVE):
        return ClaimResult(claim.id, claim.kind, claim.required, status=UNKNOWN,
                           reason=f"{claim.kind} framing is not an evidence-gated claim")

    operational = [b for b in mine if b.operational]
    non_operational = [b for b in mine if not b.operational]
    non_op_refs = [{"evidence": asdict(b.evidence),
                    "assessor": b.assessor_name} for b in non_operational]

    if not operational:
        # No operational assessor spoke to this claim -> UNKNOWN (packet: no
        # assessor operationally => UNKNOWN/WITHHELD when required).
        reason = ("no evidence bound" if not mine
                  else "only non-operational (fixture/manual) assessments; "
                       "an operational assessor is required")
        return ClaimResult(claim.id, claim.kind, claim.required, UNKNOWN,
                           non_operational_evidence=non_op_refs, reason=reason)

    valid, stale = [], []
    for b in operational:
        ok, why = _binding_valid(b, current_hashes)
        (valid if ok else stale).append((b, why))
    stale_refs = [{"evidence": asdict(b.evidence), "reason": why}
                  for b, why in stale]

    if not valid:
        return ClaimResult(
            claim.id, claim.kind, claim.required, UNSUPPORTED,
            stale_evidence=stale_refs,
            non_operational_evidence=non_op_refs,
            reason="all operational evidence is stale/unverified; re-review required")

    stances = {b.stance for b, _ in valid}
    assessors = sorted({f"{b.assessor_name}@{b.assessor_version}" for b, _ in valid})
    supporting = [asdict(b.evidence) for b, _ in valid
                  if b.stance in (SUPPORTS, PARTIAL_STANCE)]

    has_pos = bool(stances & {SUPPORTS, PARTIAL_STANCE})
    has_neg = REFUTES in stances

    if has_pos and has_neg:
        status, reason = CONFLICTED, "supporting and refuting operational evidence conflict"
    elif SUPPORTS in stances:
        status, reason = SUPPORTED, "supported by operational assessor over verified evidence"
    elif PARTIAL_STANCE in stances:
        status, reason = PARTIAL, "only partial support from operational assessor"
    elif has_neg:
        status, reason = UNSUPPORTED, "operational evidence refutes the claim"
    else:  # only UNRELATED — URL present but nothing backs the claim
        status, reason = UNSUPPORTED, "operational assessor: bound evidence does not support the claim"

    return ClaimResult(
        claim.id, claim.kind, claim.required, status,
        used_evidence=supporting or [asdict(b.evidence) for b, _ in valid],
        stale_evidence=stale_refs,
        non_operational_evidence=non_op_refs,
        assessors=assessors,
        reason=reason)


# A required factual claim must reach one of these to allow the candidate.
_PASSING = {SUPPORTED, PARTIAL}


@dataclass
class FactReview:
    passed: bool
    status: str                       # overall
    withheld_reason: str
    claim_results: list               # ClaimResult dicts
    identified_claims: list = field(default_factory=list)  # auto-identified

    def as_dict(self) -> dict:
        return asdict(self)


def review_claims(claims: list[Claim], bindings: list[SupportAssessment],
                  current_hashes: dict) -> FactReview:
    """Review the given claims; withhold if any REQUIRED FACTUAL claim is not
    supported by operational, non-stale evidence.

    This reviews exactly the claims passed in. Use :func:`review_candidate` to
    also identify material claims the caller omitted.
    """
    results = [assess_claim(c, bindings, current_hashes) for c in claims]
    failing = [r for r in results
               if r.kind == FACTUAL and r.required and r.status not in _PASSING]
    if failing:
        ids = ", ".join(f"{r.claim_id}:{r.status}" for r in failing)
        return FactReview(
            passed=False, status="WITHHELD",
            withheld_reason=f"required factual claim(s) not supported: {ids}",
            claim_results=[r.as_dict() for r in results])
    return FactReview(passed=True, status="OK", withheld_reason="",
                      claim_results=[r.as_dict() for r in results])


# --------------------------------------------------------------------------- #
# Material-claim identification (LEAD-014: callers cannot bypass by omission).
# --------------------------------------------------------------------------- #
@runtime_checkable
class ClaimExtractor(Protocol):
    def identify(self, text: str) -> list[Claim]: ...


# Inspectable marker vocabularies — deliberately bounded and auditable.
_OPINION_MARKERS = (
    "i think", "i believe", "in my opinion", "imho", "we love", "i love",
    "amazing", "gorgeous", "beautiful", "the best ever", "worst ever",
    "you should", "you must", "feels like",
)
_CREATIVE_MARKERS = (
    "once upon a time", "imagine if", "picture this", "in a fictional",
    "let's pretend", "a tale of",
)
_FACTUAL_PHRASES = (
    "according to", "study", "studies", "research", "data", "percent",
    "increase", "increased", "decrease", "decreased", "reduce", "reduced",
    "cause", "causes", "found that", "shows that", "reported", "confirmed",
    "launched", "released", "founded", "acquired", "valued at", "million",
    "billion", "record", "fastest", "largest", "first ever",
)
_YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
_NUM_RE = re.compile(r"\d")
_SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def _classify_sentence(sentence: str) -> str | None:
    """Classify a sentence; return a kind, or None if it is not a material claim."""
    low = sentence.lower()
    if any(m in low for m in _CREATIVE_MARKERS):
        return CREATIVE
    if any(m in low for m in _OPINION_MARKERS):
        return OPINION
    has_number = bool(_NUM_RE.search(sentence)) or bool(_YEAR_RE.search(sentence))
    has_phrase = any(p in low for p in _FACTUAL_PHRASES)
    if has_number or has_phrase:
        return FACTUAL
    return None  # not a material, gate-worthy claim


class HeuristicClaimExtractor:
    """A bounded, inspectable material-claim identifier.

    It splits candidate text into sentences and flags factual assertions
    (containing numbers/years or factual phrasing) as material claims, while
    marking clearly subjective/creative sentences as opinion/creative. It is not
    a language model; every decision is driven by the inspectable marker lists
    above, so a reviewer can audit exactly why a sentence was flagged.
    """
    name = "heuristic-claim-extractor"
    version = "1.0.0"

    def identify(self, text: str) -> list[Claim]:
        claims: list[Claim] = []
        for i, raw in enumerate(_SENT_SPLIT_RE.split(text or "")):
            sentence = raw.strip()
            if not sentence:
                continue
            kind = _classify_sentence(sentence)
            if kind is None:
                continue
            claims.append(Claim(id=f"auto-{i}", text=sentence, kind=kind,
                                required=(kind == FACTUAL)))
        return claims


def _normalize(text: str) -> set[str]:
    return set(_key_terms(text))


def _covers(caller: Claim, auto: Claim) -> bool:
    """True if a caller-enumerated claim covers an auto-identified claim."""
    a, b = _normalize(caller.text), _normalize(auto.text)
    if not b:
        return False
    if a == b:
        return True
    overlap = len(a & b) / len(b)
    return overlap >= 0.6


def reconcile_claims(caller_claims: list[Claim], text: str,
                     extractor: ClaimExtractor | None = None
                     ) -> tuple[list[Claim], list[Claim]]:
    """Merge caller claims with material claims identified from ``text``.

    Returns ``(final_claims, added_claims)``. Any material FACTUAL claim the
    caller did not enumerate is added as a required factual claim so it must be
    reviewed — omission cannot bypass factual review.
    """
    extractor = extractor or HeuristicClaimExtractor()
    identified = extractor.identify(text)
    added: list[Claim] = []
    for auto in identified:
        if auto.kind != FACTUAL:
            continue
        if not any(_covers(c, auto) for c in caller_claims):
            added.append(auto)
    return list(caller_claims) + added, added


def review_candidate(text: str, caller_claims: list[Claim],
                     bindings: list[SupportAssessment], current_hashes: dict,
                     *, extractor: ClaimExtractor | None = None) -> FactReview:
    """End-to-end review: identify material claims from the candidate ``text``,
    merge with the caller's claims, then gate.

    A material factual claim the caller omitted is added with no bindings, so it
    resolves to UNKNOWN and (being required) withholds the candidate — proving a
    caller cannot bypass factual review by omitting a claim.
    """
    final_claims, added = reconcile_claims(caller_claims, text, extractor)
    review = review_claims(final_claims, bindings, current_hashes)
    # Added claims are required+factual with no bindings, so review_claims has
    # already resolved them to UNKNOWN and withheld the candidate.
    review.identified_claims = [asdict(c) for c in added]
    return review
