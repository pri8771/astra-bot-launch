"""Analytics event schema + append-only per-bot event log.

Every event distinguishes, at minimum: bot runtime, persona, platform, account
alias, content item, experiment, publication id, observation time. Metrics from
different personas are never silently mixed; aggregation is explicit.
"""
from __future__ import annotations

from . import paths
from .jsonstore import append_jsonl, read_jsonl, now_iso

REQUIRED_KEYS = (
    "bot", "persona", "platform", "account_alias", "content_id",
    "experiment_id", "publication_id", "observed_at", "event_type", "metrics",
)

EVENT_TYPES = {
    "candidate_created", "experiment_registered", "queued", "published",
    "impression_snapshot", "engagement_snapshot", "decision", "correction",
}


def make_event(bot: str, persona: str, event_type: str, *,
               platform: str | None = None, account_alias: str | None = None,
               content_id: str | None = None, experiment_id: str | None = None,
               publication_id: str | None = None, metrics: dict | None = None,
               observed_at: str | None = None) -> dict:
    if event_type not in EVENT_TYPES:
        raise ValueError(f"unknown event_type {event_type!r}")
    return {
        "bot": bot,
        "persona": persona,
        "platform": platform,
        "account_alias": account_alias,
        "content_id": content_id,
        "experiment_id": experiment_id,
        "publication_id": publication_id,
        "observed_at": observed_at or now_iso(),
        "event_type": event_type,
        "metrics": metrics or {},
    }


def validate_event(event: dict) -> list[str]:
    return [f"missing key: {k}" for k in REQUIRED_KEYS if k not in event]


def emit(event: dict) -> None:
    errs = validate_event(event)
    if errs:
        raise ValueError(f"invalid analytics event: {errs}")
    append_jsonl(paths.analytics_dir(event["bot"]) / "events.jsonl", event)


def events_for(bot: str) -> list[dict]:
    return read_jsonl(paths.analytics_dir(bot) / "events.jsonl")


def aggregate(bot: str, persona: str, metric: str) -> dict:
    """Explicit, persona-scoped aggregation. Never blends personas."""
    total = 0.0
    n = 0
    for e in events_for(bot):
        if e.get("persona") != persona:
            continue
        val = e.get("metrics", {}).get(metric)
        if isinstance(val, (int, float)):
            total += val
            n += 1
    return {"bot": bot, "persona": persona, "metric": metric,
            "sum": total, "samples": n,
            "note": "persona-scoped; not blended across personas"}
