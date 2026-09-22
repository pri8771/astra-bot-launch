# Mac local inference choice and offline preflight — 2026-09-22

Status: owner route choice recorded; engineering recommendation only. No version acceptance or exact live manifest activated.

## Owner choice

Owner: “if thats all that means for bots, lets use my local machine first. (my mac), easiest to test on”.

This selects the owner's Mac for the first bounded reasoning experiment: P0/P1/P2/P3 over E1 and E0 over E2. It generates proposals, with no posts or scheduler. Do not treat this as permission for remote fallback, model downloads, recurring inference, or broader unattended work. The reviewed source/model/config/matrix and exact consumption allowance must be concrete before execution.

Read-only host inventory at approximately 19:00Z: Apple M5 Pro, 48 GiB unified memory; existing Ollama at loopback `127.0.0.1:11434`; `/api/tags` lists six installed models, `/api/ps` is empty. No inference or model load occurred. Installed candidates include:

- `qwen3.5:9b`, digest `6488c96fa5faab64bb65cbd30d4289e20e6130ef535a93ef9a49f42eda893ea7`;
- `qwen3.5:4b`, digest `2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd`;
- `gemma3:4b`, digest `a2af6cc3eb7fa8be8504abaf9b04e88f17a119ec3f04a3addf55f92841195f5a`.

Availability and inventory are not a product-path inference receipt. The Mac choice does not establish the later persistent-host/scheduler gate.

## Actual source gap

Accepted source `fec97738ec0e9407415f60228f7c3938613396c3`, tree `43e80b92d8ae559db55a41ed33329695e6fd03fc`, has no supported Ollama/LM Studio/OpenAI-compatible execution path. `runtime/authorization.py` accepts only `provider_mode=claude-cli`; `runtime/divergence_prepare.py` binds Claude subscription configuration, rejects injected provider factories and constructs `ClaudeCodeReasoningProvider`.

Requested lead release: one real loopback local-provider adapter using the existing durable dispatch/budget path, exact model/endpoint/config/prompt binding, no remote fallback, and the same experiment limits. A test seam or EngineeringStub must never be used to label real inference as offline. PR17 evidence suitability and matrix preparation remain separate prerequisites.

## Confirmed fail-fast defect

The proposed owner request requires stopping at the first provider/schema/authorization failure; the dormant manifest specifies `activation.fail_fast=true`. They are proposed contracts, not live grants.

A temporary offline harness against clean exact `fec9773` exercised real source identity, matrix binding, authorization, deep dispatch and durable CallBudget. Only the provider constructor was replaced by an in-process sentinel, following existing execution-binding tests. For each P0 outcome `provider_unavailable`, `provider_exception`, and `invalid_proposal`, all five cases ran and consumed five slots. Valid identical proposals also ran all five, correctly: lack of divergence is an experiment result, not provider failure.

Root cause: `_execute_one_case` returns a recorded failure, while `execute_batch` unconditionally advances. Recommended smallest repair: retain the failed result/consumed slot, stop before the next reservation, and expose unattempted cases. Verify these three failure outcomes and a valid nondivergent control. No tracked source edits or external calls were made by the reproducer.

Local evidence:

- `/tmp/bots-v04-failfast-audit-20260922.py`, SHA256 `85c768215d34c1a6e38e2ab84b6dbefc670539fa22d69e20d0be270791aaa1b4`;
- `/tmp/bots-v04-failfast-audit-20260922.json`, SHA256 `deeecbb068dd66878d9b1e436abe5c03d86cb7a04ad4c97dfdf43d7604f3a23a`.

## Blocker-list corrections

- Correct pending PR17: https://github.com/pri8771/astra-bot-launch/pull/17 at `da53159704e3e1dfefb8d7e4d2518fdc889317fb`; PR16 is already accepted by LEAD065. No LEAD066 found at canonical `7451465` during this audit.
- Do not cherry-pick PR12/13 again: accepted composition `8c86898` is an ancestor of `fec9773`. The account route and metrics blobs match the accepted changes. Although `feb30f4` is not an ancestor, its audience runtime/test blobs are identical at `fec9773`; ancestry alone does not establish missing implementation.
- CI exists on the QA branch but not these candidate lineages. Latest QA run `35678750483` failed before any steps with an account billing/spending-limit annotation despite the repository being public. Public visibility alone does not prove CI can execute.
- `SB-V07-001` is a bounded prepare-only candidate for reassignment; blanket READY-card execution would ignore specific holds and already submitted work. No scheduler registration is authorized.
- Cross-persona `load`/`load_all` compatibility aliases remain a concrete later source issue; do not infer they were fixed from unrelated audience ancestry.

Formal acceptance remains with the native lead; official state remains V0.4.x. Retry, scheduler, platform/public effects and later live gates remain held.

## Subsequent lead disposition

LEAD066 at `977e167` / canonical metadata `9b7e10c` accepts PR17 capture integrity, requires replacement of stale E1 and deterministic extraction lineage for both sources before another suitability review, and releases LOCAL adapter engineering on exact fec9773. Fail-fast reproduction only is released; the concrete reproduction above is returned for the separate minimal-fix release. Evidence copies are in `evidence/codex-failfast-20260922/`. The final matrix and real inference remain held.
