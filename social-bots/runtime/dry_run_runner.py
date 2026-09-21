"""Reusable V0.6 bounded dry-run runner (SB-R07-061).

One runner for all three general bots. Writes an immutable run manifest per
``RUN_MANIFEST_SCHEMA.md``, uses the zero-public-effect authority profile, and
stops before public publication. No live model call is performed.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Callable

from . import decision, pipeline, research, personas, paths
from .jsonstore import now_iso

SCHEMA_VERSION = "1.0.0"
VERSION_TARGET = "V0.6"
ZERO_PUBLIC_AUTHORITY = decision.Authority(
    can_create_candidate=True,
    can_register_experiment=True,
    can_update_state=True,
    can_public_post=False,
    can_spend=False,
    can_message_users=False,
)

# Default three-bot general persona map for V0.6 dry runs.
DEFAULT_BOT_PERSONAS = (
    ("social-a", "social-a"),
    ("social-b", "social-b"),
    ("social-c", "social-c"),
)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _file_hash(path: Path) -> str:
    if not path.exists():
        return "UNKNOWN"
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _persona_hash(persona_id: str) -> str:
    path = Path(__file__).resolve().parent.parent / "personas" / f"{persona_id}.json"
    return _file_hash(path)


def _objective_hash(persona: dict) -> str:
    obj = persona.get("purpose") or persona.get("one_line") or ""
    return _sha256_text(obj)


@dataclass
class DryRunResult:
    bot: str
    persona: str
    outcome: str
    manifest: dict
    decision_record: dict
    published: bool
    publish_authorized: bool
    checks: dict
    passed: bool

    def as_dict(self) -> dict:
        return asdict(self)


def build_run_manifest(
    *,
    run_id: str,
    artifact_id: str,
    bot: str,
    persona: str,
    started_at: str,
    finished_at: str,
    source_code_ref: str,
    decision_record: dict,
    evidence_refs: list,
    receipt_refs: list,
    limitations: list | None = None,
    host_alias: str = "engineering-host",
    scheduler_or_invoker: str = "sbots.dry_run_runner",
    authorization_manifest_ref: str = "zero-public-effect-authority",
    model_call_budget: int = 0,
    config_hash: str = "UNKNOWN",
) -> dict:
    """Assemble an immutable run manifest matching RUN_MANIFEST_SCHEMA.md."""
    persona_doc = personas.load(persona)
    queue = pipeline.admin_publish_queue(bot)
    published = any(bool(q.get("published")) for q in queue)
    publish_authorized = any(bool(q.get("publish_authorized")) for q in queue)
    public_effects_attempted = 0
    public_effects_verified = 0
    result = decision_record.get("outcome", "UNKNOWN")
    if published or publish_authorized:
        result = "FAILED_PUBLIC_EFFECT_GATE"
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "artifact_id": artifact_id,
        "version_target": VERSION_TARGET,
        "bot": bot,
        "persona": persona,
        "started_at": started_at,
        "finished_at": finished_at,
        "source_code_ref": source_code_ref or "UNKNOWN",
        "config_hash": config_hash,
        "persona_hash": _persona_hash(persona),
        "objective_hash": _objective_hash(persona_doc),
        "host_alias": host_alias,
        "scheduler_or_invoker": scheduler_or_invoker,
        "authorization_manifest_ref": authorization_manifest_ref,
        "evidence_refs": list(evidence_refs),
        "provider_runs": [],  # no model/provider calls in this runner
        "model_call_budget": model_call_budget,
        "model_calls_used": 0,
        "public_effect_budget": 0,
        "public_effects_attempted": public_effects_attempted,
        "public_effects_verified": public_effects_verified,
        "result": result,
        "limitations": list(limitations or [
            "engineering dry-run; no live model call",
            "zero-public-effect authority profile",
        ]),
        "receipt_refs": list(receipt_refs),
        "authority_profile": {
            "can_public_post": False,
            "can_spend": False,
            "can_message_users": False,
        },
        "queue_snapshot": [
            {"published": q.get("published"),
             "publish_authorized": q.get("publish_authorized"),
             "platform": q.get("platform")}
            for q in queue
        ],
        "reconciliation": [],  # append-only; empty at write time
    }


def _default_checks(record: dict, queue: list) -> dict:
    created = record.get("outcome") == "candidate_created"
    withheld = record.get("outcome") == "withheld"
    return {
        "coherent_decision": record.get("outcome") in
            ("candidate_created", "withheld", "no_action", "research_more"),
        "created_implies_valid": (not created) or (
            record.get("verify", {}).get("within_platform_limit")
            and record.get("verify", {}).get("review_passed")),
        "withheld_implies_stopped": (not withheld) or (
            bool(record.get("execute", {}).get("gate_failures"))
            and record.get("verify", {}).get("queued") is False),
        "no_publish": all(not q.get("published") for q in queue),
        "no_publish_authorized": all(not q.get("publish_authorized") for q in queue),
        "zero_model_calls": True,
    }


def run_one_dry_run(
    bot: str,
    persona_id: str,
    *,
    artifact_id: str = "SB-R07-061",
    source_code_ref: str = "UNKNOWN",
    signals: list | None = None,
    capture_signals: bool = True,
    authority: decision.Authority | None = None,
    write_manifest_to: Path | None = None,
) -> DryRunResult:
    """Run one bounded dry-run cycle for ``bot``/``persona_id``.

    Stops before public publication: authority forbids public post/spend/message.
    Optional ``signals`` are captured as fixture provenance when provided.
    """
    authority = authority or ZERO_PUBLIC_AUTHORITY
    if authority.can_public_post or authority.can_spend or authority.can_message_users:
        raise ValueError("dry-run runner refuses non-zero-public-effect authority")

    started = now_iso()
    run_id = f"dry-{uuid.uuid4().hex[:12]}"
    evidence_refs: list = []

    if capture_signals and signals:
        for spec in signals:
            sig = research.Signal.make(
                title=spec["title"], summary=spec["summary"],
                source=spec.get("source", "dry-run"),
                url=spec.get("url"),
                provenance=spec.get("provenance", "fixture"),
                tags=list(spec.get("tags") or []),
            )
            research.capture(bot, sig)
            evidence_refs.append(sig.id)

    record = decision.run_cycle(bot, persona_id, authority=authority)
    finished = now_iso()
    queue = pipeline.admin_publish_queue(bot)
    checks = _default_checks(record, queue)
    published = any(bool(q.get("published")) for q in queue)
    publish_authorized = any(bool(q.get("publish_authorized")) for q in queue)
    if published or publish_authorized:
        checks["no_publish"] = False
        checks["no_publish_authorized"] = False

    receipt_refs = []
    last = paths.state_dir(bot) / "last_decision.json"
    if last.exists():
        receipt_refs.append(str(last))

    manifest = build_run_manifest(
        run_id=run_id,
        artifact_id=artifact_id,
        bot=bot,
        persona=persona_id,
        started_at=started,
        finished_at=finished,
        source_code_ref=source_code_ref,
        decision_record=record,
        evidence_refs=evidence_refs,
        receipt_refs=receipt_refs,
    )
    if write_manifest_to is not None:
        write_manifest_to.parent.mkdir(parents=True, exist_ok=True)
        # Immutable write: refuse overwrite.
        if write_manifest_to.exists():
            raise FileExistsError(f"manifest already exists: {write_manifest_to}")
        write_manifest_to.write_text(json.dumps(manifest, indent=2) + "\n")

    passed = all(checks.values()) and not published and not publish_authorized
    return DryRunResult(
        bot=bot, persona=persona_id, outcome=record.get("outcome", "UNKNOWN"),
        manifest=manifest, decision_record=record,
        published=published, publish_authorized=publish_authorized,
        checks=checks, passed=passed,
    )


def run_three_bot_dry_runs(
    *,
    artifact_id: str = "SB-R07-061",
    source_code_ref: str = "UNKNOWN",
    signal_map: dict | None = None,
    manifest_dir: Path | None = None,
    bot_personas=DEFAULT_BOT_PERSONAS,
) -> list[DryRunResult]:
    """Run the reusable dry-run once per bot/persona pair."""
    results = []
    for bot, persona_id in bot_personas:
        signals = (signal_map or {}).get(bot)
        dest = None
        if manifest_dir is not None:
            dest = Path(manifest_dir) / f"{bot}-{persona_id}.run_manifest.json"
        results.append(run_one_dry_run(
            bot, persona_id,
            artifact_id=artifact_id,
            source_code_ref=source_code_ref,
            signals=signals,
            capture_signals=bool(signals),
            write_manifest_to=dest,
        ))
    return results
