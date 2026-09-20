# Social Bots runtime architecture

Independent of SwarmAI. Python 3.11 standard library only — no external
dependencies, no new spend, no model gateway required to run the control loop.
A model is invoked only for interpretation/creative generation/review; the
deterministic parts (waiting, no-change detection, leasing, verification) never
call one.

## Independence from SwarmAI (enforced)

Nothing here imports, calls, queues into, or waits on SwarmAI. The whole system
runs from `python3 bin/run_worker.py <bot>` with only the stdlib present. There is
no SwarmAI adapter, model, memory, or coordination dependency anywhere in
`runtime/`.

## Three isolated runtimes

`social-a`, `social-b`, `social-c`. Each owns a private namespace tree; one bot
can never write into another's private memory (`runtime/paths.py` enforces safe
namespaces). Cross-bot facts must go through the explicit `shared` namespace.

```
<SBOTS_HOME>/                 # default: this directory; override per host/test
  state/<bot>/                # bot_state.json, last_decision.json
  memory/<bot>/               # observations, decisions, action_history, signals_inbox (JSONL)
  experiments/<bot>/          # <experiment_id>.json + index.jsonl
  content/<bot>/              # content_history.jsonl, publish_queue.jsonl
  analytics/<bot>/            # events.jsonl (schema-validated)
  receipts/<bot>/             # start/finish/failure receipts + index.jsonl
  heartbeats/<worker>.json    # liveness written by the actual process
  leases/<task>.lease.json    # atomic, one active owner per task
```

Persona workspaces (e.g. a cultural persona hosted on a runtime) use a nested
namespace like `social-a/cultural-atman`, keeping their memory/experiments
separate from the host persona's.

## Modules (`runtime/`)

| Module | Responsibility |
|---|---|
| `paths.py` | Namespace isolation; safe path helpers. |
| `jsonstore.py` | Crash-safe atomic JSON writes (`fsync`+`os.replace`) and append-only JSONL. |
| `leasing.py` | Atomic `O_CREAT\|O_EXCL` task leases; TTL staleness; stale takeover sets `reconcile_required`. |
| `heartbeat.py` | Process heartbeat (real pid) — liveness only when the running worker beats. |
| `receipts.py` | Sanitized start/finish/failure receipts + defensive secret redaction. |
| `state.py` | Per-bot durable state, hypotheses, ledgers. |
| `personas.py` | Persona load/validate + accidental-convergence (distinctness) detector. |
| `research.py` | Signals = captured evidence with provenance; never fabricates topics. |
| `pipeline.py` | Ideation → fact/voice/cultural review → format → dedup → experiment → publish queue (disabled). |
| `analytics.py` | Event schema separating bot/persona/platform/account/content/experiment/pub-id/time. |
| `decision.py` | The autonomy loop + decision records. |
| `worker.py` | Bounded, resumable, no-overlap single-unit worker. |

## The autonomy loop (`decision.run_cycle`)

OBSERVE (changed evidence only, via a signal-set fingerprint) → ORIENT
(known/inferred/uncertain + current objective) → GENERATE (alternatives) → SCORE
(value, learning, relevance, confidence, risk, cost, reversibility, duplication) →
CHOOSE (incl. NO_ACTION) → EXECUTE (local effects within `Authority` only;
publishing never in local authority) → VERIFY (destination, persona, unpublished,
review, platform limit) → LEARN (evidence-tied hypothesis update) → SCHEDULE
(deterministic next check).

- **No-change path is model-free:** if the evidence fingerprint is unchanged, the
  loop returns NO_ACTION without any generation step.
- **Every decision writes a record** (`memory/<bot>/decisions.jsonl` +
  `state/<bot>/last_decision.json`) listing the alternatives and why the winner won.

## Worker guarantees (`worker.run_one_unit`)

Acquire one atomic lease → (reconcile prior owner's effects if this was a stale
takeover) → renew → one cycle → verify → sanitized receipt → heartbeat → release.
Overlap raises `LeaseHeld` (the caller treats it as the no-overlap rejection).

## Evidence, not claims

- `bin/demo_worker_evidence.py` → `receipts/evidence/SB-002-run/` proves: 2
  invocations, heartbeat, atomic lease, no-overlap rejection, stale recovery,
  restart/resume.
- `bin/dry_run.py` → `receipts/evidence/SB-007-dryruns/` runs one real cycle per
  general persona on live-captured research + a cultural WITHHELD gate.
- `tests/` (26 stdlib unittest cases): `python3 -m unittest discover -s tests`.

## What still requires a human / owner (not faked here)

Deploying this worker on the owner's always-on host (R730/Windows) as a recurring
job; public-posting authorization; account MFA/CAPTCHA/consent; binding a named
cultural reviewer for the cultural personas. See `LAUNCH_GATE_PACKET.md`.
