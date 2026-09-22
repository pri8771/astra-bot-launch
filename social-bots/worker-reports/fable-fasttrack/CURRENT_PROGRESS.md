# fable-fasttrack — current progress (LIVE V1.7 only, then hard stop)

Session `s-20260921T211438Z-d5589881` (SESSION_ONCE, emitted 2026-09-21T21:14:38Z at this session's start; the same session was resumed after a container restore and ingested LEAD-048/LEAD-050 — no second heartbeat per the owner rule "one fresh session = one SESSION_ONCE; none on resume") · branch `fable/social-bots-v23-fasttrack-20260921` · canonical read `550f2b1` (LEAD-050) · scope `delivery/V17_LIVE.md` / `V17_SCOPE.json` / `V17_ACCEPTANCE.md`.

Owner target change ingested: get Social Bots to **V1.7 genuinely LIVE, then stop**. The V2.3 specialist/strategy work submitted earlier in this session (checkpoint `a204ad0`, SB-S23-001..008, SB-S20-001) is **parked and preserved**; nothing in it is advanced or counted. Prior suite figure 523/2 is historical; every count below is a fresh run on the named SHA.

## V1.7 §A — zero-live repairs (actual modules)

| Item | Card | Source SHA | Evidence | Suite on SHA | Class | Finish state |
|---|---|---|---|---|---|---|
| A1 shared pre-dispatch authorization + budget gate (LEAD-047 P0 set) | SB-R07-041 / C04 | `12c807e` | `receipts/evidence/SB-R07-041/run-20260922T013241Z/` (5/5 defects reproduced on `347de2b`, 0/5 on `12c807e`) · report `SB-R07-041.md` | 559 discovered / 557 passed / 0 fail / 0 error / 2 skipped | ENGINEERING (fixture sentinels, real process) | READY_FOR_LEAD_REVIEW (code); BLOCKED_AUTHORIZATION for any LIVE_MODEL proof |
| A2 independent re-run of atomic heartbeat/lease/fence/worker_once suites + cross-process lock prover | SB-V03-00x / SB-V07-001 durability | `12c807e` | `receipts/evidence/SB-V17-A2-lease-heartbeat/run-20260922T013154Z/` — 58 tests OK; `prove_cross_process_lock.py`: 8 spawned interpreters, 1 acquired, 7 `LeaseHeld`, 0 errors, `single_owner_ok: true`, flock available | (subset of the full run above) | ENGINEERING (REAL_PROCESS on this ephemeral Linux VM, not the persistent host) | READY_FOR_LEAD_REVIEW (engineering); host-bound proof BLOCKED_HOST |
| A3 no first-bot starvation in scheduled due-work selection | SB-V07-001 (scheduler selection) | `b5fd038` | `tests/test_due_rotation.py` (10) | 569 discovered / 567 passed / 0 fail / 0 error / 2 skipped | ENGINEERING | READY_FOR_LEAD_REVIEW |
| A4 final-content review binding (formatting invalidates prior review; enqueue refuses unbound/mismatched; exact bytes verified at consumption) | C05 / C06 | — | — | — | — | IN PROGRESS |
| A5 prospective experiment registration (no fabricated baseline/outcome/confidence) | C07 | — | — | — | — | QUEUED |
| A6 V1.7 scope guard (dispatcher never imports/selects strategy/planner/specialist routes) | V17_SCOPE worker_requirement | — | — | — | — | QUEUED |
| A7 read-only host/provider/account preflight + single gate dossier | C09 / owner gates | — | preflight capture started | — | — | QUEUED |

Then: B (V0.4–V0.7 recovery/live proof — owner-gated), C (accounts/canaries — owner-gated), D (C03 producers + loop wiring), E (V1.7 community path offline + negative controls), F (final packet, evidence index, independent-review request).

## Hard facts about this host (for the gate dossier)

Ephemeral Linux CCR VM (`Linux 6.18.44-fc-v37`, Python 3.11.15, PID 1 is the session supervisor, no cron/systemd/launchctl), `claude` CLI on PATH, `gh` absent (GitHub via MCP), outbound HTTPS only through the agent proxy and the social platforms are refused by policy. It is **not** the persistent host V0.7+ requires: native-scheduler, account, canary and analytics evidence cannot be produced here (BLOCKED_HOST / BLOCKED_ACCOUNT). No canonical authorization manifest exists on any branch: LIVE_MODEL is BLOCKED_AUTHORIZATION.

## Authority posture

No model call, no public post/reply/DM, no spend, no account mutation, no destructive action, no main release. Workers submit; ChatGPT accepts. Independent audit by the Acceptance lane is requested on each pinned SHA above and has not been performed.
