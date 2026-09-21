# Social Bots recovery execution — current code to V0.7 with LIVE checkpoints

Lead audit date: 2026-09-21.
Primary recovery implementation branch: `cursor/social-bots-recovery-v07-20260921`.
Recovery branch base: `claude/quirky-shannon-t1377u@918c42e2a4602589997a7c625d994e049f266d6d`.

## Audit verdict

We are **not V0.7**. We are behind the owner's target because operational/live checkpoint evidence is incomplete.

### What is real now

- V0.3 is accepted.
- V0.4 has one accepted real adaptive canary.
- Current recovery source at 918c42e has materially improved V0.4 authorization hardening and V0.7 worker-once/scheduler engineering.
- Worker-reported full suite at 918c42e: 306 passed, 1 skipped.
- A real POSIX SIGKILL/restart proof exists, but it was a direct CLI engineering demonstration on a temporary Linux/CCR environment.
- One real SESSION_ONCE heartbeat exists for the fresh Claude session.

### Why this is not V0.7

1. V0.4 is not complete: genuine controlled persona/evidence adaptive divergence has not run. It remains owner-authorization-blocked.
2. V0.5 is not complete: operational factual support, platform/cultural gates and a real acceptance bundle remain open.
3. V0.6 has no accepted three-bot real-current-evidence dry-run set.
4. V0.7 has scheduler assets, but no accepted proof of repeated native OS-scheduler firings on an owner-controlled persistent host.
5. V0.7 has no accepted two-cycle ChatGPT-direction -> later scheduled worker consumption proof.
6. Current SESSION_ONCE duplicate protection is not atomic: `find_session()` performs a read across ledgers and `_append_jsonl()` appends later. Two concurrent processes with the same session_id can race between check and append. Existing sequential duplicate tests do not prove cross-process uniqueness.

## Recovery principles

- One active implementation lane: Cursor recovery branch.
- Small artifacts. Prefer SP1/SP2 only.
- One artifact per commit where practical.
- Engineering proof and LIVE proof are separate artifacts.
- A version checkpoint is not complete until the exact live evidence required by its contract exists.
- Never retry a live/model/public action until it passes.
- Do not self-accept milestones.
- If one artifact hits an owner gate, immediately continue any dependency-safe artifact.
- No public posting is needed through V0.7.

## Execution order

### Wave 0 — make the current code trustworthy
1. SB-R07-071 atomic session heartbeat.
2. SB-R07-041 audit/harden every live-provider entrypoint.
3. SB-R07-044 independent divergence verifier.
4. SB-R07-072 persistent-host preflight.

### Wave 1 — finish all no-gate preparation
5. SB-R07-042 freeze controlled V0.4 inputs.
6. SB-R07-051 operational fact-review integration.
7. SB-R07-052 platform-native formatting gate.
8. SB-R07-053 cultural-review binding.
9. SB-R07-061 reusable V0.6 runner.
10. SB-R07-073 native scheduler install if the current Cursor host passes SB-R07-072.

### Wave 2 — collect V0.7 host LIVE evidence in parallel with owner-blocked model work
11. SB-R07-074 three real scheduler firings.
12. SB-R07-075 live no-overlap.
13. SB-R07-076 live crash/restart.
14. SB-R07-077 canonical direction consumption.

These can be completed without public posting or a live adaptive model call.

### Owner gate — V0.4
SB-R07-043 remains BLOCKED until:
- owner explicitly authorizes the fixed five-call adaptive divergence batch; AND
- ChatGPT lead creates the matching canonical authorization manifest.

No worker may infer authorization from the existence of the runner or from this recovery plan.

### Wave 3 — sequential milestone LIVE evidence
15. SB-R07-043 live V0.4 divergence batch.
16. SB-R07-045 lead V0.4 closeout.
17. SB-R07-054 live V0.5 evidence run.
18. SB-R07-055 V0.5 validator.
19. SB-R07-062/063/064 three live zero-public V0.6 dry runs.
20. SB-R07-065 independent candidate review.
21. SB-R07-066 lead V0.6 closeout.

### Wave 4 — prove autonomous development loop
22. SB-R07-078 lead-worker cycle A.
23. ChatGPT publishes new bounded direction.
24. SB-R07-079 later OS-scheduled worker consumes it without owner relay.
25. SB-R07-07A final lead audit and V0.7 promotion only if all parent milestone gates are accepted.

## LIVE checkpoint definitions

- **V0.4 LIVE:** real current E1/E2 + five genuine subscription-provider calls + ledger-bound output + causal divergence.
- **V0.5 LIVE:** real current source capture through operational factual/platform/cultural review; no fixture trust.
- **V0.6 LIVE:** each general bot completes full real-current-evidence/adaptive dry run with zero public effect.
- **V0.7 LIVE:** native OS scheduler on an owner-controlled persistent host actually fires sessions over time; receipts prove heartbeats, one-task claims, crash/no-overlap and later canonical-direction consumption.

Direct CLI invocations, scheduler template tests, replay receipts and fixtures never substitute for these LIVE checkpoints.

## Parent artifact mapping

- SB-R07-041/042/043/044/045 close the remaining evidence for SB-V04-002, SB-V04-004 and SB-EVD-002.
- SB-R07-051..055 close SB-V05-002..005.
- SB-R07-061..066 close SB-V06-001..005.
- SB-R07-071..079 plus final lead bundle close SB-V07-001..005.

## Stop conditions

Stop only for:
- missing explicit live-model authorization/manifest;
- account/login/MFA/CAPTCHA/consent;
- required admin escalation or a host that is not owner-controlled/persistent;
- new spend/PAYG;
- public effect authority;
- destructive external action.

Everything else should be implemented, tested, committed and pushed without asking the owner to relay another prompt.
