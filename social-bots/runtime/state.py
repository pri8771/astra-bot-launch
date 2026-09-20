"""Per-bot durable state — logically isolated thinking & learning.

Each bot owns: goals, working_state, long-term memory, observations, hypotheses,
experiment history, content history, analytics history, pending decisions, action
history, recovery state. Isolation is enforced by ``paths`` namespacing; one bot
can never write into another's private tree. Cross-bot facts go through the
explicit ``shared`` namespace only.
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
        "observation_fingerprint": None,  # last-seen evidence hash (no-change path)
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
