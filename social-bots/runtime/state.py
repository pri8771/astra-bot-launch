"""Two-layer durable state (SB-V03-005 isolation contract).

A single runtime process (``social-a``/``social-b``/``social-c``) hosts more than
one persona *workspace* — e.g. ``social-a`` hosts the general ``social-a`` persona
AND the cultural ``cultural-primandir-atman`` persona. Two disjoint layers of
state keep those personas from contaminating each other's learning:

1. ``RuntimeState`` — SHARED, one per runtime (``state/<bot>/bot_state.json``).
   Holds only runtime-wide facts that every persona legitimately shares:
     - process/health counters (cycles/actions/no_action),
     - recovery/in-flight status,
     - the observation fingerprint of the shared capture catalog.
   The shared captured-evidence catalog itself is the runtime signal inbox
   (``memory/<bot>/signals_inbox.jsonl``); it is READ-ONLY to cycles (only the
   research capture path appends to it). Concurrent mutation of RuntimeState is
   prevented by the runtime lease (``cycle:<bot>``) and the active-cycle fence
   (SB-V03-004): only the fenced owner may commit it.

2. ``PersonaState`` — PRIVATE, one per persona/workspace
   (``state/<bot>/persona-<persona_id>.json``). Holds everything that must NOT
   leak between personas on the same runtime:
     - ``consumed_signal_ids`` — which shared signals THIS persona has decided on;
     - ``hypotheses`` — this persona's evidence-tied learning;
     - ``working_state``, ``pending_decisions``, ``goals`` — private working set.
   Because consumption is persona-private, the SAME shared signal can be
   independently considered by ``social-a`` and ``cultural-primandir-atman``:
   one consuming it does not hide it from the other. One persona's hypothesis
   count can never change another persona's reasoning context.

NON-SHARED persona *artifacts* (content history, experiments, publish queue,
analytics events, action/decision records) live in the runtime's append-only
stores but are LOGICALLY isolated per persona: every such record carries an
explicit ``persona`` field and a persona-derived, collision-free identity key
(see ``runtime.isolation``). One bot's ``paths`` namespace can never be written
by another bot; cross-bot facts use the explicit ``shared`` namespace only.

Migration: an older ``bot_state.json`` carried the persona-private fields at the
runtime level. On first load they are archived into ``_legacy`` (never silently
deleted) and, when the default-owner persona (``persona_id == bot``) first loads
its private state, migrated into it exactly once.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from . import paths
from .jsonstore import read_json, write_json, append_jsonl, read_jsonl, now_iso

_STATE_FILE = "bot_state.json"

# Fields that used to live on the shared runtime state but are persona-private.
_PERSONA_PRIVATE_KEYS = (
    "consumed_signal_ids", "hypotheses", "working_state", "pending_decisions",
    "goals",
)


def _default_runtime_state(bot: str) -> dict:
    return {
        "bot": bot,
        "schema_version": 2,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "observation_fingerprint": None,  # diagnostic: fingerprint at last cycle
        "recovery": {"last_clean_tick": None, "in_flight": None},
        "counters": {"cycles": 0, "actions": 0, "no_action": 0},
    }


@dataclass
class RuntimeState:
    """Shared, single-writer-per-runtime state. Fenced on commit (SB-V03-004)."""

    bot: str
    data: dict = field(default_factory=dict)

    @classmethod
    def load(cls, bot: str) -> "RuntimeState":
        if bot not in paths.BOTS:
            raise ValueError(f"unknown bot {bot!r}; expected one of {paths.BOTS}")
        p = paths.state_dir(bot) / _STATE_FILE
        data = read_json(p, default=None) or _default_runtime_state(bot)
        data = cls._migrate_out_persona_private(bot, data)
        return cls(bot=bot, data=data)

    @staticmethod
    def _migrate_out_persona_private(bot: str, data: dict) -> dict:
        """Move any legacy persona-private fields into ``_legacy`` (never delete).

        A pre-SB-V03-005 ``bot_state.json`` stored the consumed ledger/hypotheses/
        working set at the runtime level. We relocate them under ``_legacy`` so the
        shared file no longer *actively* carries persona-private data, while the
        old values are preserved for a one-time migration into the default-owner
        persona (see ``PersonaState.load``). Idempotent: after the first load the
        top-level keys are gone, so subsequent loads find nothing to move.
        """
        moved = {k: data[k] for k in _PERSONA_PRIVATE_KEYS
                 if k in data and data[k] not in (None, [], {})}
        had_any = any(k in data for k in _PERSONA_PRIVATE_KEYS)
        for k in _PERSONA_PRIVATE_KEYS:
            data.pop(k, None)
        if moved:
            legacy = data.setdefault("_legacy", {})
            # Preserve the very first archived copy; do not clobber on re-load.
            if "archived_persona_private" not in legacy:
                legacy["archived_persona_private"] = moved
                legacy["archived_at"] = now_iso()
                legacy["default_owner_persona"] = bot
                legacy["migrated_to_persona"] = False
        elif had_any:
            # Legacy keys were present but empty: mark schema touched, nothing to keep.
            data.setdefault("_legacy", {}).setdefault("migrated_to_persona", True)
        data["schema_version"] = 2
        return data

    def save(self) -> None:
        self.data["updated_at"] = now_iso()
        write_json(paths.state_dir(self.bot) / _STATE_FILE, self.data)

    # --- shared append-only stores (persona-LABELED records) ----------------
    # These append to the runtime's shared stores but every record must carry an
    # explicit ``persona`` field so ``runtime.isolation`` can partition them.
    def record_observation(self, obs: dict) -> None:
        obs = {"recorded_at": now_iso(), **obs}
        append_jsonl(paths.memory_dir(self.bot) / "observations.jsonl", obs)

    def record_action(self, action: dict) -> None:
        action = {"recorded_at": now_iso(), **action}
        append_jsonl(paths.memory_dir(self.bot) / "action_history.jsonl", action)
        self.data["counters"]["actions"] += 1

    def record_content(self, content: dict) -> None:
        content = {"recorded_at": now_iso(), **content}
        append_jsonl(paths.content_dir(self.bot) / "content_history.jsonl", content)

    def admin_content_history(self) -> list[dict]:
        """ADMIN/INTERNAL whole-runtime read (all personas), structurally
        admin-named (SB-V03-005 LEAD-026): there is no ordinary public
        whole-runtime content-history reader. Persona-facing production reads must
        use ``runtime.isolation.persona_content_history`` / ``persona_records``;
        deliberate runtime-wide reads go through ``isolation.admin_all_records``."""
        return read_jsonl(paths.content_dir(self.bot) / "content_history.jsonl")


# Back-compat alias: older callers/tests import ``BotState`` for runtime-level
# concerns (counters, recovery, shared stores). It is the shared RuntimeState.
BotState = RuntimeState


def _default_persona_state(bot: str, persona_id: str) -> dict:
    return {
        "runtime": bot,
        "persona_id": persona_id,
        "schema_version": 1,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "goals": [],
        "working_state": {},
        "pending_decisions": [],
        "hypotheses": {},          # id -> {statement, confidence, evidence[], updated_at}
        "consumed_signal_ids": [],  # signals THIS persona has decided upon
    }


def _persona_file(bot: str, persona_id: str):
    # persona ids match paths._SAFE (validated) so this is a safe filename.
    return paths.state_dir(bot) / f"persona-{persona_id}.json"


@dataclass
class PersonaState:
    """Per-persona private state. Never shared across personas on one runtime."""

    bot: str
    persona_id: str
    data: dict = field(default_factory=dict)

    @classmethod
    def load(cls, bot: str, persona_id: str,
             runtime: "RuntimeState | None" = None) -> "PersonaState":
        """Load (or first-time STAGE a migration for) this persona's private state.

        SIDE-EFFECT FREE (SB-V03-004 LEAD-019 repair): this NEVER writes to disk.
        A first-time legacy migration is STAGED IN MEMORY only — the persona file
        and the runtime migrated-marker are persisted exclusively inside the
        cycle's ownership-fenced commit (``decision._commit`` -> ``ps.save()`` /
        ``rt.save()`` under ``Fence.fenced_commit``). So an obsolete owner that
        loses the fence mid-cycle leaves NO persona-state or migration-marker
        write behind, exactly like every other durable cycle write.

        ``runtime`` is the RuntimeState instance the caller will commit this cycle.
        When migration is staged, the migrated-marker is set on THAT in-memory
        instance so the marker the fenced commit persists is the final one.

        Idempotency is gated on PERSONA-FILE EXISTENCE (checked here) plus the fact
        that staging is deterministic from the legacy archive: before any fenced
        commit persists the persona file, every load re-stages the same data; once
        the file exists, migration never runs again. A crash that loses the marker
        cannot cause re-migration or data loss.
        """
        if bot not in paths.BOTS:
            raise ValueError(f"unknown bot {bot!r}; expected one of {paths.BOTS}")
        p = _persona_file(bot, persona_id)
        existing = read_json(p, default=None)
        if existing is not None:
            return cls(bot=bot, persona_id=persona_id, data=existing)
        data = _default_persona_state(bot, persona_id)
        obj = cls(bot=bot, persona_id=persona_id, data=data)
        obj._stage_legacy_migration(runtime)
        return obj

    def _stage_legacy_migration(self, runtime: "RuntimeState | None") -> bool:
        """Stage a one-time legacy migration IN MEMORY (no disk writes).

        Pre-SB-V03-005 runtimes kept a single consumed ledger/hypotheses set at
        the runtime level. That data historically belonged to the default-owner
        persona (the general persona whose id equals the runtime). We stage it into
        this persona's private state, and (if a runtime instance is supplied) set
        the migrated marker on that in-memory runtime. NOTHING is written here:
        both the persona file and the marker are persisted only by the fenced
        commit, so this load path is safe for a worker that may not own the fence.

        Returns True iff a migration was staged.
        """
        bot, persona_id = self.bot, self.persona_id
        if persona_id != bot:
            return False
        # Source the legacy archive: prefer the caller's in-memory runtime (the
        # instance that will be committed), else read the on-disk runtime file
        # (either an archived ``_legacy`` block or still-top-level legacy keys).
        # Reading is not a side effect; only writing would be.
        archived: dict = {}
        if runtime is not None:
            archived = dict((runtime.data.get("_legacy") or {})
                            .get("archived_persona_private") or {})
        if not archived:
            rt_raw = read_json(paths.state_dir(bot) / _STATE_FILE, default=None) or {}
            disk_legacy = rt_raw.get("_legacy") or {}
            archived = dict(disk_legacy.get("archived_persona_private") or {})
            for k in _PERSONA_PRIVATE_KEYS:
                if k not in archived and rt_raw.get(k) not in (None, [], {}):
                    archived[k] = rt_raw[k]
        if not archived:
            return False
        for k in _PERSONA_PRIVATE_KEYS:
            if k in archived:
                self.data[k] = archived[k]
        self.data["_migrated_from_legacy_runtime_state"] = now_iso()
        # Stage the marker on the SHARED in-memory runtime so the fenced commit
        # persists it on the instance the real cycle commits. No write here.
        if runtime is not None:
            runtime.data.setdefault("_legacy", {})["migrated_to_persona"] = True
        return True

    def save(self) -> None:
        self.data["updated_at"] = now_iso()
        write_json(_persona_file(self.bot, self.persona_id), self.data)

    # --- hypotheses (evidence-tied learning, persona-private) ---------------
    def upsert_hypothesis(self, hid: str, statement: str, confidence: float,
                          evidence: list[str]) -> None:
        confidence = max(0.0, min(1.0, confidence))
        h = self.data["hypotheses"].get(hid, {"evidence": []})
        h.update({
            "statement": statement,
            "confidence": round(confidence, 3),
            "updated_at": now_iso(),
        })
        h.setdefault("evidence", [])
        for e in evidence:
            if e not in h["evidence"]:
                h["evidence"].append(e)
        self.data["hypotheses"][hid] = h

    def get_hypothesis(self, hid: str) -> dict[str, Any] | None:
        return self.data["hypotheses"].get(hid)

    def hypothesis_count(self) -> int:
        return len(self.data.get("hypotheses", {}))

    # --- evidence consumption (persona-private, restart-safe) ---------------
    def consumed_ids(self) -> list[str]:
        return self.data.setdefault("consumed_signal_ids", [])

    def is_consumed(self, signal_id: str) -> bool:
        return signal_id in self.consumed_ids()

    def mark_consumed(self, signal_id: str) -> None:
        ids = self.consumed_ids()
        if signal_id not in ids:
            ids.append(signal_id)
