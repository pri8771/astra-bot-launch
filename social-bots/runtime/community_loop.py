"""V1.7 community path (SB-S17 / C25): observe -> scoped memory -> decide ->
reviewed, bound reply candidate -> persisted outcome and next check.

This is the production path the general bots run for community threads. It is
READ-ONLY by construction:

- Input is an inbox of community signals (fixture rows, or read-only platform
  captures that MUST carry a ``receipt_ref``). Nothing here fetches, posts,
  replies, votes, follows or messages; there is no send function to call.
- Every signal passes the negative controls BEFORE any decision: wrong
  persona/account/thread scope, replayed capture receipt, duplicate signal,
  stale observation, prompt-injection pattern, spam/abuse/unsafe text.
- A PROPOSE_RESPONSE decision produces a reply CANDIDATE that goes through the
  same factual/voice/cultural/platform review and final-content binding as any
  other content (``pipeline.review`` / ``final_review``) and is persisted with
  ``publish_authorized: False`` and ``effect_status`` BLOCKED_NO_AUTHORITY unless
  a registry route explicitly authorizes replies — and even then no effect is
  performed here (``community.clear_for_effect`` performs none).
- Memory, themes and audience evidence are persona-scoped and labelled with the
  evidence class of the signals they came from (OFFLINE_FIXTURE for fixtures,
  LIVE_SOURCE only for receipt-backed captures).

The record it returns says exactly what happened, including BLOCKED_DATA when
no real (receipt-backed) input exists.
"""
from __future__ import annotations

import hashlib
import re
from datetime import datetime, timedelta, timezone

from . import account_routes, audience, community, paths, pipeline
from .jsonstore import append_jsonl, now_iso, read_json, read_jsonl, write_json
from .personas import load as load_persona

OFFLINE_FIXTURE = "OFFLINE_FIXTURE"
LIVE_SOURCE = "LIVE_SOURCE"
BLOCKED_DATA = "BLOCKED_DATA"

DEFAULT_MAX_AGE_HOURS = 14 * 24
_INJECTION = (
    "ignore previous instructions", "ignore all previous", "disregard your instructions",
    "system prompt", "you are now", "act as an", "developer mode", "reveal your prompt",
    "print your instructions", "as an ai language model", "<|", "[inst]", "```system",
)

REFUSED_SCOPE = "refused_scope"
REFUSED_THREAD = "refused_thread"
REFUSED_ACCOUNT = "refused_account"
SKIPPED_DUPLICATE = "skipped_duplicate"
SKIPPED_REPLAY = "skipped_replayed_receipt"
SKIPPED_STALE = "skipped_stale"
BLOCKED_INJECTION = "blocked_injection"


# --------------------------------------------------------------------------- #
# Persona-scoped storage
# --------------------------------------------------------------------------- #
def _dir(bot: str, persona: str):
    if not persona:
        raise ValueError("community path is persona-scoped; a persona is required")
    d = paths.memory_dir(bot) / "community" / paths._check(persona)
    d.mkdir(parents=True, exist_ok=True)
    return d


def inbox_path(bot: str, persona: str):
    return _dir(bot, persona) / "inbox.jsonl"


def _ledger_path(bot: str, persona: str):
    return _dir(bot, persona) / "processed.json"


def _replies_path(bot: str, persona: str):
    return _dir(bot, persona) / "reply_candidates.jsonl"


def _decisions_path(bot: str, persona: str):
    return _dir(bot, persona) / "decisions.jsonl"


def read_ledger(bot: str, persona: str) -> dict:
    data = read_json(_ledger_path(bot, persona), default=None)
    if not isinstance(data, dict):
        return {"signal_ids": [], "receipt_refs": [], "fingerprints": []}
    for k in ("signal_ids", "receipt_refs", "fingerprints"):
        data.setdefault(k, [])
    return data


def load_inbox(bot: str, persona: str) -> list[dict]:
    """Raw inbox rows (a fixture drop or a read-only capture export)."""
    return read_jsonl(inbox_path(bot, persona))


def reply_candidates(bot: str, persona: str) -> list[dict]:
    return read_jsonl(_replies_path(bot, persona))


def decisions(bot: str, persona: str) -> list[dict]:
    return read_jsonl(_decisions_path(bot, persona))


