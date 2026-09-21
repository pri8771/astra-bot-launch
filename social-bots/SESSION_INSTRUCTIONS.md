# SESSION_INSTRUCTIONS — Windows Core / V0.3 closure

Mode: ACTIVE — FAST TRACK
Branch: `claude/social-bots-windows-core-host`
Lead review: LEAD-023

Heartbeat is observability only. Do not wait on heartbeat acceptance before coding.

At start/checkpoint:
1. `git pull --ff-only`
2. `git fetch origin`
3. read canonical `FAST_TRACK_EXECUTION.md` and `SESSION_ROUTER.md` with `git show`
4. inspect `worker-reports/windows-core/LEAD_ACK.json`
5. continue dependency-ready work without routine permission prompts.

## SB-V03-004 — repair submitted; HOLD implementation unless QA finds a defect

Lead independently inspected commit `175f741fcedace3113191a847d6a7568d77b9cde`.
The LEAD-019 migration-side-effect defect appears repaired: PersonaState load/migration staging is side-effect free and durable migration writes flow through the fenced commit, with a stale-owner regression.

Mac QA is assigned an independent verification pass. Do not keep reworking V03-004 unless that review finds a concrete defect.

## Priority 1 — SB-V03-005 authoritative persona read boundary

Finish this now.

Preserve the RuntimeState/PersonaState split and migration repair.

Add one authoritative persona-scoped production interface for private/personalized stores and route normal production reads through it. At minimum cover actual production paths for:
- content history/dedup;
- experiment load/list;
- action history;
- decision history;
- analytics/history where persona-private;
- publish queue reads where applicable.

Raw whole-runtime reads may remain only when explicitly named/documented admin/internal and not used by normal persona-facing production flows.

Add mixed-persona regressions through the real production read/list APIs proving one persona cannot enumerate or accidentally consume another persona's private records.

Submit `SB-V03-005` with exact source SHA, focused tests, full relevant suite, and known limits.

## Priority 2 — SB-V03-006 fresh V0.3 acceptance bundle

After V03-005 is complete and your branch suite is green:
- regenerate fresh evidence from the current implementation;
- include V03-002/003/004/005 adversarial scenarios;
- do not reuse superseded proof;
- submit `SB-V03-006`.

## Priority 3 — V0.4 Core dependency reconciliation

After the V0.3 bundle is submitted:
- reconcile SB-V04-001/002/003/004 with the current accepted contracts;
- keep deterministic authority/policy ownership;
- do not run the real canary from this Linux-container lane.
The dedicated local authenticated branch `claude/social-bots-v04-live-canary` owns `SB-V04-005`.

## CI / review

Mac QA owns CI/control and independent V03-004 verification. Do not duplicate that lane.

## Reporting

Reports stay under `social-bots/worker-reports/windows-core/`.
Commit/push after each parent artifact and continue to the next dependency-ready item.

## Safety

No public effects, paid API/new spend, destructive actions, secrets, fake evidence, or SwarmAI dependency.
