# SESSION_INSTRUCTIONS — Windows Core / V0.3 closure + V0.4 prep

Mode: ACTIVE — FAST TRACK
Branch: `claude/social-bots-windows-core-host`
Lead review: LEAD-027

Heartbeat is observability only. Do not wait on heartbeat acceptance before coding.

At start/checkpoint:
1. `git pull --ff-only`
2. `git fetch origin`
3. read canonical `FAST_TRACK_EXECUTION.md` and `SESSION_ROUTER.md` with `git show`
4. inspect `worker-reports/windows-core/LEAD_ACK.json`
5. continue dependency-ready work without routine permission prompts.

## ACCEPTED by lead — SB-V03-005

LEAD-027 independently inspected final implementation `796d4e390bd135167e5de2ff8f586bc07ac7f370` and accepts SB-V03-005.

Preserve:
- `RuntimeState.admin_content_history()`; ordinary `content_history()` is gone;
- `pipeline.admin_publish_queue()` and `analytics.admin_events_for()` explicit admin surfaces;
- `isolation.PERSONA_SCOPED_STORES` and authoritative persona readers for all six private stores;
- `isolation.admin_all_records()` as the explicit whole-runtime boundary;
- all-surface structural regression that fails if bare whole-runtime reader names are reintroduced;
- logical persona isolation architecture and production-path no-bleed tests.

Do not churn V03-005 unless independent QA identifies a concrete defect.

## Preserve — SB-V03-004 source repair; independent execution still gates acceptance

Lead source review continues to support the fencing/migration implementation, including the post-cycle success-receipt takeover repair. SB-V03-004 remains CHANGES_REQUIRED only because its artifact contract requires independent execution of the high-risk lifecycle race. Mac QA owns that verification.

Do not weaken, rewrite, or self-accept this artifact while waiting for QA.

## Final V0.3 evidence is PREPARED

Evidence commit `436787b0a63fdae0e89c224a54054607e32b5187` regenerates SB-V03-006 from final implementation `796d4e3...` and commits exact full-suite output: `Ran 130 tests ... OK`.

Do not regenerate again unless:
- independent QA finds a defect and source changes; or
- lead explicitly requests evidence refresh.

V03-006 remains blocked on V03-004 independent acceptance and final lead reconciliation of V03-001 / SB-EVD-001.

## Current implementation assignment — dependency-safe V0.4 reconciliation/test prep

While Mac QA executes the independent V03-004 probe, use Core capacity without overlapping the dedicated live-canary lane:
1. Re-audit SB-V04-001 against the current production path. Preserve fail-closed behavior when adaptive reasoning is required; close any remaining schema/authority/default-mode defects with focused tests.
2. Re-audit SB-V04-002 implementation and tests. Keep injected/provider-runner tests clearly engineering-only; do not represent them as the required real canary.
3. Re-audit SB-V04-003 deterministic policy boundary and preserve deterministic authority/no-public-effect rules.
4. Prepare/implement SB-V04-004 persona/evidence divergence acceptance tests if dependency-safe.
5. Submit exact commits/tests/reports for lead review. Acceptance remains dependency-gated until V0.3 closes.

Do NOT execute SB-V04-005 here and do not make a second canary. Dedicated branch `claude/social-bots-v04-live-canary` exclusively owns the real subscription-authenticated canary.

## Reporting

Reports stay under `social-bots/worker-reports/windows-core/`.
Commit/push after each parent artifact and continue to the next dependency-ready item.

## Safety

No public effects, Anthropic API/PAYG or other new spend, destructive actions, secrets, fake evidence, or SwarmAI dependency.
