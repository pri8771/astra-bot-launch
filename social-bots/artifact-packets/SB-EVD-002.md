# Artifact packet — SB-EVD-002

Artifact: Independent V0.4 real-canary acceptance
Milestone: V0.4
Owner: ChatGPT lead
Story points: n/a

Depends on:
- SB-V04-001
- SB-V04-002
- SB-V04-003
- SB-V04-004
- SB-V04-005

## Acceptance

ChatGPT independently audits SB-V04-005 source/code/evidence.

Must verify:
- source was live/non-fixture;
- model provider invocation was actual Claude Code subscription path;
- no injected runner/model output;
- no API PAYG path;
- persisted proposal/decision matches evidence;
- schema/policy gates were applied;
- no public effect;
- artifact evidence is internally consistent.

Only after SB-EVD-002 is ACCEPTED may the project claim **V0.4 complete**.
