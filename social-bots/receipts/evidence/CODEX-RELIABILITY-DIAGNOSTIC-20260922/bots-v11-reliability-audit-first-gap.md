# Bots SB-V11-001/002 read-only reliability audit — first reproduced gap

## Source and authorization

- Accepted source: `8c86898d1c6641adbf5c9884e1aa7ab2923b1af3`
- Tree: `72bccc0dc5ee9eaf2919dcdfd0ac35b568719c5a`
- Release: `social-bots/lead-reviews/LEAD-062_2026-09-22T0805.md` on canonical coordination ref.
- Scope used: synthetic temporary runtime only; no provider/model/network/account/public/host/scheduler action.

## Existing reliability map read before stop

- **Live provider call budget:** `runtime/authorization.py` reserves a bounded slot before provider construction/spawn and makes failed/unavailable/malformed outcomes non-retryable within that authorization. `runtime/model_dispatch.py` classifies `provider_exception` and `provider_unavailable` and records the reserved outcome.
- **Reasoning unavailable/invalid:** `runtime/decision.py:174-221` emits `blocked_reasoning_unavailable`, performs no effect, explicitly leaves the signal unconsumed, writes a durable decision, and schedules the changed-evidence path again in six hours.
- **Account route unavailable:** platform selection classifies unavailable/unauthorized routes as blocked; the decision path produces `no_platform`, no experiment or queue entry. The normal post-decision path then consumes the signal (`decision.py:270-279`).
- **Research request:** `RESEARCH_MORE` is a local no-effect outcome (`decision.py:488-492`); the normal post-decision path consumes the signal. No separate retry/dead-letter behavior was found during this bounded read.
- **Restart/reconciliation:** persona consumed IDs and signal inbox are durable. Worker stale-lease takeover invokes `_reconcile`, currently limited to checking the unpublished queue for unauthorized published entries (`runtime/worker.py:192-208`).
- **Dead-letter/block store:** no generic durable dead-letter or exhausted-block state was found before the stop point.

## REWORK_FOUND — unavailable reasoning retries indefinitely

`decision.run_cycle(..., require_adaptive=True)` with changed evidence and no adaptive provider follows this causal path:

1. it chooses the unavailable adaptive-required provider (`decision.py:149-181`);
2. it emits a truthful, no-effect `blocked_reasoning_unavailable` decision (`200-216`);
3. it deliberately does not consume the signal (`217-220`);
4. it schedules another changed-evidence check after six hours (`216`, `_schedule` at `296-300`);
5. the durable commit writes runtime/persona state and another decision record (`684-717`), but no per-signal blocker attempt count, backoff, exhausted state or dead-letter record;
6. after process restart, the same unconsumed signal is selected again and the identical path repeats.

The retained harness seeded one synthetic signal and invoked four **separate Python processes** against the same temporary `SBOTS_HOME`. All four cycles returned `blocked_reasoning_unavailable`, `consumed_this_cycle=null`, `pending_after=1`, `next_check_in_hours=6`, and `live_model_call=false`. Runtime cycles advanced 1→4, four decision records accumulated, the consumed ledger remained empty, and the same signal remained pending. The only durable files were ordinary signal, decision and state files; no dead-letter/block file appeared.

Artifacts:

- `/tmp/bots-v11-unavailable-retry-repro.py` — SHA-256 `92e9d6ff7c5abcf7b877ddb5ab99144a93521cc421353c51f00c7157e24485b7`
- `/tmp/bots-v11-unavailable-retry-repro.log` — SHA-256 `743ad625e41b34761405da2dd93bc68898cba7fbcc4de8dfa7673d4d4e8b97bd`

Exact execution from `/Users/pchordia/Downloads/swarm_codex/review/bots-composition-source/social-bots`:

```text
home=$(mktemp -d /tmp/bots-v11-unavailable-home.XXXXXX)
for mode in seed run run run run report; do
  env -u SBOTS_REASONING -u SBOTS_REASONING_REQUIRE_ADAPTIVE SBOTS_HOME="$home" PYTHONPATH="$PWD" python3 /tmp/bots-v11-unavailable-retry-repro.py "$mode"
done
```

This is a bounded-retry defect, not an unsafe effect: no provider was dispatched and no external action occurred. It can cause every scheduled invocation to reconsider the same unchanged blocker forever, grow decision/receipt history, and prevent later signals from reaching the head of the oldest-first queue.

## Smallest repair proposal

Request a separate bounded repair release for a durable persona/signal blocker ledger keyed by signal ID plus stable blocker classification/fingerprint. Repeated unchanged `reasoning_unavailable` outcomes should increment a bounded attempt count and use bounded backoff; at a lead-selected ceiling, move the signal into an explicit exhausted/blocked state that is excluded from ordinary oldest-first retries but remains inspectable and is not represented as successfully decided. A material route/provider availability change or explicit operator reset may re-queue it under a specified rule.

The repair should preserve current fail-closed/no-effect behavior, avoid consuming unresolved evidence as success, allow later signals to progress, survive restart, expose the exact block category/attempts/next eligibility, and never grant a fresh live-call budget or silently retry a consumed authorization slot.

Per LEAD-062, the audit stopped at this first concrete gap. No source or test file was edited.