# --------------------------------------------------------------------------- #
# Negative controls (run BEFORE any decision)
# --------------------------------------------------------------------------- #
def injection_suspect(text: str) -> bool:
    low = (text or "").lower()
    return any(marker in low for marker in _INJECTION)


def _fingerprint(sig: community.CommunitySignal) -> str:
    normalized = re.sub(r"\s+", " ", sig.text.strip().lower())
    basis = f"{sig.thread_id}|{sig.author_ref}|{normalized}"
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()[:24]


def _persona_content_ids(bot: str, persona: str) -> set[str]:
    hist = read_jsonl(paths.content_dir(bot) / "content_history.jsonl")
    ids = {h.get("content_id") for h in hist if h.get("persona") == persona}
    ids |= {e.get("content_id") for e in pipeline.admin_publish_queue(bot)
            if e.get("persona") == persona}
    return {i for i in ids if i}


def _route_aliases(bot: str, persona: str, *, now: datetime | None = None) -> tuple[bool, set[str], dict]:
    """(registry_present, aliases of this persona's routes, reply-authorized route by alias)."""
    try:
        routes = account_routes.load_routes()
    except account_routes.RouteRegistryError:
        return True, set(), {}
    if routes is None:
        return False, set(), {}
    mine = [r for r in routes if r.get("bot") == bot and r.get("persona") == persona]
    aliases = {r.get("account_alias") for r in mine if r.get("account_alias")}
    reply_ok = {r.get("account_alias"): r for r in mine
                if account_routes._route_ok(r, now=now)[0]
                and (r.get("capabilities") or {}).get("reply") and r.get("reply_authorized") is True}
    return True, aliases, reply_ok


def _control(sig: community.CommunitySignal, *, bot: str, persona: str, ledger: dict,
             seen_fps: set, own_content: set, registry_present: bool, aliases: set,
             now: datetime, max_age_hours: float) -> tuple[str | None, str]:
    """Return (verdict, reason); verdict None means the signal may be decided."""
    if sig.persona is not None and sig.persona != persona:
        return REFUSED_SCOPE, f"signal addressed to persona {sig.persona!r}, not {persona!r}"
    if sig.content_id and sig.content_id not in own_content:
        return REFUSED_THREAD, (f"thread is about content {sig.content_id!r} that is not "
                                f"this persona's")
    if registry_present and sig.account_alias and sig.account_alias not in aliases:
        return REFUSED_ACCOUNT, f"account alias {sig.account_alias!r} is not a route of this persona"
    if sig.id in ledger["signal_ids"]:
        return SKIPPED_DUPLICATE, "signal id already processed"
    if sig.receipt_ref and sig.receipt_ref in ledger["receipt_refs"]:
        return SKIPPED_REPLAY, "capture receipt already consumed (replayed observation)"
    fp = _fingerprint(sig)
    if fp in ledger["fingerprints"] or fp in seen_fps:
        return SKIPPED_DUPLICATE, "same thread/author/text already processed"
    try:
        observed = datetime.fromisoformat(sig.observed_at.replace("Z", "+00:00"))
        if observed.tzinfo is None:
            observed = observed.replace(tzinfo=timezone.utc)
    except (ValueError, AttributeError):
        return SKIPPED_STALE, "observed_at is not a valid timestamp; freshness unknown"
    if now - observed > timedelta(hours=max_age_hours):
        return SKIPPED_STALE, f"observation older than {max_age_hours:.0f}h"
    if injection_suspect(sig.text):
        return BLOCKED_INJECTION, "prompt-injection pattern in source text; never enters a prompt"
    return None, "controls passed"


