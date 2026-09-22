"""Platform-independent content/experiment pipeline.

Flow: signal -> persona ideation -> fact/voice/cultural review -> platform format
-> dedup -> experiment registration -> publish queue (publishing DISABLED by
default). No operational mock data: candidates are built from real captured
signals and the persona spec. Publishing here only *queues*; it never emits an
external effect.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, replace
from pathlib import Path

from . import paths, factcheck, content_intelligence as ci, cultural_review as cr
from .jsonstore import read_json, write_json, append_jsonl, read_jsonl, now_iso


# --------------------------------------------------------------------------- #
# Ideation — persona-specific, deterministic and inspectable.
# One signal yields DIFFERENT candidates for different personas by construction.
# --------------------------------------------------------------------------- #
def ideate(persona: dict, signal: dict) -> dict:
    voice = persona["voice"]
    sig_move = (voice["signature_moves"] or ["angle"])[0]
    angle = f"{persona['id']}:{sig_move}:{signal['id']}"
    content_id = "c-" + hashlib.sha256(angle.encode()).hexdigest()[:12]
    # Persona-shaped hook/body scaffolds (voice-driven, not a shared template).
    hook = f"[{persona['display_name']}] {signal['title']}"
    body = (
        f"Angle ({sig_move}): {signal['summary']} "
        f"— framed for {persona['target_audience']} in a "
        f"{', '.join(voice['tone'])} voice."
    )
    return {
        "content_id": content_id,
        "bot": persona["runtime"],
        "persona": persona["id"],
        "signal_id": signal["id"],
        "angle": angle,
        "hook": hook,
        "body": body,
        "source_refs": [s for s in [signal.get("url")] if s] or [signal.get("source")],
        "signature_move": sig_move,
        "created_at": now_iso(),
        "status": "ideated",
    }


# --------------------------------------------------------------------------- #
# Reviews
# --------------------------------------------------------------------------- #
def fact_check(persona: dict, candidate: dict) -> dict:
    """Operational claim-to-source factual review (SB-R07-051 / SB-V05-002).

    Routes through :mod:`runtime.factcheck` with the closed
    :class:`BoundedPropositionAssessor`. Callers cannot grant operational
    authority. Fixture/untrusted receipts never yield an operational pass.

    Candidate optional fields:
    - ``claims``: list of :class:`factcheck.Claim` or claim dicts
    - ``evidence_items``: list of :class:`factcheck.EvidenceItem`
    - ``support_assessments``: precomputed assessments (tests / advanced)
    - ``evidence_hashes``: ``{receipt_id: content_hash}`` for staleness
    """
    needs_evidence = persona.get("source_requirements", {}).get("evidence_required", True)
    has_source = bool(candidate.get("source_refs"))
    if not needs_evidence:
        return {"check": "fact", "passed": True, "reason": "evidence not required",
                "operational": False, "mode": "not-required"}

    text = f"{candidate.get('hook', '')} {candidate.get('body', '')}".strip()
    normalized_claims: list = []
    for c in candidate.get("claims") or []:
        if isinstance(c, factcheck.Claim):
            normalized_claims.append(c)
        elif isinstance(c, dict):
            normalized_claims.append(factcheck.Claim(
                id=c["id"], text=c["text"],
                kind=c.get("kind", factcheck.FACTUAL),
                required=c.get("required", True)))

    current_hashes = dict(candidate.get("evidence_hashes") or {})
    evidence_items = list(candidate.get("evidence_items") or [])
    for item in evidence_items:
        ref = item.ref
        current_hashes.setdefault(ref.receipt_id, ref.content_hash)

    bindings = list(candidate.get("support_assessments") or [])
    if evidence_items and not bindings:
        assessor = factcheck.default_operational_assessor()
        final_preview, _ = factcheck.reconcile_claims(normalized_claims, text)
        for claim in final_preview:
            if claim.kind != factcheck.FACTUAL:
                continue
            bindings.extend(factcheck.assess_bindings(claim, evidence_items, assessor))

    review = factcheck.review_candidate(
        text, normalized_claims, bindings, current_hashes)

    material = [r for r in review.claim_results if r.get("kind") == factcheck.FACTUAL]
    if not material and not review.identified_claims:
        ok = has_source
        return {
            "check": "fact", "passed": ok,
            "reason": ("no material factual claims; source ref present"
                       if ok else "no material factual claims; no source ref"),
            "operational": False,
            "mode": "no-material-claims",
            "fact_review": review.as_dict(),
        }

    return {
        "check": "fact",
        "passed": review.passed,
        "reason": review.withheld_reason or review.status,
        "operational": True,
        "mode": "claim-to-source",
        "fact_review": review.as_dict(),
    }


def voice_review(persona: dict, candidate: dict) -> dict:
    banned = [b.replace("-", " ") for b in persona["voice"].get("banned_moves", [])]
    text = f"{candidate['hook']} {candidate['body']}".lower()
    hits = [b for b in banned if b in text]
    return {"check": "voice", "passed": not hits,
            "reason": "clean" if not hits else f"banned-move hit: {hits}"}


def cultural_review(persona: dict, candidate: dict) -> dict:
    """Cultural-review evidence binding gate (SB-R07-053 / SB-V05-004)."""
    return cr.evaluate_cultural_review(persona, candidate)


def review(persona: dict, candidate: dict) -> dict:
    """Draft-level review. Stamps a binding over EXACTLY the inputs reviewed, so a
    later edit to the candidate (or a re-format) is detectable by ``final_review``
    and ``enqueue`` (V1.7 C05/C06)."""
    checks = {
        "fact": fact_check(persona, candidate),
        "voice": voice_review(persona, candidate),
        "cultural": cultural_review(persona, candidate),
    }
    candidate["review"] = checks
    candidate["review_passed"] = all(c["passed"] for c in checks.values())
    candidate["status"] = "reviewed" if candidate["review_passed"] else "withheld"
    candidate["review_binding"] = {"reviewed_sha256": reviewed_digest(candidate),
                                   "reviewed_at": now_iso()}
    return candidate


# --------------------------------------------------------------------------- #
# Platform formatting — hard gate via content_intelligence (SB-R07-052)
# --------------------------------------------------------------------------- #
_LIMITS = {p: c["char_limit"] for p, c in ci.PLATFORM_CONSTRAINTS.items()}


def _concept_from_candidate(candidate: dict):
    """Build a ContentConcept for platform formatting.

    Prefer an explicit concept/segments on the candidate. Legacy hook/body
    candidates are modeled as framing segments (repairable). Fact segments must
    carry acceptable SB-V05-002 bindings and are never silently truncated.
    """
    if candidate.get("content_concept") is not None:
        return candidate["content_concept"]
    if candidate.get("segments"):
        concept = ci.new_concept(candidate["persona"], list(candidate["segments"]),
                                 series_id=candidate.get("series_id"))
        return _stable_concept(concept, candidate)
    segs: list = []
    for fs in candidate.get("fact_segments") or []:
        segs.append(ci.Segment.fact(fs["text"], fs["binding_ref"]))
    if candidate.get("hook"):
        segs.append(ci.Segment.framing(candidate["hook"]))
    if candidate.get("body"):
        segs.append(ci.Segment.framing(candidate["body"]))
    if not segs:
        segs.append(ci.Segment.framing(""))
    concept = ci.new_concept(candidate["persona"], segs, series_id=candidate.get("series_id"))
    return _stable_concept(concept, candidate)


def _stable_concept(concept, candidate: dict):
    """Give a candidate-derived concept a DETERMINISTIC id (V1.7 C05 lineage).

    ``new_concept`` mints a random id, and the platform hashtag tail is derived
    from it, so the same candidate rendered twice produced different final text.
    A reviewer (human cultural review, G-CULTURAL) signs the hash of the text they
    saw; the runtime must be able to render that exact text again. The id is
    therefore a function of persona + content_id, and lineage stays truthful:
    one candidate, one concept.
    """
    if not candidate.get("content_id"):
        return concept
    basis = f"{candidate.get('persona')}|{candidate['content_id']}".encode("utf-8")
    stable_id = "cc-" + hashlib.sha256(basis).hexdigest()[:12]
    try:
        return replace(concept, concept_id=stable_id)
    except TypeError:                                 # not a dataclass instance
        concept.concept_id = stable_id
        return concept


def format_for_platform(candidate: dict, platform: str) -> dict:
    """Platform-native formatting gate (SB-R07-052 / SB-V05-003).

    Uses :mod:`runtime.content_intelligence` exclusively — no parallel
    formatter. Facts are preserved verbatim; over-limit framing is repaired by
    dropping framing; facts that cannot fit cause WITHHELD (never silent
    truncation or factual mutation).
    """
    concept = _concept_from_candidate(candidate)
    variant = ci.plan_variant(concept, platform)
    preserved = (ci.facts_preserved(concept, variant)
                 if variant.status == ci.READY else False)
    return {
        "platform": platform,
        "char_limit": variant.char_limit,
        "text": variant.text,
        "within_limit": variant.within_limit and variant.status == ci.READY,
        "alt_text_required": bool(variant.asset_plan.get("alt_text_required")),
        "native_format": variant.native_format,
        "status": variant.status,
        "withheld_reason": variant.withheld_reason,
        "fact_bindings": variant.fact_bindings,
        "lineage": variant.lineage,
        "dropped_framing": variant.dropped_framing,
        "facts_preserved": preserved,
        "silent_truncation": False,
        "content_id": variant.content_id,
        # Enough to rebuild the variant for lineage/novelty (V1.6) without
        # carrying a non-serializable object in the queue payload.
        "concept_id": variant.concept_id,
        "persona": variant.persona,
        "hook": variant.hook,
        "char_count": variant.char_count,
        "asset_plan": dict(variant.asset_plan),
    }


def variant_from_payload(payload: dict) -> "ci.PlatformVariant":
    """Rebuild the PlatformVariant a payload was rendered from (for lineage/novelty)."""
    return ci.PlatformVariant(
        content_id=payload["content_id"], concept_id=payload["concept_id"],
        persona=payload["persona"], platform=payload["platform"],
        native_format=payload["native_format"], hook=payload.get("hook", ""),
        text=payload["text"], char_count=payload.get("char_count", len(payload["text"])),
        char_limit=payload["char_limit"], within_limit=bool(payload["within_limit"]),
        status=payload["status"], withheld_reason=payload.get("withheld_reason", ""),
        fact_bindings=list(payload.get("fact_bindings") or []),
        dropped_framing=payload.get("dropped_framing", 0),
        asset_plan=dict(payload.get("asset_plan") or {}),
        lineage=dict(payload.get("lineage") or {}))


# --------------------------------------------------------------------------- #
# Final-content review binding (V1.7 C05/C06; LEAD-050 item 5)
#
# Draft-level review looks at hook/body/claims; platform formatting then renders
# the FINAL text (it may drop framing). Nothing may be queued unless the factual,
# voice, cultural and platform checks were run over that exact final text and the
# result is bound to its hash. Formatting again, editing the candidate or editing
# the payload invalidates the binding; ``enqueue`` refuses unbound or mismatched
# payloads; ``verify_queued_entry`` re-checks the exact bytes a consumer reads.
# --------------------------------------------------------------------------- #
class ReviewBindingError(ValueError):
    """A payload reached the queue without a review bound to its exact final content."""


# Keys the review itself writes; everything else on the candidate is a reviewed input.
_REVIEW_OUTPUT_KEYS = frozenset({"review", "review_passed", "status", "review_binding"})


def _canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def reviewed_digest(candidate: dict) -> str:
    """sha256 over every reviewed input of a candidate (its own review output excluded)."""
    inputs = {k: v for k, v in candidate.items() if k not in _REVIEW_OUTPUT_KEYS}
    return hashlib.sha256(_canonical(inputs)).hexdigest()


def text_digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def final_review(persona: dict, candidate: dict, payload: dict) -> dict:
    """Run every review over the FINAL rendered text and bind the result to its hash.

    The binding (also stored on ``payload["review_binding"]``) names the exact
    content id / persona / runtime / platform and the sha256 of ``payload["text"]``.
    ``passed`` is False when the candidate changed since its draft review, when any
    check fails on the final text, or when the platform gate is not READY.
    """
    reasons: list[str] = []
    draft = candidate.get("review_binding") or {}
    draft_ok = bool(draft) and draft.get("reviewed_sha256") == reviewed_digest(candidate)
    if not draft_ok:
        reasons.append("candidate changed after its draft review (or was never reviewed)")
    text = payload.get("text")
    if not isinstance(text, str):
        reasons.append("payload carries no rendered text")
        text = ""

    final_view = dict(candidate)
    final_view["hook"] = ""
    final_view["body"] = text                          # exactly what would be published
    has_facts = bool(candidate.get("fact_segments") or candidate.get("segments")
                     or candidate.get("content_concept"))
    platform_ok = bool(payload.get("within_limit")) and payload.get("status") == ci.READY \
        and not payload.get("silent_truncation") \
        and (bool(payload.get("facts_preserved")) or not has_facts)
    checks = {
        "fact": fact_check(persona, final_view),
        "voice": voice_review(persona, final_view),
        "cultural": cultural_review(persona, final_view),
        "platform": {"check": "platform", "passed": platform_ok,
                     "reason": ("ready within limit" if platform_ok else
                                f"status={payload.get('status')!r} within_limit="
                                f"{payload.get('within_limit')!r} facts_preserved="
                                f"{payload.get('facts_preserved')!r}")},
    }
    # G-CULTURAL: a required cultural pass must name THIS final text, not merely
    # the candidate id — an attributable review over exact final content.
    cultural = checks["cultural"]
    if cultural.get("required") and cultural.get("passed"):
        if not cr.bound_to_content(cr.binding_from_candidate(candidate), text_digest(text)):
            checks["cultural"] = dict(cultural, passed=False, status=cr.WITHHELD,
                                      reason="cultural review is not bound to the final "
                                             "rendered text (content_sha256 missing or "
                                             "mismatched)")
    reasons += [f"{k}: {c.get('reason')}" for k, c in checks.items() if not c["passed"]]
    binding = {
        "final_text_sha256": text_digest(text),
        "draft_reviewed_sha256": draft.get("reviewed_sha256"),
        "content_id": candidate.get("content_id"),
        "persona": candidate.get("persona"),
        "bot": candidate.get("bot"),
        "platform": payload.get("platform"),
        "checks": checks,
        "passed": draft_ok and all(c["passed"] for c in checks.values()),
        "reasons": reasons,
        "bound_at": now_iso(),
    }
    payload["review_binding"] = binding
    return binding


def verify_payload_binding(bot: str, candidate: dict, payload: dict) -> dict:
    """Raise ``ReviewBindingError`` unless ``payload`` carries a passed final review
    bound to its exact current text and to this candidate/persona/runtime/platform."""
    binding = payload.get("review_binding")
    if not isinstance(binding, dict) or not binding:
        raise ReviewBindingError("payload has no final-content review binding; run "
                                 "final_review after format_for_platform")
    problems: list[str] = []
    if not binding.get("passed"):
        problems.append("final review did not pass: " + "; ".join(binding.get("reasons") or []))
    text = payload.get("text")
    if not isinstance(text, str) or binding.get("final_text_sha256") != text_digest(text):
        problems.append("payload text differs from the reviewed final text")
    if binding.get("draft_reviewed_sha256") != reviewed_digest(candidate):
        problems.append("candidate changed after its review")
    for key, expected in (("content_id", candidate.get("content_id")),
                          ("persona", candidate.get("persona")),
                          ("platform", payload.get("platform")),
                          ("bot", bot)):
        if binding.get(key) != expected:
            problems.append(f"binding {key} {binding.get(key)!r} != {expected!r}")
    if candidate.get("bot") != bot:
        problems.append(f"candidate runtime {candidate.get('bot')!r} != queue runtime {bot!r}")
    if problems:
        raise ReviewBindingError("; ".join(problems))
    return binding


def _queue_path(bot: str) -> Path:
    """The canonical publish-queue file; never read or written through a link."""
    p = paths.content_dir(bot) / "publish_queue.jsonl"
    if p.is_symlink():
        raise ReviewBindingError(f"publish queue for {bot!r} is a symlink; refusing to "
                                 f"operate through a link")
    return p


def verify_queued_entry(bot: str, entry: dict) -> dict:
    """Re-verify the exact bytes a consumer is about to act on against the binding.

    Any publisher/canary MUST call this before acting on a queue entry: it catches
    a late write to the queue, a replaced payload, a wrong-runtime entry and a
    symlinked queue. Returns ``{"verified": bool, "problems": [...]}``.
    """
    problems: list[str] = []
    binding = entry.get("review_binding")
    payload = entry.get("payload") or {}
    text = payload.get("text")
    if not isinstance(binding, dict) or not binding:
        problems.append("entry has no review binding")
        binding = {}
    if not binding.get("passed"):
        problems.append("bound review did not pass")
    if not isinstance(text, str) or text_digest(text) != entry.get("final_text_sha256") \
            or entry.get("final_text_sha256") != binding.get("final_text_sha256"):
        problems.append("payload text does not match the bound final text")
    if entry.get("bot") != bot or binding.get("bot") != bot:
        problems.append(f"entry is not scoped to runtime {bot!r}")
    if entry.get("persona") != binding.get("persona") \
            or entry.get("content_id") != binding.get("content_id") \
            or entry.get("platform") != binding.get("platform") \
            or payload.get("platform") != binding.get("platform"):
        problems.append("entry fields do not match the binding")
    try:
        _queue_path(bot)
    except ReviewBindingError as exc:
        problems.append(str(exc))
    return {"verified": not problems, "problems": problems,
            "final_text_sha256": entry.get("final_text_sha256")}


# --------------------------------------------------------------------------- #
# Dedup — against the persona's own content history
# --------------------------------------------------------------------------- #
def content_key(candidate: dict) -> str:
    basis = f"{candidate['persona']}|{candidate['signal_id']}|{candidate['signature_move']}"
    return hashlib.sha256(basis.encode()).hexdigest()[:16]


def persona_content_keys(bot: str, persona: str) -> set[str]:
    """Authoritative persona-scoped read of prior content keys (SB-V03-005).

    Production dedup reads must be persona-scoped, not whole-runtime: this returns
    only the given persona's content keys. (Whole-runtime reads remain available
    as explicit internal/admin reads, e.g. ``read_jsonl`` directly.)
    """
    hist = read_jsonl(paths.content_dir(bot) / "content_history.jsonl")
    return {h.get("content_key") for h in hist if h.get("persona") == persona}


def is_duplicate(bot: str, candidate: dict) -> bool:
    # Persona-scoped: only the SAME persona's history can make a candidate a
    # duplicate. content_key is persona-derived, so this is also collision-free
    # across personas; scoping the READ makes the isolation boundary explicit.
    key = content_key(candidate)
    return key in persona_content_keys(bot, candidate["persona"])


# --------------------------------------------------------------------------- #
# Experiment registry
# --------------------------------------------------------------------------- #
PROSPECTIVE = "PROSPECTIVE"
NOT_MEASURED = "NOT_MEASURED"
MEASURED = "MEASURED"


class ExperimentRegistrationError(ValueError):
    """An experiment carried a fabricated baseline, outcome or confidence."""


def prospective_baseline(metric: str) -> dict:
    """The only honest pre-publication baseline: the metric name and NO value."""
    return {"metric": metric, "value": None, "status": NOT_MEASURED,
            "note": "no pre-publication measurement exists; prospective registration"}


@dataclass
class Experiment:
    """A registered, PROSPECTIVE experiment (V1.7 C07).

    Registration happens BEFORE publication, so at that moment there is no
    baseline measurement, no outcome and no confidence. Those fields therefore
    default to None and ``register_experiment`` refuses any value in them: a
    number that was never measured is a fabricated performance record. A real
    pre-publication baseline is allowed only with provenance (``status``
    MEASURED, ``measured_at``, ``source``).
    """
    experiment_id: str
    bot: str
    persona: str
    platform: str
    hypothesis: str
    baseline: dict
    intervention: str
    success_metric: str
    stop_criteria: str
    observation_window_hours: int
    cost_budget: str = "none"
    result: dict | None = None
    confidence: float | None = None
    decision: str | None = None
    registered_at: str = field(default_factory=now_iso)
    status: str = PROSPECTIVE
    window: dict = field(default_factory=lambda: {
        "opens_at": None, "closes_at": None,
        "note": "opens only when the candidate is actually published"})


def validate_prospective(exp: Experiment | dict) -> list[str]:
    """Violations that would make a registration a fabricated performance record."""
    d = exp.__dict__ if isinstance(exp, Experiment) else dict(exp)
    errs: list[str] = []
    if d.get("status") != PROSPECTIVE:
        errs.append(f"status {d.get('status')!r} is not {PROSPECTIVE}; only prospective "
                    f"experiments are registered")
    for fld in ("result", "decision", "confidence"):
        if d.get(fld) is not None:
            errs.append(f"{fld} must be None at registration (got {d.get(fld)!r})")
    baseline = d.get("baseline")
    if not isinstance(baseline, dict):
        errs.append("baseline must be a dict")
    elif baseline.get("value") is not None:
        if baseline.get("status") != MEASURED or not baseline.get("measured_at") \
                or not baseline.get("source"):
            errs.append("baseline carries a value without measurement provenance "
                        "(status MEASURED, measured_at, source)")
    window = d.get("window") or {}
    if not isinstance(window, dict) or window.get("opens_at") is not None \
            or window.get("closes_at") is not None:
        errs.append("observation window cannot be open before publication")
    hours = d.get("observation_window_hours")
    if isinstance(hours, bool) or not isinstance(hours, int) or hours < 1:
        errs.append("observation_window_hours must be a positive integer")
    return errs


def register_experiment(exp: Experiment) -> Path:
    errs = validate_prospective(exp)
    if errs:
        raise ExperimentRegistrationError("; ".join(errs))
    p = paths.experiments_dir(exp.bot) / f"{exp.experiment_id}.json"
    write_json(p, exp.__dict__)
    append_jsonl(paths.experiments_dir(exp.bot) / "index.jsonl",
                 {"experiment_id": exp.experiment_id, "persona": exp.persona,
                  "platform": exp.platform, "registered_at": exp.registered_at})
    return p


# --------------------------------------------------------------------------- #
# Publish queue — DISABLED by default. Queuing is never an external effect.
# --------------------------------------------------------------------------- #
def enqueue(bot: str, candidate: dict, platform_payload: dict,
            experiment_id: str | None) -> dict:
    """Queue a candidate whose FINAL text carries a passed, matching review binding.

    Refuses (``ReviewBindingError``) an unbound payload, a payload edited after
    its final review, a candidate edited after review, a persona/platform/runtime
    mismatch, or a symlinked queue file. Queuing is never an external effect.
    """
    binding = verify_payload_binding(bot, candidate, platform_payload)
    queue = _queue_path(bot)
    entry = {
        "queued_at": now_iso(),
        "content_id": candidate["content_id"],
        "content_key": content_key(candidate),
        "persona": candidate["persona"],
        "bot": bot,
        "platform": platform_payload["platform"],
        "experiment_id": experiment_id,
        "payload": platform_payload,
        "final_text_sha256": binding["final_text_sha256"],
        "review_binding": binding,
        "publish_authorized": False,   # hard default: never publish without explicit authority
        "published": False,
        "publication_id": None,
    }
    append_jsonl(queue, entry)
    return entry


def admin_publish_queue(bot: str) -> list[dict]:
    """ADMIN/INTERNAL: the whole-runtime publish queue (ALL personas).

    Structurally admin-named (SB-V03-005 LEAD-025): there is no non-admin
    whole-runtime publish-queue reader, so a persona-facing production path cannot
    accidentally enumerate another persona's queued items. Persona-facing reads
    must use ``isolation.persona_publish_queue`` / ``isolation.persona_records``;
    deliberate runtime-wide reads (e.g. takeover reconciliation) go through
    ``isolation.admin_all_records(bot, "publish_queue")``.
    """
    return read_jsonl(_queue_path(bot))
