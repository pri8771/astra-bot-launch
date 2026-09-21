"""Community observation, decision and memory (SB-V17-001).

Safely OBSERVE community signals (comments/replies) from fixtures or read-only
evidence, decide whether a response would be useful, and retain community
memory — with a hard wall between reading and any public response effect.

Boundaries (non-negotiable)
---------------------------
- **Read/observe is fully separated from response effect.** Ingestion and
  classification never touch a posting path. There is deliberately NO public
  posting, voting, following, or engagement function in this module.
- Spam / abuse / unsafe / content-policy signals gate to NO_ACTION.
- A response is only ever a *proposal* carrying a confidence and an authority
  requirement. It cannot become an effect without an explicit authorized route
  AND a passing deterministic review — and even then this module performs no
  public effect (that remains an unauthorized, out-of-scope external gate).
- Community themes update audience memory only through real ingested evidence.
"""
from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field, asdict

from . import paths
from .jsonstore import append_jsonl, read_jsonl, now_iso

# Safety classes.
SAFE = "safe"
SPAM = "spam"
ABUSE = "abuse"
UNSAFE = "unsafe"
POLICY = "policy_violation"

# Value classes.
V_HIGH = "high"
V_MEDIUM = "medium"
V_LOW = "low"
V_NONE = "none"

# Decision actions (none of these perform a public effect).
NO_ACTION = "NO_ACTION"
OBSERVE_ONLY = "OBSERVE_ONLY"
PROPOSE_RESPONSE = "PROPOSE_RESPONSE"

# Deterministic, clearly-heuristic keyword gates.
_ABUSE = ("idiot", "moron", "hate you", "kill yourself", "slur")
_UNSAFE = ("kill", "bomb", "self-harm", "suicide", "attack them", "dox")
_SPAM = ("buy now", "free money", "click here", "promo code", "make $$$", "t.me/")
_LOW_VALUE = ("lol", "nice", "cool", "first", "👍", "same")


@dataclass(frozen=True)
class CommunitySignal:
    """A single ingested community observation. READ-ONLY evidence."""
    id: str
    thread_id: str
    parent_id: str | None
    content_id: str | None
    persona: str | None
    account_alias: str | None
    author_ref: str            # anonymized/opaque author reference (no PII)
    text: str
    observed_at: str
    source: str                # 'fixture' | 'read-only-evidence'

    @staticmethod
    def ingest(*, thread_id: str, text: str, source: str = "fixture",
               parent_id: str | None = None, content_id: str | None = None,
               persona: str | None = None, account_alias: str | None = None,
               author_ref: str = "anon", observed_at: str | None = None) -> "CommunitySignal":
        if source not in ("fixture", "read-only-evidence"):
            raise ValueError("community ingestion is read-only "
                             "(source must be fixture or read-only-evidence)")
        return CommunitySignal(
            id="cs-" + uuid.uuid4().hex[:12], thread_id=thread_id, parent_id=parent_id,
            content_id=content_id, persona=persona, account_alias=account_alias,
            author_ref=author_ref, text=text, observed_at=observed_at or now_iso(),
            source=source)

    def as_dict(self) -> dict:
        return asdict(self)


def _contains(text: str, needles) -> bool:
    t = text.lower()
    return any(n in t for n in needles)


def classify(signal: CommunitySignal) -> dict:
    """Deterministic safety + value classification (heuristic, inspectable)."""
    text = signal.text.strip()
    low = text.lower()

    if _contains(low, _UNSAFE):
        safety = UNSAFE
    elif _contains(low, _ABUSE):
        safety = ABUSE
    elif _contains(low, _SPAM) or low.count("http") >= 2:
        safety = SPAM
    else:
        safety = SAFE

    if not text:
        value = V_NONE
    elif safety != SAFE:
        value = V_NONE
    elif "?" in text and len(text) >= 15:
        value = V_HIGH               # a substantive question
    elif len(text) >= 40:
        value = V_MEDIUM             # substantive comment
    elif _contains(low, _LOW_VALUE) or len(text) < 15:
        value = V_LOW
    else:
        value = V_MEDIUM

    return {"safety": safety, "value": value,
            "note": "heuristic classification; not a fabricated judgement"}


