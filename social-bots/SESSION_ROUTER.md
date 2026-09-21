# Session router — LEAD-047

## Fable: primary integrator, RELEASED_AWAITING_WORKER_ACK

Branch: fable/social-bots-v23-fasttrack-20260921.
Assignment: social-bots/delivery/FINAL_RUN.md.
Scope: recovery repair, current shared runtime integration, existing S20–S23 completion, delivery closure and later V3.0 work in the declared priority order. The prior pause and new-files-only restriction are superseded. Preserve any current/just-pushed work. Check for overlapping uncommitted changes before shared-file edits.

## Cursor and legacy implementation lanes: PARKED_SAFE_HANDOFF

Do not start new overlapping source. Preserve and submit any existing local work so Fable can integrate it. Lead instructions do not establish that a worker consumed the handoff.

## Independent QA: REVIEW_ONLY

May independently run the pinned candidate and negative regressions without changing runtime source or invoking real models. Return actual commands/results/evidence. A separate actual reviewer context/worktree can provide engineering review; no worker or subagent promotes milestones.

## Heartbeat and live gates

Exactly one SESSION_ONCE start receipt per fresh top-level session. No periodic chat heartbeat. Task lease renewal and actual invocation completion receipts are separate.

No live product-model/public/spend grant is created. Operational gates remain in MILESTONE_MANIFEST.md, current owner approvals and delivery/OWNER_GATES.md. Canary evidence remains frozen. Social Bots stays independent of SwarmAI.