# --------------------------------------------------------------------------- #
# Reply candidate (deterministic draft, reviewed and bound like any content)
# --------------------------------------------------------------------------- #
def _draft_reply(persona: dict, sig: community.CommunitySignal) -> dict:
    excerpt = re.sub(r"\s+", " ", sig.text.strip())[:80]
    move = "reply"
    content_id = "reply-" + hashlib.sha256(
        f"{persona['id']}|{sig.thread_id}|{sig.id}".encode("utf-8")).hexdigest()[:12]
    body = (f"Thanks for asking. Re: \"{excerpt}\" — a short, sourced answer is being "
            f"prepared in {persona.get('display_name', persona['id'])}'s voice; nothing is "
            f"claimed here beyond the linked source.")
    return {
        "content_id": content_id, "bot": persona["runtime"], "persona": persona["id"],
        "signal_id": sig.id, "thread_id": sig.thread_id, "parent_id": sig.parent_id,
        "angle": f"{persona['id']}:{move}:{sig.id}", "hook": "", "body": body,
        "source_refs": [sig.receipt_ref or f"community:{sig.source}:{sig.thread_id}"],
        "signature_move": move, "created_at": now_iso(), "status": "ideated",
        "draft_source": "deterministic-template", "adaptive": False,
        "reply_to": {"thread_id": sig.thread_id, "parent_id": sig.parent_id,
                     "signal_id": sig.id, "author_ref": sig.author_ref},
    }


def _thread_platform(persona: dict, sig: community.CommunitySignal) -> str:
    return ((persona.get("platform_strategy") or {}).get("primary") or ["x"])[0]