@dataclass
class ResponseProposal:
    proposal_id: str
    signal_id: str
    thread_id: str
    content_id: str | None
    persona: str | None
    account_alias: str | None
    action: str
    confidence: float
    authority_required: bool
    reason: str
    draft_hint: str = ""          # a hint only; NOT a published response
    cleared_for_effect: bool = False
    effect_status: str = "no-effect-performed"

    def as_dict(self) -> dict:
        return asdict(self)


def recommend(signal: CommunitySignal, classification: dict | None = None) -> ResponseProposal:
    """Decide whether a response would be useful. Never performs an effect."""
    c = classification or classify(signal)
    safety, value = c["safety"], c["value"]

    def mk(action, confidence, authority, reason):
        return ResponseProposal(
            proposal_id="rp-" + uuid.uuid4().hex[:12], signal_id=signal.id,
            thread_id=signal.thread_id, content_id=signal.content_id,
            persona=signal.persona, account_alias=signal.account_alias,
            action=action, confidence=confidence, authority_required=authority,
            reason=reason)

    if safety != SAFE:
        return mk(NO_ACTION, 0.95, False,
                  f"safety gate: {safety}; no engagement")
    if value in (V_NONE, V_LOW):
        return mk(NO_ACTION, 0.8, False, f"low-value ({value}); not worth a reply")
    if value == V_MEDIUM:
        return mk(OBSERVE_ONLY, 0.6, False,
                  "medium value; observe and update memory, no response")
    # high value, safe -> propose (still requires authority + review to ever act)
    return mk(PROPOSE_RESPONSE, 0.7, True,
              "high-value safe question; response proposed pending authority + review")


@dataclass(frozen=True)
class AuthorizedRoute:
    """An explicit authorization token for a specific account/thread. Absence of
    this (or authorized=False) means a proposal can never become an effect."""
    account_alias: str
    authorized: bool = False
    granted_by: str = ""


def clear_for_effect(proposal: ResponseProposal, route: AuthorizedRoute | None,
                     review_fn) -> ResponseProposal:
    """Gate a proposal: needs an authorized route AND a passing deterministic
    review. Even when cleared, THIS MODULE PERFORMS NO PUBLIC EFFECT."""
    if proposal.action != PROPOSE_RESPONSE:
        proposal.effect_status = "not-a-response-proposal"
        return proposal
    if route is None or not route.authorized:
        proposal.cleared_for_effect = False
        proposal.effect_status = "BLOCKED_NO_AUTHORITY"
        return proposal
    if not review_fn(proposal):
        proposal.cleared_for_effect = False
        proposal.effect_status = "BLOCKED_REVIEW"
        return proposal
    proposal.cleared_for_effect = True
    # Deliberately no public effect here — an authorized external executor would
    # act; none exists in this module (public posting is unauthorized).
    proposal.effect_status = "CLEARED_NO_EFFECT_PERFORMED"
    return proposal


# --------------------------------------------------------------------------- #
# Community memory + themes.
# --------------------------------------------------------------------------- #
def _mem_path(bot: str):
    return paths.memory_dir(bot) / "community_signals.jsonl"


def remember(bot: str, signal: CommunitySignal, classification: dict) -> None:
    rec = signal.as_dict()
    rec["classification"] = classification
    append_jsonl(_mem_path(bot), rec)


def signals(bot: str) -> list[dict]:
    return read_jsonl(_mem_path(bot))


_WORD = re.compile(r"[a-z]{4,}")
_STOP = {"this", "that", "with", "your", "have", "what", "when", "they", "from",
         "about", "would", "could", "there", "just", "like", "really"}


def community_themes(bot: str, *, top: int = 5, min_count: int = 2) -> list[dict]:
    """Aggregate recurring themes from SAFE ingested signals only."""
    counts: dict[str, int] = {}
    for s in signals(bot):
        if s.get("classification", {}).get("safety") != SAFE:
            continue
        for w in set(_WORD.findall(s.get("text", "").lower())):
            if w in _STOP:
                continue
            counts[w] = counts.get(w, 0) + 1
    themes = [{"theme": w, "count": n} for w, n in counts.items() if n >= min_count]
    themes.sort(key=lambda t: t["count"], reverse=True)
    return themes[:top]


def theme_to_audience_evidence(bot: str, theme: dict) -> dict:
    """An evidence ref (from real ingested signals) for audience memory. Carries
    no invented confidence — audience.py derives that from the observation."""
    return {"source": "community", "bot": bot, "theme": theme["theme"],
            "observed_count": theme["count"], "captured_at": now_iso()}
