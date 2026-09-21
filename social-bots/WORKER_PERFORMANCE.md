# Claude worker performance

Purpose: measure Claude Code's implementation reliability by story-pointed artifact packet and task type. Story points are complexity/uncertainty, not time.

No task is counted as accepted until ChatGPT lead verifies the stated acceptance evidence.

## Summary

First artifact-oriented sample now exists across SP2-SP5 work.

Early signal only — not statistically meaningful yet:
- SP3 signal/state repair (`SB-V03-002`) reached lead acceptance on its first submitted checkpoint.
- SP2 review-gate implementation is directionally correct but missed two packet-required regressions, so it is partial rather than accepted.
- SP5 lease/fencing work substantially improved concurrent acquisition but missed active-cycle fence loss after TTL expiry; this is exactly the kind of cross-cutting failure that justifies decomposition/adversarial acceptance for SP5.
- SP4 runtime serialization is directionally correct but remains coupled to the SP5 fencing artifact and contains a documentation/implementation mismatch on persona-private namespaces.

No GitHub CI run exists for implementation head `2cab7219`; test counts below are worker-local unless explicitly marked as independently inspected source/tests.

## Task results

| Task | Artifact | SP | Type | First attempt | Independent evidence | Review findings | Repair cycles | Accepted | Notes |
|---|---|---:|---|---|---|---|---:|---|---|
| SB-R0A1 | SB-V03-002 | 3 | signal/state correctness | PASS | lead inspected source + later/batch/restart regressions at `2cab7219` | 0 blocking | 0 | yes | per-signal consumed ledger accepted; no CI run |
| SB-R0A2 | SB-V03-003 | 2 | gating/regression | PARTIAL | lead inspected deterministic stop gate + current review tests | 1 acceptance gap | 0 | no | missing packet-required forced fact-review and voice-review failure regressions |
| SB-R0B1 | SB-V03-004 | 5 | concurrency/fencing | PARTIAL | lead inspected `flock` acquisition CAS + adversarial takeover tests | 1 blocking lead defect | 1 worker-internal repair before submission | no | lease may expire during active cycle; old owner can still commit after takeover; native-Windows/cross-host strong fence unproven |
| SB-R0B2 | SB-V03-005 | 4 | state/lease architecture | PARTIAL | lead inspected runtime task key + concurrent persona tests | 2 blocking dependencies/mismatches | 0 | no | serialization depends on SB-V03-004; architecture claims persona-private namespaces but storage is bot-scoped |
| SB-R0B3 | SB-V03-006 | 3 | adversarial integration test | BLOCKED | packet groomed by lead | dependencies not accepted | 0 | no | run only after V03-003/004/005 are accepted and evidence is regenerated |

## Review findings by artifact

### SB-V03-003
Current implementation uses one deterministic `review_passed` gate, so the code path should stop fact/voice/cultural failures. The submitted regression suite does not yet prove the required fact and voice failure cases. This is a bounded test/evidence repair, not a reason to redesign the gate.

### SB-V03-004
The simultaneous takeover race is fixed on one POSIX host by the `flock` critical section. The remaining defect is lifecycle fencing: `run_one_unit()` renews before `decision.run_cycle()`, but no fence is validated while/after the cycle before mutations are committed. A work unit exceeding TTL can therefore be taken over while the old owner still completes writes. The repair should add an actual active-cycle fence/renewal mechanism plus a forced-expiry adversarial test; increasing TTL alone is not acceptance.

### SB-V03-005
Runtime-level serialization is the right shared-state boundary if shared `bot_state.json` remains. However the design still needs valid lifecycle fencing from V03-004. Separately, documentation says persona experiment/content/memory namespaces are isolated while current path/storage APIs are bot-scoped. Claude must either implement true persona-private non-shared namespaces or change the contract and prove logical isolation/filtering everywhere.

## Metrics to accumulate

For each SP level:
- attempts;
- first-pass accepted;
- first-pass partial;
- first-pass failed;
- average repair cycles (descriptive only, not time);
- escaped defects discovered later;
- task-definition ambiguity incidents;
- access/evidence blockers.

Do not infer worker quality from one task. Track patterns over multiple comparable tasks.
