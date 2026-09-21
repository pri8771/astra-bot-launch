"""Content intelligence (SB-V16-001).

Generate/repair platform-native content while preserving facts, persona voice,
novelty and experiment intent.

Core guarantees
---------------
- Content is modeled as ordered *segments* tagged ``fact`` or ``framing``. Fact
  segments carry an evidence binding (SB-V05-002) and are NEVER altered or
  dropped. Only framing is compressed.
- Over-limit content is **repaired** (drop/reduce framing) or **withheld** — a
  fact never gets silently truncated. If facts alone exceed the platform limit,
  the variant is withheld.
- Novelty/dedup: exact key match plus word-shingle near-duplicate detection.
- Series / repurpose lineage is recorded on every variant.
- Each platform gets a native variant (limits, format, asset plan), so one
  concept produces distinct outputs per platform.
"""
from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field, asdict

from . import paths
from .jsonstore import append_jsonl, read_jsonl, now_iso

FACT = "fact"
FRAMING = "framing"

READY = "ready"
WITHHELD = "withheld"

# Platform-native constraints. Deliberately local (does not couple to pipeline).
PLATFORM_CONSTRAINTS = {
    "x": {"char_limit": 280, "native_format": "post", "alt_text": False, "hashtags": 0},
    "instagram": {"char_limit": 2200, "native_format": "reel-caption", "alt_text": True, "hashtags": 5},
    "tiktok": {"char_limit": 2200, "native_format": "short-video-caption", "alt_text": True, "hashtags": 3},
    "reddit": {"char_limit": 40000, "native_format": "text-post", "alt_text": False, "hashtags": 0},
    "facebook": {"char_limit": 63000, "native_format": "post", "alt_text": False, "hashtags": 0},
}


@dataclass(frozen=True)
class Segment:
    text: str
    kind: str = FRAMING
    binding_ref: dict | None = None   # for fact segments: {claim_id, receipt_id, content_hash}

    @staticmethod
    def fact(text: str, binding_ref: dict) -> "Segment":
        if not binding_ref:
            raise ValueError("a fact segment must carry an evidence binding_ref")
        return Segment(text=text, kind=FACT, binding_ref=dict(binding_ref))

    @staticmethod
    def framing(text: str) -> "Segment":
        return Segment(text=text, kind=FRAMING)


@dataclass
class ContentConcept:
    concept_id: str
    persona: str
    segments: list          # Segment objects
    series_id: str | None = None
    experiment_id: str | None = None
    repurposed_from: str | None = None

    def fact_segments(self):
        return [s for s in self.segments if s.kind == FACT]

    def framing_segments(self):
        return [s for s in self.segments if s.kind == FRAMING]


def new_concept(persona: str, segments: list, *, series_id: str | None = None,
                experiment_id: str | None = None,
                repurposed_from: str | None = None) -> ContentConcept:
    return ContentConcept(
        concept_id="cc-" + uuid.uuid4().hex[:12], persona=persona,
        segments=list(segments), series_id=series_id,
        experiment_id=experiment_id, repurposed_from=repurposed_from)


def new_series() -> str:
    return "series-" + uuid.uuid4().hex[:10]


def repurpose(concept: ContentConcept, *, persona: str | None = None,
              experiment_id: str | None = None) -> ContentConcept:
    """Create a new concept repurposed from an existing one (lineage kept)."""
    return ContentConcept(
        concept_id="cc-" + uuid.uuid4().hex[:12],
        persona=persona or concept.persona,
        segments=list(concept.segments),
        series_id=concept.series_id,
        experiment_id=experiment_id or concept.experiment_id,
        repurposed_from=concept.concept_id)


@dataclass
class PlatformVariant:
    content_id: str
    concept_id: str
    platform: str
    native_format: str
    hook: str
    text: str
    char_count: int
    char_limit: int
    within_limit: bool
    status: str
    withheld_reason: str
    fact_bindings: list          # bindings that survived into the rendered text
    dropped_framing: int
    asset_plan: dict
    lineage: dict

    def as_dict(self) -> dict:
        return asdict(self)


def _hook_for(platform: str, concept: ContentConcept) -> str:
    # Native hook: first segment's text, bounded for terse platforms.
    lead = concept.segments[0].text if concept.segments else ""
    if platform == "x":
        return lead[:100]
    return lead


def _hashtag_tail(platform: str, concept: ContentConcept) -> str:
    n = PLATFORM_CONSTRAINTS[platform]["hashtags"]
    if n <= 0:
        return ""
    # Deterministic, persona-shaped tags (framing only; never factual content).
    base = hashlib.sha256(concept.concept_id.encode()).hexdigest()
    tags = [f"#{concept.persona.replace('-', '')}"] + [f"#t{base[i:i+4]}" for i in range(0, n * 4, 4)]
    return "\n\n" + " ".join(tags[:n])


