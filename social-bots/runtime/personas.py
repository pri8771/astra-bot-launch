"""Persona loading, validation, and an accidental-convergence detector.

Personas are public-facing AI-managed characters/brands — never fabricated humans.
Runtime identity (which bot process runs) is distinct from persona identity (public
surface). A runtime may host more than one persona *workspace*.

The distinctness check exists because the biggest failure mode for a multi-persona
system is silent convergence: three "different" voices that drift into one. We
compute lexical overlap across voice/topic/strategy features and fail if any two
*general* personas are too similar.
"""
from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

PERSONA_DIR = Path(__file__).resolve().parent.parent / "personas"

REQUIRED_FIELDS = (
    "id", "kind", "display_name", "runtime", "purpose", "target_audience",
    "voice", "values_boundaries", "topics", "content_styles",
    "platform_strategy", "success_metric_hierarchy", "memory_namespace",
    "experiment_namespace", "content_history_namespace", "correction_behavior",
    "moderation_policy", "source_requirements", "audience_hypotheses",
)
REQUIRED_VOICE = ("tone", "diction", "sentence_style", "signature_moves", "banned_moves")

# Two personas sharing more than this fraction of voice/topic features are too alike.
DISTINCTNESS_MAX_JACCARD = 0.34


def load(persona_id: str) -> dict:
    p = PERSONA_DIR / f"{persona_id}.json"
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_all() -> list[dict]:
    out = []
    for p in sorted(PERSONA_DIR.glob("*.json")):
        with open(p, "r", encoding="utf-8") as fh:
            out.append(json.load(fh))
    return out


def validate(persona: dict) -> list[str]:
    errors = []
    for f in REQUIRED_FIELDS:
        if f not in persona or persona[f] in (None, "", [], {}):
            errors.append(f"missing/empty field: {f}")
    voice = persona.get("voice", {})
    for f in REQUIRED_VOICE:
        if f not in voice or not voice[f]:
            errors.append(f"missing/empty voice.{f}")
    if persona.get("kind") == "cultural":
        sr = persona.get("source_requirements", {})
        if not sr.get("cultural_review_required"):
            errors.append("cultural persona must set source_requirements.cultural_review_required=true")
        if not sr.get("named_reviewer_required"):
            errors.append("cultural persona must require a named cultural reviewer")
    # Guard against fabricated-human identity.
    boundaries = " ".join(persona.get("values_boundaries", [])).lower()
    if "ai-managed" not in json.dumps(persona).lower() and "not a real" not in boundaries:
        errors.append("persona must declare it is an AI-managed character (no fabricated human identity)")
    return errors


def _feature_set(persona: dict) -> set[str]:
    v = persona["voice"]
    feats = set()
    for token in v.get("tone", []):
        feats.add(f"tone:{token.lower()}")
    for token in v.get("signature_moves", []):
        feats.add(f"sig:{token.lower()}")
    for token in persona.get("topics", []):
        feats.add(f"topic:{token.lower()}")
    for token in persona.get("content_styles", []):
        feats.add(f"style:{token.lower()}")
    # primary platform + primary metric characterize strategy
    plats = persona.get("platform_strategy", {}).get("primary", [])
    for token in plats:
        feats.add(f"plat:{token.lower()}")
    metrics = persona.get("success_metric_hierarchy", [])
    if metrics:
        feats.add(f"metric1:{str(metrics[0]).lower()}")
    return feats


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def distinctness_report(personas: list[dict] | None = None) -> dict:
    """Report pairwise similarity for the general personas; flag convergence."""
    personas = personas or [p for p in load_all() if p.get("kind") == "general"]
    pairs = []
    worst = 0.0
    for a, b in combinations(personas, 2):
        sim = round(jaccard(_feature_set(a), _feature_set(b)), 3)
        worst = max(worst, sim)
        pairs.append({
            "a": a["id"], "b": b["id"], "jaccard": sim,
            "too_similar": sim > DISTINCTNESS_MAX_JACCARD,
        })
    return {
        "threshold": DISTINCTNESS_MAX_JACCARD,
        "worst_jaccard": worst,
        "converged": any(p["too_similar"] for p in pairs),
        "pairs": pairs,
    }
