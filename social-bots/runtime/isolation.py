"""SB-V03-005 — persona/runtime isolation contract (logical isolation model).

A runtime (``social-a``/``social-b``/``social-c``) hosts more than one persona:
``social-a`` hosts the general ``social-a`` persona AND the cultural
``cultural-primandir-atman`` persona; ``social-b`` hosts ``social-b`` and
``cultural-primandir-utsava``. This module defines — and the tests prove — how
those personas coexist on one runtime without corruption or cross-persona
contamination.

Three classes of data (SB-V03-005):

0. SHARED CAPTURE CATALOG — the runtime signal inbox
   ``memory/<bot>/signals_inbox.jsonl``. Captured evidence is shared and
   READ-ONLY to decision cycles; the same signal can be independently considered
   by every persona on the runtime (consumption is tracked per persona, below).

1. SHARED RUNTIME STATE — one per runtime, in ``state/<bot>/bot_state.json``:
   process/health counters, recovery/in-flight and the observation fingerprint
   ONLY. It no longer holds the consumed ledger or hypotheses — those are
   persona-private. Concurrent mutation is prevented by the runtime lease
   (``worker.runtime_task_id`` -> ``cycle:<bot>``) and the active-cycle fence
   (SB-V03-004): only the fenced owner may commit it.

1b. PERSONA-PRIVATE STATE — one per persona/workspace, in
   ``state/<bot>/persona-<persona_id>.json``: this persona's consumed-signal
   ledger, hypotheses, working state, pending decisions and goals. A signal that
   ``social-a`` consumes stays unconsumed for ``cultural-primandir-atman`` on the
   same runtime, and one persona's hypothesis count never enters another
   persona's reasoning context.

2. NON-SHARED PERSONA DATA — each persona's own content, experiments, publish
   queue, analytics events, action records and decision records. These live in
   the runtime's append-only stores (``content/<bot>``, ``experiments/<bot>``,
   ``analytics/<bot>``, ``memory/<bot>``) but are LOGICALLY isolated, not
   physically nested. The isolation contract is:

     (a) every non-shared record carries an explicit ``persona`` field;
     (b) every identity key is persona-derived and therefore collision-free
         across personas: ``content_id = H(persona:signature_move:signal_id)``,
         ``content_key = H(persona|signal_id|signature_move)``,
         ``experiment_id = "exp-" + content_id``. Two personas acting on the
         same signal produce different ids by construction, so one persona's
         record can never be mistaken for another's;
     (c) every read that must be persona-specific goes through the filters in
         this module, which select strictly by the ``persona`` field.

Why logical (not physical nesting): the shared runtime state must stay shared and
serialized, and the experiment/content stores are owned by the Intelligence lane
(``pipeline.py``). Logical isolation keeps a single audited contract across both
lanes without a cross-lane storage-layout change. ``ARCHITECTURE.md`` documents
this exact model so the docs and code agree (SB-V03-005 reconciliation).

Host/filesystem scope is identical to the lease/fence: single POSIX host, single
local filesystem. No function here performs any external/public effect.
"""
from __future__ import annotations

from . import paths, analytics, pipeline
from .jsonstore import read_jsonl

# The keys of SHARED runtime state (bot_state.json), for docs/audit assertions.
# Note: consumed_signal_ids and hypotheses are NO LONGER here — they are
# persona-private (see PERSONA_PRIVATE_STATE_KEYS).
SHARED_RUNTIME_STATE_KEYS = (
    "counters", "recovery", "observation_fingerprint",
)

# The keys of PERSONA-PRIVATE state (persona-<id>.json).
PERSONA_PRIVATE_STATE_KEYS = (
    "consumed_signal_ids", "hypotheses", "working_state", "pending_decisions",
    "goals",
)

# The non-shared stores that MUST partition cleanly by persona.
PERSONA_SCOPED_STORES = (
    "content_history", "publish_queue", "experiments", "analytics_events",
    "action_history", "decisions",
)


def _persona_of(record: dict) -> str | None:
    return record.get("persona")


# --------------------------------------------------------------------------- #
# Persona-scoped read/filter views over the shared runtime stores.
# Each returns ONLY the given persona's records; a record lacking a persona
# label is never attributed to a persona (it is surfaced by ``audit`` instead).
# --------------------------------------------------------------------------- #
def persona_content_history(bot: str, persona: str) -> list[dict]:
    rows = read_jsonl(paths.content_dir(bot) / "content_history.jsonl")
    return [r for r in rows if _persona_of(r) == persona]


def persona_publish_queue(bot: str, persona: str) -> list[dict]:
    return [e for e in pipeline.publish_queue(bot) if _persona_of(e) == persona]


def persona_experiments(bot: str, persona: str) -> list[dict]:
    idx = read_jsonl(paths.experiments_dir(bot) / "index.jsonl")
    return [r for r in idx if _persona_of(r) == persona]


def persona_analytics(bot: str, persona: str) -> list[dict]:
    return [e for e in analytics.events_for(bot) if _persona_of(e) == persona]


def persona_action_history(bot: str, persona: str) -> list[dict]:
    rows = read_jsonl(paths.memory_dir(bot) / "action_history.jsonl")
    return [r for r in rows if _persona_of(r) == persona]


def persona_decisions(bot: str, persona: str) -> list[dict]:
    rows = read_jsonl(paths.memory_dir(bot) / "decisions.jsonl")
    return [r for r in rows if _persona_of(r) == persona]


_READERS = {
    "content_history": lambda bot: read_jsonl(paths.content_dir(bot) / "content_history.jsonl"),
    "publish_queue": lambda bot: pipeline.publish_queue(bot),
    "experiments": lambda bot: read_jsonl(paths.experiments_dir(bot) / "index.jsonl"),
    "analytics_events": lambda bot: analytics.events_for(bot),
    "action_history": lambda bot: read_jsonl(paths.memory_dir(bot) / "action_history.jsonl"),
    "decisions": lambda bot: read_jsonl(paths.memory_dir(bot) / "decisions.jsonl"),
}


def audit(bot: str, personas: list[str]) -> dict:
    """Prove the non-shared stores partition cleanly by persona.

    For each store: every record carries a known persona, the per-persona
    filtered views are disjoint, and their union is the whole store (no record is
    lost or double-counted). Returns a structured report; ``clean`` is True only
    if every store partitions with no unlabeled or unknown-persona record.
    """
    report: dict = {"bot": bot, "personas": list(personas), "stores": {}, "clean": True}
    known = set(personas)
    for store, reader in _READERS.items():
        rows = reader(bot)
        labels = [_persona_of(r) for r in rows]
        unlabeled = sum(1 for l in labels if l is None)
        unknown = sorted({l for l in labels if l is not None and l not in known})
        per_persona = {p: sum(1 for l in labels if l == p) for p in personas}
        partitions_cover = (sum(per_persona.values()) + unlabeled
                            + sum(1 for l in labels if l in unknown) == len(rows))
        store_clean = (unlabeled == 0 and not unknown)
        report["stores"][store] = {
            "total": len(rows),
            "per_persona": per_persona,
            "unlabeled": unlabeled,
            "unknown_persona": unknown,
            "partition_covers_all": partitions_cover,
            "clean": store_clean,
        }
        if not store_clean:
            report["clean"] = False
    return report