def plan_variant(concept: ContentConcept, platform: str) -> PlatformVariant:
    """Produce a platform-native variant, repairing framing to fit the limit.

    Facts are preserved verbatim; if facts alone exceed the limit the variant is
    withheld rather than truncated.
    """
    if platform not in PLATFORM_CONSTRAINTS:
        raise ValueError(f"unknown platform {platform!r}")
    con = PLATFORM_CONSTRAINTS[platform]
    limit = con["char_limit"]

    facts = concept.fact_segments()
    framing = concept.framing_segments()
    tail = _hashtag_tail(platform, concept)

    def render(chosen_framing):
        parts = [s.text for s in chosen_framing] + [s.text for s in facts]
        body = "\n\n".join(p for p in parts if p)
        return body + tail

    # Essential = all facts (never dropped/altered) + hashtag tail.
    essential = render([])
    lineage = {"concept_id": concept.concept_id, "series_id": concept.series_id,
               "repurposed_from": concept.repurposed_from, "platform": platform}
    content_id = "ci-" + hashlib.sha256(
        f"{concept.concept_id}|{platform}".encode()).hexdigest()[:12]
    fact_bindings = [s.binding_ref for s in facts]
    asset_plan = {"alt_text_required": con["alt_text"],
                  "native_format": con["native_format"],
                  "suggested_assets": (["video", "cover-frame"]
                                       if "video" in con["native_format"]
                                       else ["image"])}

    if len(essential) > limit:
        # Cannot fit facts without changing meaning -> withhold, never truncate.
        return PlatformVariant(
            content_id=content_id, concept_id=concept.concept_id, platform=platform,
            native_format=con["native_format"], hook=_hook_for(platform, concept),
            text="", char_count=len(essential), char_limit=limit, within_limit=False,
            status=WITHHELD,
            withheld_reason="fact-bound content exceeds platform limit; "
                            "repair would drop/alter a fact (no silent truncation)",
            fact_bindings=fact_bindings, dropped_framing=len(framing),
            asset_plan=asset_plan, lineage=lineage)

    # Repair loop: greedily keep framing (highest priority first) that still fits.
    chosen: list = []
    for seg in framing:
        trial = render(chosen + [seg])
        if len(trial) <= limit:
            chosen.append(seg)
    text = render(chosen)
    dropped = len(framing) - len(chosen)

    return PlatformVariant(
        content_id=content_id, concept_id=concept.concept_id, platform=platform,
        native_format=con["native_format"], hook=_hook_for(platform, concept),
        text=text, char_count=len(text), char_limit=limit, within_limit=True,
        status=READY, withheld_reason="",
        fact_bindings=fact_bindings, dropped_framing=dropped,
        asset_plan=asset_plan, lineage=lineage)


def facts_preserved(concept: ContentConcept, variant: PlatformVariant) -> bool:
    """Every fact segment's exact text must appear in a ready variant."""
    if variant.status != READY:
        return False
    return all(s.text in variant.text for s in concept.fact_segments())


# --------------------------------------------------------------------------- #
# Novelty / dedup.
# --------------------------------------------------------------------------- #
def _shingles(text: str, k: int = 3) -> set:
    words = [w for w in text.lower().split() if w]
    if len(words) < k:
        return {" ".join(words)} if words else set()
    return {" ".join(words[i:i + k]) for i in range(len(words) - k + 1)}


def similarity(a: str, b: str) -> float:
    sa, sb = _shingles(a), _shingles(b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    inter = len(sa & sb)
    union = len(sa | sb)
    return inter / union if union else 0.0


def _history_path(bot: str):
    return paths.content_dir(bot) / "content_intel_history.jsonl"


def record_variant(bot: str, variant: PlatformVariant) -> None:
    append_jsonl(_history_path(bot), {
        "content_id": variant.content_id, "platform": variant.platform,
        "concept_id": variant.concept_id, "text": variant.text,
        "status": variant.status, "recorded_at": now_iso(),
        "lineage": variant.lineage})


def check_novelty(bot: str, variant: PlatformVariant, *,
                  near_threshold: float = 0.8) -> dict:
    hist = read_jsonl(_history_path(bot))
    exact = any(h.get("content_id") == variant.content_id for h in hist)
    max_sim = 0.0
    nearest = None
    for h in hist:
        if h.get("platform") != variant.platform:
            continue
        sim = similarity(variant.text, h.get("text", ""))
        if sim > max_sim:
            max_sim, nearest = sim, h.get("content_id")
    return {
        "is_exact_duplicate": exact,
        "is_near_duplicate": max_sim >= near_threshold,
        "max_similarity": round(max_sim, 4),
        "nearest_content_id": nearest,
        "novel": (not exact) and max_sim < near_threshold,
    }
