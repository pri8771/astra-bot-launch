# Codex: one coordination session, three independent projects

This is the owner-requested cross-project handoff stored in `pri8771/astra-bot-launch`, canonical branch `chatgpt/social-bots-plan-20260920`. It is a notes/routing layer, NOT a shared product runtime, authority service or replacement artifact registry.

## Objective

Coordinate Bots, Jobs and SwarmAI from one Codex session. Each currently targets **LIVE V1.7 and stop**. Read each repository's current scoped contract before acting. Same version number does not mean the same deliverable or permissions. No V1.8+ implementation or future roadmap expansion.

## Minimal startup

1. Read root AGENTS.md, this file and PROJECTS.json. The registry contains pinned observations, not necessarily the latest heads.
2. Discover the actual three local checkouts or use authorized GitHub reads. Verify repository identity and current coordination/source refs. Do not overwrite a dirty worktree, assume sibling directories exist, or merge coordination snapshots into application source.
3. Read each project's own AGENTS/startup/current scope and current worker/checkpoint/heartbeat. Read the relevant one of `projects/SOCIAL_BOTS.md`, `projects/JOBS.md`, `projects/SWARMAI.md` only when working that project.
4. Read OPERATING_CONTRACT.md and HEARTBEATS_AND_HANDOFFS.md once. Preserve current implementation ownership and exact real-action gates. This assignment does not stop or take over Fable automatically.
5. Produce one compact three-project status/next-action table grounded in fresh source. Mark unavailable repos/access as unavailable, not empty or complete. Check submissions before assigning more work.
6. Execute the smallest released nonconflicting action: review/test, unblock, update a precise handoff, or implement after an actual safe ownership handoff. Continue across projects when one is externally blocked. Do not create another broad plan.

## On-demand routes

- Owner intent and superseded decisions: OWNER_DECISIONS.md.
- Detailed Social Bots notes, historical findings and current live gates: projects/SOCIAL_BOTS.md.
- Jobs' real application/ingestion gates and candidate-truth rules: projects/JOBS.md.
- Swarm's actual local application/checkpoint path: projects/SWARMAI.md.
- Cross-repo Git safety, authority and work selection: OPERATING_CONTRACT.md.
- Heartbeat differences and handoff: HEARTBEATS_AND_HANDOFFS.md.
- Compact durable context: SESSION_RECORD.md.
- Reusable kickoff: PROMPT.md.

This pass only stored notes and verified source scope/routes. It did not rerun runtime suites, accept milestones, start workers/watchers, install scheduling, grant account/model/public actions or edit the Jobs/Swarm repositories. Source references live in PROJECTS.json. Preserve this distinction when reporting progress.

Codex reads AGENTS.md as project instructions; the detailed notes stay on demand. Do not assume starting in this repository automatically loads sibling repositories' rules. Read them explicitly and do not replace global user instructions. Official instruction-discovery reference: https://developers.openai.com/codex/guides/agents-md/ .
