# Autonomy contract

Autonomous thinking is the core product requirement.

## Independent state

Each runtime and persona has separate:
- goals;
- durable memory;
- observed facts with timestamps;
- hypotheses;
- experiment history;
- content history;
- platform state;
- pending actions;
- lease/heartbeat state;
- stop/recovery state.

Shared facts may be referenced through an explicit shared namespace; never silently merge personas.

## Decision record

Every non-trivial decision records:

- What changed?
- What is known vs inferred?
- What objective is currently most valuable?
- What candidate actions were considered?
- Why was the chosen action preferred?
- What authority does it require?
- What is the expected result?
- What would falsify the hypothesis?
- What is the next observation time/event?

## Action policy

Use deterministic code for predictable work and waiting. Invoke a model for interpretation, synthesis, creative generation, uncertain prioritization or review.

The bot may autonomously:
- research public information;
- analyze existing permitted analytics;
- create drafts/candidates;
- run local tests;
- register experiments;
- update its own non-secret state;
- prepare account/browser steps;
- choose among already-authorized local actions.

The bot must stop at the exact gate for:
- passwords/passkeys/MFA/CAPTCHA/consent;
- new spending or paid fallback;
- public posting/deployment not already explicitly authorized;
- customer/user messages not already explicitly authorized;
- purchases/refunds;
- destructive actions;
- unsupported platform automation;
- uncertain identity/account ownership.

## Learning

A bot does not "learn" because a model said it learned. Learning is a persisted hypothesis update tied to evidence.

Each experiment records baseline, hypothesis, intervention, observation window, success/stop criteria, result, confidence, decision and next experiment.

Negative and inconclusive results are valid.

## Heartbeat

Worker heartbeat fields:
- worker_id
- host_alias
- pid/session reference if safe
- lease_id
- started_at
- heartbeat_at
- current_task_id
- source_ref
- status
- last_receipt
- next_safe_action

Heartbeat proves liveness only when updated by the actual worker process. Scheduler configuration alone is not evidence.

## No-overlap

A task can have one active execution lease. Lease acquisition must be atomic. A second worker must exit or choose another eligible task. Stale leases require bounded expiry plus reconciliation of external effects before reassignment.
