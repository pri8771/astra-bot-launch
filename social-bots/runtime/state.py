"""Per-runtime durable state (SB-V03-005 isolation contract).

``bot_state.json`` is SHARED RUNTIME STATE: one per runtime, holding the
consumed-signal ledger, hypotheses, counters, recovery/in-flight and the
observation fingerprint. Every persona hosted on the runtime shares it (e.g.
``social-a`` and ``cultural-primandir-atman`` both run on ``social-a``), because
evidence is captured for the runtime and consumed exactly once for the runtime.
Concurrent mutation is prevented by the runtime lease (``cycle:<bot>``) and the
active-cycle fence (SB-V03-004): only the fenced owner may commit it.

Non-shared PERSONA data (content history, experiments, publish queue, analytics
events, action/decision records) lives in the runtime's append-only stores but is
LOGICALLY isolated per persona: every such record carries an explicit ``persona``
field and a persona-derived, collision-free identity key. It is NOT physically
nested per persona. Persona-specific reads go through ``runtime.isolation``;
``runtime.isolation`` documents and ``tests/test_isolation.py`` proves the
contract. One bot's ``paths`` namespace can never be written by another bot;
cross-bot facts use the explicit ``shared`` namespace only.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from . import paths
from .jsonstore import read_json, write_json, append_jsonl, read_jsonl, now_iso

_STATE_FILE = "bot_state.json"


def _default_state(bot: str) -> dict:
    return {
        "bot": bot,
        "schema_version": 1,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "goals": [],
        "working_state": {},
        "hypotheses": {},          # id -> {statement, confidence, evidence[], updated_at}
        "consumed_signal_ids": [],  # signals already decided upon (evidence consumption)
        "observation_fingerprint": None,  # diagnostic: fingerprint at last cycle
        "pending_decisions": [],
        "recovery": {"last_clean_tick": None, "in_flight": None},
        "counters": {"cycles": 0, "actions": 0, "no_action": 0},
    }


@dataclass
class BotState:
    bot: str
    data: dict = field(default_factory=dict)

    @classmethod
    def load(cls, bot: str) -> "BotState":
        if bot not in paths.BOTS:
            raise ValueError(f"unknown bot {bot!r}; expected one of {paths.BOTS}")
        p = paths.state_dir(bot) / _STATE_FILE
        data = read_json(p, default=None) or _default_state(bot)
        return cls(bot=bot, data=data)

    def save(self) -> None:
        self.data["updated_at"] = now_iso()
        write_json(paths.state_dir(self.bot) / _STATE_FILE, self.data)

    # --- memory / ledgers (append-only) -------------------------------------
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

    def content_history(self) -> list[dict]:
        return read_jsonl(paths.content_dir(self.bot) / "content_history.jsonl")

    # --- hypotheses (evidence-tied learning) --------------------------------
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

    # --- evidence consumption (restart-safe) --------------------------------
    def consumed_ids(self) -> list[str]:
        return self.data.setdefault("consumed_signal_ids", [])

    def is_consumed(self, signal_id: str) -> bool:
        return signal_id in self.consumed_ids()

    def mark_consumed(self, signal_id: str) -> None:
        ids = self.consumed_ids()
        if signal_id not in ids:
            ids.append(signal_id)
