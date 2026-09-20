"""Platform-independent content/experiment pipeline.

Flow: signal -> persona ideation -> fact/voice/cultural review -> platform format
-> dedup -> experiment registration -> publish queue (publishing DISABLED by
default). No operational mock data: candidates are built from real captured
signals and the persona spec. Publishing here only *queues*; it never emits an
external effect.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

from . import paths
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
    needs_evidence = persona.get("source_requirements", {}).get("evidence_required", True)
    has_source = bool(candidate.get("source_refs"))
    ok = (not needs_evidence) or has_source
    return {"check": "fact", "passed": ok,
            "reason": "source ref present" if has_source else "no source ref"}


def voice_review(persona: dict, candidate: dict) -> dict:
    banned = [b.replace("-", " ") for b in persona["voice"].get("banned_moves", [])]
    text = f"{candidate['hook']} {candidate['body']}".lower()
    hits = [b for b in banned if b in text]
    return {"check": "voice", "passed": not hits,
            "reason": "clean" if not hits else f"banned-move hit: {hits}"}


def cultural_review(persona: dict, candidate: dict) -> dict:
    sr = persona.get("source_requirements", {})
    if persona.get("kind") != "cultural" and not sr.get("cultural_review_required"):
        return {"check": "cultural", "required": False, "passed": True,
                "reason": "not a cultural persona"}
    reviewer = sr.get("named_reviewer")  # only present once owner binds one
    has_source = bool(candidate.get("source_refs"))
    passed = bool(reviewer) and has_source
    return {"check": "cultural", "required": True, "passed": passed,
            "status": "ACCEPTED" if passed else "WITHHELD",
            "reason": ("named reviewer + source bound" if passed
                       else "no named cultural reviewer and/or source; WITHHELD per contract")}


def review(persona: dict, candidate: dict) -> dict:
    checks = {
        "fact": fact_check(persona, candidate),
        "voice": voice_review(persona, candidate),
        "cultural": cultural_review(persona, candidate),
    }
    candidate["review"] = checks
    candidate["review_passed"] = all(c["passed"] for c in checks.values())
    candidate["status"] = "reviewed" if candidate["review_passed"] else "withheld"
    return candidate


# --------------------------------------------------------------------------- #
# Platform formatting
# --------------------------------------------------------------------------- #
_LIMITS = {"x": 280, "reddit": 40000, "instagram": 2200, "tiktok": 2200, "facebook": 63000}


def format_for_platform(candidate: dict, platform: str) -> dict:
    limit = _LIMITS.get(platform, 2200)
    text = f"{candidate['hook']}\n\n{candidate['body']}"
    truncated = text if len(text) <= limit else text[: limit - 1] + "…"
    return {
        "platform": platform,
        "char_limit": limit,
        "text": truncated,
        "within_limit": len(text) <= limit,
        "alt_text_required": platform in {"instagram", "tiktok"},
    }


# --------------------------------------------------------------------------- #
# Dedup — against the persona's own content history
# --------------------------------------------------------------------------- #
def content_key(candidate: dict) -> str:
    basis = f"{candidate['persona']}|{candidate['signal_id']}|{candidate['signature_move']}"
    return hashlib.sha256(basis.encode()).hexdigest()[:16]


def is_duplicate(bot: str, candidate: dict) -> bool:
    key = content_key(candidate)
    hist = read_jsonl(paths.content_dir(bot) / "content_history.jsonl")
    return any(h.get("content_key") == key for h in hist)


# --------------------------------------------------------------------------- #
# Experiment registry
# --------------------------------------------------------------------------- #
@dataclass
class Experiment:
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
    confidence: float = 0.0
    decision: str | None = None
    registered_at: str = field(default_factory=now_iso)


def register_experiment(exp: Experiment) -> Path:
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
    entry = {
        "queued_at": now_iso(),
        "content_id": candidate["content_id"],
        "content_key": content_key(candidate),
        "persona": candidate["persona"],
        "bot": bot,
        "platform": platform_payload["platform"],
        "experiment_id": experiment_id,
        "payload": platform_payload,
        "publish_authorized": False,   # hard default: never publish without explicit authority
        "published": False,
        "publication_id": None,
    }
    append_jsonl(paths.content_dir(bot) / "publish_queue.jsonl", entry)
    return entry


def publish_queue(bot: str) -> list[dict]:
    return read_jsonl(paths.content_dir(bot) / "publish_queue.jsonl")
