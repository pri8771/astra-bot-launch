# Assignment — Fable 5.1

Role: senior planning architect + non-conflicting implementation worker.

## Priority

1. **Get V2.3 genuinely working as fast as honestly possible.**
2. Harden the plan through V3.0 so a Sonnet 4.6-class worker could execute artifacts without inventing major architecture.
3. After V2.3 is accepted, continue automatically toward V3.0 when dependencies/authority allow it.

V3.0 planning must inform earlier architecture, but **V2.4–V3.0 implementation must not delay V2.3**.

## First pass

- Check useful past project conversation/memory if available.
- Audit Claude history/heartbeat and latest ChatGPT reviews only as needed to avoid rebuilding rejected work.
- Audit the active Cursor recovery branch to avoid source collisions.
- Verify current status against Git before any claim.
- Emit one Fable `SESSION_ONCE` heartbeat.

## Planning job

Audit existing artifact contracts rather than replacing the roadmap.

Make ambiguous critical-path artifacts detailed enough that a Sonnet 4.6-class worker can implement them with:
- inputs/outputs and interfaces;
- reuse targets / likely modules;
- dependency and ownership boundaries;
- deterministic vs model responsibility;
- fail-closed/error behavior;
- focused/adversarial tests;
- ENGINEERING vs LIVE evidence;
- owner gates;
- concise definition of done.

Do not reread or rewrite already-sufficient packets.

## Execution job

Cursor currently owns V0.7 recovery implementation. Do not duplicate active Cursor artifacts.

While Cursor owns recovery:
- focus Fable on plan hardening, dependency analysis, acceptance/test architecture and genuinely independent future scaffolding;
- only implement source when canonical ownership permits and it does not overlap active Cursor work.

Fast-track engineering toward V2.3 may run ahead of operational version promotion when dependencies allow, but no later engineering may be used to falsely promote an earlier LIVE gate.

## Token/model efficiency

- Prefer git diff/search and targeted symbol/file reads.
- Maintain a compact working summary; do not repeatedly summarize the roadmap.
- Keep reports concise.
- If subagents/models are available, use the lowest capable model for bounded mechanical work (tests from fixed specs, search, lint/type fixes, fixtures, mechanical schemas, docs).
- Reserve Fable 5.1 for architecture, dependency reasoning, concurrency, authority/security, cross-module integration and hard debugging.
- Do not create excessive subagents or merge-conflict fanout.

## Hard gates

No unauthorized live model calls, public effects, new spend/PAYG, credential exposure, destructive actions, MFA/CAPTCHA bypass, fabricated LIVE evidence, or SwarmAI dependency.

## Handoff

Persist planning changes in Git. At the end return only:
- exact SHA(s);
- audited current state;
- critical path to V2.3;
- planning files/artifacts changed;
- first 5 executable non-conflicting tasks;
- blockers/owner gates;
- `READY_FOR_LEAD_REVIEW`.
