# SESSION_INSTRUCTIONS — Windows Core / V0.3 closure

Mode: ACTIVE — FAST TRACK
Branch: `claude/social-bots-windows-core-host`
Lead review: LEAD-024

Heartbeat is observability only. Do not wait on heartbeat acceptance before coding.

At start/checkpoint:
1. `git pull --ff-only`
2. `git fetch origin`
3. read canonical `FAST_TRACK_EXECUTION.md` and `SESSION_ROUTER.md` with `git show`
4. inspect `worker-reports/windows-core/LEAD_ACK.json`
5. continue dependency-ready work without routine permission prompts.

## Priority 1 — SB-V03-004 post-cycle success-receipt fencing repair

The migration/load side-effect defect from LEAD-019 is repaired in `175f741...`: migration is staged in memory and durable cycle writes are fenced.

LEAD-024 found a separate ownership hole in `runtime/worker.py`:
- `decision.run_cycle(..., fence=fence)` returns after its durable decision/state/content commit;
- the worker then writes the `finish` receipt outside the fence;
- if the worker stalls after the cycle commit, its lease expires, and another worker takes over before the old worker resumes, the old worker can still emit a finish receipt implying `candidate_succeeded=true` / verified success after fence loss.

This violates SB-V03-004's acceptance rule that an old owner cannot commit receipts implying success after losing/expiring ownership.

Required repair:
1. fence or atomically ownership-check every durable post-cycle receipt/status write that can imply successful completion;
2. a stale owner after takeover must not write a success/finish receipt;
3. failure/fenced-out evidence may remain truthful, but must never be confused with success;
4. add an adversarial regression that pauses after the cycle commit, forces TTL expiry + generation takeover, then resumes the old worker and proves it cannot write a success finish receipt;
5. preserve the existing side-effect-free migration/fenced decision commit behavior and single-POSIX-host scope.

Do not fix this by only increasing TTL.

## Priority 2 — SB-V03-005 enforce the production persona read boundary

Commit `d1e4bee...` adds useful `PERSONA_SCOPED_READERS`, `persona_records()` and mixed-persona tests. Keep that work.

LEAD-024 found the remaining contract gap: wrapping raw readers in `_ADMIN_READERS` does not make the underlying raw APIs admin-only. Public/raw calls such as `pipeline.publish_queue(bot)` and `analytics.events_for(bot)` still enumerate the whole runtime, and direct JSONL access remains possible. The artifact requires normal production persona-specific flows to be structurally routed through the persona boundary, or raw whole-runtime APIs to be explicitly internal/admin and not accidentally usable as persona-facing reads.

Required repair:
1. route real production persona-facing read/list call sites through the authoritative persona-scoped interface;
2. rename/private/admin-scope raw whole-runtime APIs where they remain necessary, or otherwise enforce an equivalent explicit boundary;
3. cover content/dedup, experiment list/load, action history, decision history, analytics/history and publish-queue reads where persona-private;
4. keep intentional runtime-wide admin/reconciliation reads explicit and separate;
5. add regressions through actual production call paths proving a persona cannot enumerate another persona's private records.

## Priority 3 — regenerate SB-V03-006 after both repairs

The evidence bundle at `0433fc85...` is useful PREPARED evidence and truthfully reports 122 passing tests, but it predates the LEAD-024 repairs above and is not acceptance-eligible.

After SB-V03-004 and SB-V03-005 are repaired:
- regenerate the focused + full acceptance evidence from the new implementation SHA;
- include the new post-cycle receipt-takeover regression and production read-boundary regressions;
- do not represent the current prepared bundle as final acceptance proof.

## Then — V0.4 Core dependency reconciliation

Only after the V0.3 repair bundle is resubmitted:
- reconcile SB-V04-001/002/003/004;
- keep deterministic authority/policy ownership;
- do not run the real canary from this Linux-container lane.
Dedicated branch `claude/social-bots-v04-live-canary` owns `SB-V04-005`.

## CI / review

Mac QA owns independent QA/control and will independently probe the receipt-fence and reader-boundary scenarios. Do not duplicate its source ownership.

## Reporting

Reports stay under `social-bots/worker-reports/windows-core/`.
Commit/push after each parent artifact and continue to the next dependency-ready item.

## Safety

No public effects, paid API/new spend, destructive actions, secrets, fake evidence, or SwarmAI dependency.
