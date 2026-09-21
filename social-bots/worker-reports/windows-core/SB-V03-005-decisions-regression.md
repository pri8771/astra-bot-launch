# Coordinated contribution — SB-V03-005 persona decision-history regression

Contributed by: Intelligence-session (coordinating a NON-overlapping slice)
Branch: `claude/social-bots-windows-core-host`
Status: SUBMITTED — test-only; NOT self-accepted. Windows Core session retains
ownership of all `runtime/` Core source.

## Why this is non-overlapping

The Windows Core session owns and is actively implementing SB-V03-005. Its
`runtime/isolation.py` already exposes every persona-scoped read in the
Priority-2 list (content history, publish queue, experiments, analytics, action
history, **and** `persona_decisions`) plus an `audit()` helper, and
`tests/test_isolation.py` already regresses all of those stores — except one:
`persona_decisions` (decision history) had a live read API but **no
mixed-persona no-bleed regression**.

This contribution adds only that missing regression, in a **new** file
(`tests/test_isolation_decisions.py`) so it does not touch the sibling's
`test_isolation.py` or any `runtime/` Core source (`state.py`, `decision.py`,
`isolation.py`, etc. are all unmodified).

## What was added

`social-bots/tests/test_isolation_decisions.py` — 3 real production-path tests:
- two personas on one runtime each run `decision.run_cycle` (which writes
  `decisions.jsonl` inside the fenced commit); each persona's
  `isolation.persona_decisions` view contains only its own records;
- the two views are disjoint and their union equals the whole decisions store
  (no lost, double-counted, unlabeled, or foreign-persona record);
- `isolation.audit()` reports the `decisions` store clean.

## Evidence

- `python3 -m unittest tests.test_isolation_decisions` → 3 passing.
- `python3 -m unittest discover -s tests` → **118 passing** (was 115; +3).
- No `runtime/` source modified (verify: `git show --stat` for this commit lists
  only `tests/test_isolation_decisions.py` and this report + the AGENT_MESSAGES
  coordination note).

## Ownership / hand-back

Core source for SB-V03-004/005/006 remains the Windows Core session's. If the
sibling prefers this regression live inside `test_isolation.py`, it can fold it
in and delete this file — no dependency points at it. Flagging so we do not both
push the same decision-store test.