# --------------------------------------------------------------------------- #
# The cycle
# --------------------------------------------------------------------------- #
def run_community_cycle(bot: str, persona_id: str, *, signals=None, fence=None,
                        now: datetime | None = None,
                        max_age_hours: float = DEFAULT_MAX_AGE_HOURS) -> dict:
    """One bounded community cycle for ``persona_id`` on runtime ``bot``.

    ``signals``: an explicit list of ``CommunitySignal`` (tests / operators);
    otherwise the persona's inbox rows are ingested. Returns the persisted record.
    Durable writes run inside ``fence.fenced_commit`` when a fence is given.
    """
    persona = load_persona(persona_id)
    if persona["runtime"] != bot:
        raise ValueError(f"persona {persona_id} runs on {persona['runtime']}, not {bot}")
    now = now or datetime.now(timezone.utc)
    ledger = read_ledger(bot, persona_id)
    registry_present, aliases, reply_routes = _route_aliases(bot, persona_id, now=now)
    own_content = _persona_content_ids(bot, persona_id)

    ingested: list[community.CommunitySignal] = []
    ingest_errors: list[dict] = []
    if signals is None:
        for row in load_inbox(bot, persona_id):
            try:
                ingested.append(community.CommunitySignal.ingest(**{
                    k: row.get(k) for k in ("thread_id", "text", "source", "parent_id",
                                             "content_id", "persona", "account_alias",
                                             "author_ref", "observed_at", "receipt_ref")
                    if row.get(k) is not None}))
            except (TypeError, ValueError) as exc:
                ingest_errors.append({"row_thread": row.get("thread_id"),
                                      "error": str(exc)[:200]})
    else:
        ingested = list(signals)

    controls: list[dict] = []
    decided: list[dict] = []
    remembered: list[tuple] = []
    replies: list[dict] = []
    seen_fps: set = set()
    new_ids, new_receipts, new_fps = [], [], []
    for sig in ingested:
        verdict, reason = _control(sig, bot=bot, persona=persona_id, ledger=ledger,
                                   seen_fps=seen_fps, own_content=own_content,
                                   registry_present=registry_present, aliases=aliases,
                                   now=now, max_age_hours=max_age_hours)
        entry = {"signal_id": sig.id, "thread_id": sig.thread_id, "source": sig.source,
                 "operational": sig.is_operational(), "control": verdict or "passed",
                 "reason": reason}
        controls.append(entry)
        if verdict is not None:
            continue
        seen_fps.add(_fingerprint(sig))
        classification = community.classify(sig)
        proposal = community.recommend(sig, classification)
        decision = {"signal_id": sig.id, "thread_id": sig.thread_id,
                    "classification": classification, "action": proposal.action,
                    "confidence": proposal.confidence, "reason": proposal.reason,
                    "authority_required": proposal.authority_required,
                    "evidence_class": LIVE_SOURCE if sig.is_operational() else OFFLINE_FIXTURE}
        remembered.append((sig, classification))
        new_ids.append(sig.id)
        new_fps.append(_fingerprint(sig))
        if sig.receipt_ref:
            new_receipts.append(sig.receipt_ref)
        if proposal.action == community.PROPOSE_RESPONSE:
            cand = pipeline.review(persona, _draft_reply(persona, sig))
            platform = _thread_platform(persona, sig)
            payload = pipeline.format_for_platform(cand, platform)
            final = pipeline.final_review(persona, cand, payload)
            route = None
            if sig.account_alias in reply_routes:
                route = community.AuthorizedRoute(account_alias=sig.account_alias,
                                                  authorized=True,
                                                  granted_by=reply_routes[sig.account_alias]
                                                  .get("route_id", ""))
            community.clear_for_effect(proposal, route, lambda _p: bool(final["passed"]))
            reply = {"recorded_at": now_iso(), "bot": bot, "persona": persona_id,
                     "signal_id": sig.id, "thread_id": sig.thread_id,
                     "proposal_id": proposal.proposal_id, "content_id": cand["content_id"],
                     "platform": platform, "draft_source": cand["draft_source"],
                     "adaptive": False, "review_passed": cand["review_passed"],
                     "final_review_bound": final["passed"],
                     "final_text_sha256": final["final_text_sha256"],
                     "text": payload.get("text"),
                     "cleared_for_effect": proposal.cleared_for_effect,
                     "effect_status": proposal.effect_status,
                     "publish_authorized": False, "published": False,
                     "evidence_class": decision["evidence_class"]}
            replies.append(reply)
            decision["reply_candidate"] = {k: reply[k] for k in (
                "content_id", "final_review_bound", "final_text_sha256",
                "effect_status", "cleared_for_effect", "publish_authorized")}
        decided.append(decision)

    operational = sum(1 for s in ingested if s.is_operational())
    record = {
        "recorded_at": now_iso(), "bot": bot, "persona": persona_id, "kind": "community_cycle",
        "ingested": len(ingested), "ingest_errors": ingest_errors, "controls": controls,
        "decided": decided, "reply_candidates": len(replies),
        "effects_performed": 0,
        "evidence_class": LIVE_SOURCE if operational else OFFLINE_FIXTURE,
        "data_state": ("READY" if operational else BLOCKED_DATA),
        "data_note": (None if operational else
                      "no receipt-backed read-only community capture exists; fixture "
                      "signals prove the path only, never live completion"),
        "registry_present": registry_present,
        "next_check_in_hours": 6 if decided else 24,
        "fence": fence.token() if fence is not None else None,
    }

    def commit():
        for sig, classification in remembered:
            community.remember(bot, persona_id, sig, classification)
        for reply in replies:
            append_jsonl(_replies_path(bot, persona_id), reply)
        ledger["signal_ids"] = ledger["signal_ids"] + new_ids
        ledger["receipt_refs"] = ledger["receipt_refs"] + new_receipts
        ledger["fingerprints"] = ledger["fingerprints"] + new_fps
        ledger["updated_at"] = now_iso()
        write_json(_ledger_path(bot, persona_id), ledger)
        record["themes"] = community.community_themes(bot, persona_id)
        record["audience_evidence"] = _learn_themes(bot, persona_id, record["themes"],
                                                    record["evidence_class"])
        append_jsonl(_decisions_path(bot, persona_id), record)

    if fence is not None:
        fence.fenced_commit(commit)
    else:
        commit()
    return record


def _learn_themes(bot: str, persona_id: str, themes: list[dict], evidence_class: str) -> list:
    """Recurring SAFE themes become persona-scoped audience observations, labelled
    with their evidence class; confidence is never invented (audience derives it)."""
    out = []
    existing = {h.segment.get("content_theme"): h for h in audience.list_hypotheses(bot, persona_id)
                if h.segment.get("content_theme")}
    for theme in themes:
        name = theme["theme"]
        hyp = existing.get(name) or audience.new_hypothesis(
            bot, persona_id, {"content_theme": name},
            f"the community around {persona_id} keeps raising '{name}'")
        evidence = community.theme_to_audience_evidence(bot, persona_id, theme)
        evidence["evidence_class"] = evidence_class
        audience.add_observation(hyp, audience.Observation.make(
            audience.SUPPORTS, evidence, weight=float(theme["count"]),
            note=f"community theme ({evidence_class})"))
        audience.save(bot, persona_id, hyp)
        out.append({"hypothesis_id": hyp.id, "theme": name, "count": theme["count"],
                    "evidence_class": evidence_class})
    return out
