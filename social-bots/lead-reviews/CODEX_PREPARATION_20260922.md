# Codex independent review preparation — Social Bots

Reviewer: Codex portfolio coordinator; bounded mechanical execution by a lower-cost subagent. No ChatGPT/Mac Acceptance identity is assumed. Owner clarified the minimum live target is **Bots V0.7**, with Jobs and SwarmAI V1.7. Native Bots ceiling remains V1.7; prioritize the complete V0.4–V0.7 proof chain.

## Source and ownership

Canonical contracts and latest LEAD-051: `chatgpt/social-bots-plan-20260920@6f794a0cfa1a55c3a8089090b8b9cbbb19106f8b`. Implementation owner remains Fable, session `s-20260921T211438Z-d5589881`, branch `fable/social-bots-v23-fasttrack-20260921@e9678f8bead4f872c199bdf09dbf709a8f649159`.

Tested source: `f0f1307cf99c181cf07f113672d5308cf5528386`. The subsequent `e9678f8` changes only `social-bots/SESSION_INSTRUCTIONS.md`; production and test trees are equivalent. R07-041 repair: `0bca4e654923932c755c89c20a85ec79b37d0a10`. LEAD-051 now records SUBMITTED / READY FOR INDEPENDENT ACCEPTANCE REVIEW, superseding its earlier rejection of `12c807e`.

Origin verified; isolated worktrees clean before edits. Fable remote dirty state/process is unavailable, so no implementation ownership is claimed. ChatGPT continues writing canonical coordination; Mac Acceptance is review-only. Cursor/Core/Intelligence remain parked. This is a docs-only proposal with no native queue/status promotion.

## Checks and recommendations

Transcript: `social-bots/receipts/evidence/CODEX-20260922/bots-checks.txt`. macOS independent execution, temporary homes, harmless sentinels and local child processes; no live model/account/public effect.

- Eight focused modules: **118 passed, 0 failed/errors/skipped**, including no-scope and production refusal, explicit ENGINEERING behavior, subprocess tripwire, shared budget/concurrency/reentry, SESSION_ONCE race, due rotation, final-review binding, prospective experiments, scope guard, loop/community negatives.
- Full discovery: **707 run; 703 passed, 2 failed, 2 skipped, 0 errors**. Host-preflight module rerun: 5 passed, same 2 failures.
- **RECOMMEND_ACCEPT**, narrowly, the R07-041 no-scope seam repair after authorized review of this independent evidence. No version or live acceptance is implied.
- **REWORK_FOUND** for a portable Mac full-suite claim: `tests/test_host_preflight.py:52–85` mocks Linux scheduler binaries without mocking `platform.system()`. On Darwin, `runtime/host_preflight.py:147` sees mocked launchctl=None and returns UNSUITABLE before attestation logic. The two expected clean-host verdicts therefore fail. This is test isolation, not a real-host suitability verdict.

Root inspected the repaired dispatch diff and failed test/platform branches. The worker's reported 707/2 is not a fresh passing Mac suite. Mac Acceptance and ChatGPT retain their native independent-review/formal-verdict requirements.

## Small next assignment

State: **PREPARED / WAITING_FOR_WORKER_ACK**; Fable remains sole implementation owner. Native lineage: SB-R07-072 host-preflight tests, SP1.

- Bound changes to `social-bots/tests/test_host_preflight.py`, with production changes only if a separate real defect is demonstrated.
- Make the simulated OS explicit; cover Linux and Darwin scheduler presence/absence plus attestation and ephemeral-host negatives. Do not weaken the live host predicate to make tests green.
- Rerun the host module and full Mac suite; return exact source SHA, discovered/pass/fail/error/skip counts. No scheduler installation or live model call.
- In parallel, designated Mac Acceptance reviews R07-041 and R07-071 evidence on the pinned candidate, without source edits. Codex's run is additional independent engineering evidence, not a fabricated Mac Acceptance acknowledgement.

## Live minimum remains REVIEW_BLOCKED

Official milestone position remains V0.4.x, with V0.3 accepted. Required V0.7 predecessors from `delivery/V17_ACCEPTANCE.md`: V0.4 real controlled divergence and SB-EVD-002; V0.5 current source-to-claim/review/render chain; V0.6 three real unpublished adaptive loops; V0.7 persistent owner host, at least three native scheduler firings, contention/crash/restart/stale takeover, and two genuine engineering-artifact → lead → later-worker cycles without owner relay.

The retained `af3fded92eaba5e68c8088737b68c6f043e40a5e` preflight/dossier reports an ephemeral Linux worker, no native scheduler, no canonical live authorization manifest and missing account/reviewer inputs. The exactly-one earlier canary grant is consumed. Reuse `worker-reports/fable-fasttrack/V17_GATE_DOSSIER.md`; obtain concrete host designation and fresh bounded model manifest before dependent live work. Later public canaries are not prerequisites invented for the V0.7 minimum.

Heartbeat: one SESSION_ONCE at `2026-09-21T21:14:38Z`; same session resumed and has material commits. No periodic tick is expected; no new heartbeat was emitted for this review or resume. Runtime recurrence remains unproven.

Requested verdict: ChatGPT/Mac Acceptance decide the bounded R07-041 repair, record the host-test rework, and route only the next authorized V0.7 prerequisite. No new account/model/public/spend grants or implementation replacement.
