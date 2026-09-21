# Work queue

Artifact-first, pull-driven coordination is active.

Canonical lead review: `lead-reviews/LEAD-018_2026-09-20T2202.md`.

Workers should pull their own branch and read `social-bots/SESSION_INSTRUCTIONS.md`. See `SESSION_ROUTER.md` and `WORKER_HEARTBEAT_PROTOCOL.md`.

## Session A — Windows Core / Host

Branch: `claude/social-bots-windows-core-host`

Verified head: `5318065aad6e38de1e3313ad984d09451a2dfcb7`

Accepted:
- SB-V03-004.

Next:
1. narrow SB-V03-005 migration/read-boundary cleanup;
2. SB-V03-006 fresh V0.3 bundle;
3. V04 production fail-closed + real adaptive provider;
4. Windows/WSL host proof + V0.7 liveness.

Do not implement CI; Mac QA owns SB-CTL-006 unless reassigned.

## Session B — Intelligence / Evidence

Branch: `claude/social-bots-intelligence-repair-v2`

Verified head: `cbd781cab4d751b2a0626c3ce060c5a217d771e9`

Next:
1. close SB-V05-001 static trust / operational evidence / DNS-connect boundary;
2. harden SB-V05-002 trust; keep heuristic assessor/extractor diagnostic/test-only; fail closed operationally until accepted semantic provider integration;
3. proceed V13 metric semantics;
4. V14 persona audience memory;
5. V15 evidence-linked experiments;
6. V16 content evidence/persona history;
7. V17 community evidence/persona memory;
8. V20-002 typed accepted-evidence growth inputs.

## Session C — Mac QA / Integration Control

Branch: `claude/social-bots-mac-qa-control`

Next:
1. SB-CTL-012 artifact graph validator/readiness reporter;
2. SB-CTL-006 GitHub CI/control;
3. V2 engineering-acceptance harness preparation.

No runtime source edits.

## Current version

V0.3.x.

V0.3 now primarily waits on final SB-V03-005 cleanup and regenerated SB-V03-006.

## Concurrency

Run 3 Claude sessions maximum for this phase.

Do not start a fourth until lead accepts the state/evidence contracts and integration becomes the bottleneck.

## Authority

No public posting/replies/messages, purchases, paid APIs/additional spend, destructive actions, credentials/secrets, fake operational evidence, engagement manipulation or SwarmAI dependency.
