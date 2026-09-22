#!/usr/bin/env python3
"""Synthetic no-network reproducer for repeated unavailable-reasoning cycles."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from runtime import decision, paths, research
from runtime.jsonstore import read_json, read_jsonl
from runtime.state import PersonaState, RuntimeState

BOT = "social-b"
PERSONA = "social-b"


def seed() -> None:
    signal = research.Signal.make(
        "synthetic reliability input",
        "controlled local input",
        "reliability-harness",
        "https://example.invalid/synthetic",
        "fixture",
        ["reliability"],
    )
    research.capture(BOT, signal)
    print(json.dumps({"seeded_signal_id": signal.id, "home": os.environ["SBOTS_HOME"]}))


def run() -> None:
    record = decision.run_cycle(BOT, PERSONA, require_adaptive=True)
    print(
        json.dumps(
            {
                "cycle": record["cycle"],
                "outcome": record["outcome"],
                "consumed_this_cycle": record["observe"]["consumed_this_cycle"],
                "pending_after": record["observe"]["pending_after"],
                "provider": record["reasoning"]["provider"],
                "provider_available": record["reasoning"]["available"],
                "live_model_call": record["reasoning"]["live_model_call"],
                "next_check_in_hours": record["schedule"]["next_check_in_hours"],
            },
            sort_keys=True,
        )
    )


def report() -> None:
    rt = RuntimeState.load(BOT)
    ps = PersonaState.load(BOT, PERSONA, runtime=rt)
    decisions = read_jsonl(paths.memory_dir(BOT) / "decisions.jsonl")
    pending = research.unconsumed_signals(BOT, ps.consumed_ids())
    home = Path(os.environ["SBOTS_HOME"])
    files = sorted(str(p.relative_to(home)) for p in home.rglob("*") if p.is_file())
    payload = {
        "result": "REPRODUCED_UNBOUNDED_UNAVAILABLE_RETRY",
        "decision_count": len(decisions),
        "cycles": [d["cycle"] for d in decisions],
        "outcomes": [d["outcome"] for d in decisions],
        "consumed_this_cycle": [d["observe"]["consumed_this_cycle"] for d in decisions],
        "pending_after": [d["observe"]["pending_after"] for d in decisions],
        "next_check_hours": [d["schedule"]["next_check_in_hours"] for d in decisions],
        "live_model_calls": [d["reasoning"]["live_model_call"] for d in decisions],
        "consumed_ids": ps.consumed_ids(),
        "pending_signal_ids": [s["id"] for s in pending],
        "runtime_cycles": rt.data["counters"]["cycles"],
        "last_decision": read_json(paths.state_dir(BOT) / "last_decision.json"),
        "runtime_files": files,
        "dead_letter_or_block_files": [
            name for name in files if "dead" in name.lower() or "block" in name.lower()
        ],
    }
    assert payload["decision_count"] >= 4
    assert set(payload["outcomes"]) == {"blocked_reasoning_unavailable"}
    assert set(payload["consumed_this_cycle"]) == {None}
    assert set(payload["pending_after"]) == {1}
    assert set(payload["next_check_hours"]) == {6}
    assert set(payload["live_model_calls"]) == {False}
    assert payload["consumed_ids"] == []
    assert len(payload["pending_signal_ids"]) == 1
    assert payload["dead_letter_or_block_files"] == []
    print(json.dumps(payload, indent=2, sort_keys=True))


parser = argparse.ArgumentParser()
parser.add_argument("mode", choices=("seed", "run", "report"))
args = parser.parse_args()
{"seed": seed, "run": run, "report": report}[args.mode]()
