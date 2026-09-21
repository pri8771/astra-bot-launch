# Social Bots — compact current state

Source of truth remains `../STATE.json`; this file is the startup summary.

Updated from LEAD-041.

## Version

- Official: **V0.4.x**
- Completed: V0.3
- Target sequence: honest V0.7 recovery -> V2.3 ASAP -> continue through V3.0
- V3.0 is a planning/architecture compatibility target until V2.3 works.

## Implementation

Primary branch:
`cursor/social-bots-recovery-v07-20260921`

Latest verified material source inherited into recovery:
`a73b7b58de8f3669795b81637bff55247d67943c`

Latest verified reported suite:
**312 passed, 1 skipped**

Immediate artifact:
**SB-R07-071 — atomic cross-process SESSION_ONCE uniqueness**

Then:
SB-R07-041 -> SB-R07-044 -> SB-R07-072 -> dependency-ready recovery artifacts.

## Hard blockers / gates

- SB-V04-002 / SB-V04-004 require a future fixed five-call LIVE adaptive divergence batch.
- That batch is **not authorized**.
- It requires fresh explicit owner authorization + matching ChatGPT lead authorization manifest.
- No public social effect or new spend is authorized through the current recovery work.
- V0.7 LIVE acceptance requires real native OS-scheduler evidence on an owner-controlled persistent host.

## Heartbeat

One fresh session = one heartbeat. Current inherited heartbeat implementation still has an atomicity defect tracked by SB-R07-071.

For full detail, read only when needed:
- `../STATE.json`
- `../WORK_QUEUE.md`
- latest `../lead-reviews/`
