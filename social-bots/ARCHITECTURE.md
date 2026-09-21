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
| `leasing.py` | `flock`-CAS task leases; TTL staleness; stale takeover sets `reconcile_required`; per-task fencing `generation` + `Fence.fenced_commit` for active-cycle commit fencing. |
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

## Concurrency model (SB-R0B)

- **Lease CAS.** `leasing.acquire` runs the whole "is the current lease missing or
  stale? then claim it" sequence inside an exclusive per-task `fcntl.flock`
  critical section, so a fresh claim and a stale takeover are both single-owner
  even under concurrent contention on one host. The kernel releases `flock` if the
  holder dies, so a crash cannot wedge it. (`FLOCK_AVAILABLE` is False on non-POSIX
  hosts, which fall back to atomic-replace; the Linux host asserts the strong
  path.) This replaced an earlier rename-CAS that had a clobber window.
- **Runtime-state boundary.** A runtime's `bot_state.json` (consumed-signal ledger,
  hypotheses, counters) is shared by every persona workspace on that runtime, so
  the worker lease is keyed by the **runtime (`cycle:<bot>`)**, not by
  `(bot, persona)`. Two personas on one runtime therefore cannot mutate that state
  concurrently — the second cycle is rejected (no-overlap) — which prevents lost
  updates. Personas keep isolated experiment/content/memory *namespaces* for their
  non-shared artifacts. Full per-persona state isolation is a deliberate future
  alternative if per-runtime concurrency is ever required.
- Proven by `tests/test_concurrency.py`: 6-way concurrent stale takeover and fresh
  create each yield exactly one owner across 40 rounds; a second persona on a held
  runtime is rejected; 25 rounds of concurrent general+cultural cycles leave the
  cycle counter equal to the number of cycles that ran (no lost update), a
  duplicate-free consumed ledger, and uncorrupted `bot_state.json`.

## Active-cycle fencing (SB-V03-004)

The lease CAS above only protects **acquisition**. It does not, by itself, stop a
worker whose lease expires *during* `decision.run_cycle()` from committing after
another worker has taken over. That is closed by a fencing token:

- **Fence token.** Each lease carries a strictly increasing per-task
  `generation`. A fresh slot starts at 1; a stale takeover bumps the prior
  generation. A generation is monotonic per task, so a superseded owner can never
  again match the on-disk generation — its fence is permanently invalid.
- **Fenced commit.** `leasing.Fence.fenced_commit(commit)` runs the ownership
  check **and** the commit inside the *same* per-task `flock` critical section
  that a takeover's `acquire` uses. So the check-and-write is atomic w.r.t.
  takeover: either this worker is still the sole owner and the commit runs while
  the lock is held (no takeover can interleave), or a takeover already bumped the
  generation and the commit is refused with `FenceLost` — writing nothing.
- **All-or-nothing cycle commit.** `decision.run_cycle(..., fence=...)` PREPARES
  the outcome, then commits every durable artifact — shared `bot_state.json`
  (consumed ledger, counters, hypotheses), experiment registration, publish-queue
  entry, success analytics and the decision log — through one `fenced_commit`.
  A fenced-out worker therefore advances no state, registers no experiment, queues
  nothing, and writes no success receipt. `worker.run_one_unit` catches
  `FenceLost` and stands down with a truthful `fence_lost` receipt
  (`candidate_succeeded=false`); it never deletes the new owner's lease.
- **Ownership is inspectable** after a race via `leasing.inspect(task)` (lease_id,
  generation, worker_id) and via `fence_generation` on start/finish receipts.
- Proven by `tests/test_fencing.py`: generation increments on takeover; the old
  owner's fence is invalid and cannot renew or `fenced_commit`; a mid-cycle
  takeover leaves zero durable artifacts and an unadvanced state while the takeover
  worker becomes owner (gen 2) and commits; `run_one_unit` returns `fence_lost`.

### Host / filesystem scope (explicit)

- **Guaranteed:** one **POSIX host**, one **local filesystem**. `fcntl.flock`
  gives the mutual exclusion the fenced commit relies on, and the kernel frees the
  lock if the holder dies.
- **Not proven — native Windows.** `FLOCK_AVAILABLE` is False; the fallback is
  atomic-replace only and does **not** provide the flock critical section, so the
  strong active-cycle fence is **not** claimed there. A Windows deployment needs a
  separate, proven mechanism (e.g. `LockFileEx`) before any equivalent claim.
- **Not proven — cross-host / network filesystem.** `flock` semantics over NFS/SMB
  and across machines are unreliable; multi-host fencing would require a shared
  authority (a lease service or a DB with compare-and-set), which is out of scope
  here and must not be assumed. The Linux always-on host asserts `FLOCK_AVAILABLE`.

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
