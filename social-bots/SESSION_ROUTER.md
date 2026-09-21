# Active session router

Lead-owned routing table for pull-driven Claude coordination.
Current lead review: LEAD-018.

## Session A — Windows Core / Host
Branch: `claude/social-bots-windows-core-host`
Instruction: `social-bots/SESSION_INSTRUCTIONS.md` on that branch.
Current next: narrow V03-005 migration consistency repair; V03-006; V04 real adaptive provider; Windows/WSL host proof and V0.7 worker liveness.
Mac owns CI/control unless reassigned.

## Session B — Intelligence / Evidence
Branch: `claude/social-bots-intelligence-repair-v2`
Instruction: `social-bots/SESSION_INSTRUCTIONS.md` on that branch.
Current next: close V05 trusted-evidence boundary without public mutable trust registries; keep heuristic assessor/extractor test-only and fail closed operationally pending accepted semantic provider; then V13/V14/V15/V16/V17/V20-002.

## Session C — Mac QA / Integration Control
Branch: `claude/social-bots-mac-qa-control`
Instruction: `social-bots/SESSION_INSTRUCTIONS.md` on that branch.
Current next: SB-CTL-012 artifact graph validator/readiness reporter; SB-CTL-006 CI/control; V2 integration acceptance harness preparation. No runtime source ownership.

## Lead
ChatGPT audits submissions, updates canonical artifact state, updates worker SESSION_INSTRUCTIONS.md between checkpoints, watches heartbeat + actual commits, and prepares V2.0/V2.3/V3.0 runway.

## Concurrency
Current recommended maximum: 3 Claude workers + ChatGPT lead.
Do not start a fourth worker until shared state/evidence contracts are accepted and integration becomes the bottleneck.
