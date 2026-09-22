# Owner decisions and goal post reset to V1.7 — Social Bots — 2026-09-22 (~18:45Z)

Recorded by Claude from the owner's direct messages in the current Claude session. **This records owner direction only. It is not a lead verdict, a release or a version acceptance.** The native ChatGPT Social Bots lead must reconcile `STATE.json`, `ARTIFACT_INDEX.json` and `SESSION_ROUTER.md`, and keeps acceptance authority.

## Owner messages (verbatim)

- **"1. yes, 2 yes."** (1: Swarm lint packet. 2: public-repo GitHub Actions is the intended CI route.)
- **"If we havent reached 1.7 for any, then change the goal post for 1.7"**

## Decisions

1. **Target: LIVE V1.7.** Bots has not reached V1.7, so V2.0, V2.3 and V2.7 are deferred.
   - Canonical `STATE.campaign.target/hard_stop` still says V1.3 (LEAD-062/063).
   - The native V1.7 contract (LEAD-048: `delivery/V17_LIVE.md`, `V17_SCOPE.json`, `V17_ACCEPTANCE.md`) names Fable as sole integrator. The owner's current working model is Codex-direct and Claude, with no automatic dispatch, so the lead must re-issue ownership.
2. **CI:** public-repo Actions is the owner-confirmed zero-cost route. There is no billing change.

## Where Bots is (native evidence, adversarially checked)

- **Official: V0.4.x.** V0.3 is ACCEPTED/CLOSED. Sources: `chatgpt/social-bots-plan-20260920@7451465:social-bots/STATE.json` (`version.current=V0.4.x`) and LEAD-065.
  - V0.4 is still blocked on SB-V04-002, SB-V04-004 and SB-EVD-002. SB-V04-005 is already accepted.
- **Engineering (non-sequential):**
  - SB-V13-002 is accepted (PR13, LEAD-060). PR14 composition is accepted (LEAD-061).
  - SB-V13-001 and SB-V14-001 were accepted on a *different* lineage (`feb30f4`, fixture-labelled). That lineage is not an ancestor of `fec9773`, and its runtime files differ.
  - The PR6–PR16 engineering repairs are accepted.
- **Canonical metadata lags:** STATE, ARTIFACT_INDEX and SESSION_ROUTER still point at LEAD-063 and the superseded `8c86898` pin.
- **Pending on the lead:** PR17 `da531597` suitability (LEAD-066). The only review of the capture commit is Codex's integrity recommendation. Both receipts have extraction `not_attempted`. The E1 June-4 recency needs a ruling. The PR17 head carries non-capture commits.
- **CI:** no workflow exists on the canonical, PR16 or PR17 lineages. `social-bots-ci.yml` exists only on `claude/social-bots-mac-qa-control`.

## V1.7 blockers

### Lead verdicts, releases and reconciliation

1. **GOV-1 / LANE-REASSIGN:** set the campaign target to LIVE V1.7. Reassign V1.7-scope card owners (Cursor, Claude-Core, Claude-Intelligence, Claude-Acceptance, Claude-Windows, Fable) to the active workers. Reconcile STATE, ARTIFACT_INDEX, SESSION_ROUTER and AGENT_MESSAGES for LEAD-064/065.
2. **LEAD-066:** PR17 E1/E2 suitability. Then V04-B, a prepare-only P0/P1/P2/P3/E0 matrix rebuild on a PR16 descendant with a pinned source, tree and matrix.
3. **Release the dependency-READY cards:**
   - SB-V07-001 prepare-only host package/runbook (LEAD-037 "may proceed").
   - SB-R07-042 divergence freeze and SB-R07-044 verifier.
   - SB-R07-071 heartbeat.
   - SB-V07-WIN-001.
   - SB-R07-051.
4. **Route decisions** SB-ACC-010..014: Buffer draft-only, three-channel bootstrap, Meta fallback, Reddit design, TikTok fallback.
5. **SB-V11-001** retry/backoff is held (3 attempts, 15m/60m).
6. **INTEGRATED-CANDIDATE:** compose one pinned V1.7 candidate from:
   - the fec9773 lineage;
   - the PR12/13 cherry-picks;
   - the feb30f4 SB-V13-001/V14-001 work, which needs a code-identity review;
   - the PR17 evidence.
7. **CI:** add a workflow to the canonical lineage, and name an **independent non-implementer reviewer**. The mac_qa lane is stale.

### Owner grants (aliases/paths only)

| Gate | Needed |
|---|---|
| G-MODEL-V04 | ≤5 subscription Claude Code calls bound to source/tree/matrix, 2h expiry, no retries, no API fallback. Only after LEAD-066 and V04-B |
| G-MODEL-RUNS | Separate per-artifact budgets for generation, review and unattended development. No PAYG |
| G-CULTURAL | A named reviewer alias or review method for attributable cultural review over exact final content |
| G-HOST | Persistent host/path, existing scheduler identity, sleep/reboot/auth facts. Registration needs a later exact grant |
| G-ACCOUNTS | Per-route X/Instagram/TikTok/Reddit/Facebook aliases and consent. The X official API is pay-per-use, which conflicts with G-SPEND, so the owner or lead must rule |
| G-PUBLISH + G-MEASURE | 3 individually scoped canaries (one per persona): content hash, persona, account, permalink readback, named windows |

### External and elapsed time (cannot be backfilled)

- G-LEAD-LOOP: a real worker → GitHub → ChatGPT → worker transport, 2 cycles.
- V0.7: 3 scheduler-fired receipts across ≥2 intervals (SB-R07-073/074).
- V1.0: a 24h three-bot window.
- V1.3–V1.5: real measurement windows.
- The bounded integrated V1.7 run.

### Engineering (only after release)

- V0.5: SB-V05-002 has no operational semantic assessor. Also SB-R07-052..055 and 061.
- V0.6: three real unpublished dry runs.
- SB-V15-001: cross-persona load aliases.
- SB-V16-001: source audit and fact-binding.
- SB-V17-001/002 and SB-S17-001..008.
- The S08–S16 slice cards, including the exactly-once public-effect wrapper and effect-idempotency reconciler (S09-002, S10-002).
- V1.7 privacy, abuse, spam and duplicate-response tests.
- The GATE-DOSSIER per owner gate.
- SCOPE-GUARD acceptance. The test exists at `fec9773:social-bots/tests/test_v17_scope_guard.py` but has never been separately lead-accepted.

**Honest outlook:** V1.7 is 13 minor versions and several elapsed windows away. The critical path is **LEAD-066 → V04-B → G-MODEL-V04 → V0.5/V0.6 → G-HOST/scheduler → G-ACCOUNTS → G-PUBLISH/MEASURE**.
