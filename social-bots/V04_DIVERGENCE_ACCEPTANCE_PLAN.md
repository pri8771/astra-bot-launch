# V0.4 adaptive divergence acceptance plan

Lead decision: **prepare now; execute no additional adaptive/model calls unless the owner later grants a new explicit bounded authorization.**

## Why this exists

SB-V04-002 and SB-V04-004 require causal evidence that the real adaptive reasoning provider changes its proposal/ranking when:

1. persona/workspace changes while evidence, objective and state are held constant; and
2. evidence changes while persona, objective and state are held constant.

Core has repaired the single-variable experimental design and built a receipt-replay seam. Those are valid engineering/test assets, but synthetic receipts and replayed output cannot prove how a live adaptive model would respond to counterfactual inputs.

The accepted first SB-V04-005 canary proves one genuine adaptive invocation. One output cannot prove causal divergence. The later second live call exceeded the owner's one-call authorization and is permanently excluded from acceptance evidence.

Therefore there is **no legitimate zero-live-call path to final SB-V04-002/SB-V04-004 acceptance from the evidence currently available.** The correct state is authorization-blocked, not accepted and not “fixed” by relabeling replay evidence.

## Current disposition

- SB-V04-001: ACCEPTED.
- SB-V04-003: ACCEPTED.
- SB-V04-005: ACCEPTED from the first chronological authorized call only.
- SB-V04-002: BLOCKED on fresh owner authorization for empirical divergence execution.
- SB-V04-004: BLOCKED on the same empirical execution.
- SB-EVD-002: WITHHELD until SB-V04-002 and SB-V04-004 are accepted.
- No additional Claude CLI/adaptive provider/model call is authorized.

## Conservative future acceptance matrix

If the owner later explicitly authorizes a bounded divergence batch, use **one fixed five-call matrix** and do not retry until it passes.

All five calls must use:
- the existing subscription-authenticated Claude Code provider;
- `ANTHROPIC_API_KEY` absent;
- no injected runner;
- no effect tools;
- no public post/message/purchase/destructive action;
- the same provider version/model configuration within the batch;
- one run ID and one immutable evidence/context manifest.

### Persona-only matrix

Capture one real current evidence snapshot E1 through the accepted current-source collector and freeze its bytes/hash/receipt for the batch.

Hold objective, evidence E1, pending count, duplication state, prior hypotheses, policy posture and allowed actions constant.

Run:
- P0: social-a + E1
- P1: social-b + E1
- P2: social-c + E1
- P3: one cultural/Primandir workspace + E1

Required comparisons:
- P0 vs P1
- P0 vs P2
- P0 vs P3

Each comparison must differ only in persona/workspace and must show material proposal/ranking divergence under the existing acceptance metric.

### Evidence-only matrix

Capture a second materially different real current evidence snapshot E2.

Run:
- E0: social-a + E2

Compare P0 vs E0. Persona, objective, state, policy posture and provider configuration must remain identical; only evidence changes.

This produces five total live adaptive invocations in the clean conservative batch.

## Why the accepted first canary is not used as P0

The first canary is valid SB-V04-005 evidence, but its committed acceptance bundle does not cryptographically bind a complete pre-invocation bounded CONTEXT/prompt artifact suitable for a controlled counterfactual matrix. Some context can be reconstructed, but causal acceptance should not depend on reconstruction or inference.

If a later independent audit proves that the exact canary input is fully and unambiguously reconstructable from committed evidence, the lead may reduce a future owner authorization request. Until then, the acceptance plan uses five fresh controlled calls.

The unauthorized second call is never eligible to reduce the batch.

## Prepare-only work authorized now

Core may implement and test, **without invoking any adaptive/model provider**:

1. a prepare-only divergence matrix builder that emits the five bounded context envelopes;
2. context JSON + SHA-256 and exact prompt SHA-256 for every planned case;
3. automatic single-variable isolation checks;
4. receipt-schema validation and proposal-difference reporting;
5. a hard fail-closed live-execution gate that requires a lead-created, scope-specific authorization manifest that does not currently exist;
6. a call-budget counter that stops before call N+1;
7. no-retry semantics: malformed/unavailable/non-divergent outcomes are recorded truthfully rather than rerun until success.

Tests must use fixtures and clearly label them engineering-only.

## Authorization control

No live divergence execution may occur merely because code supports it.

A future live batch requires:
- a new explicit owner authorization in conversation;
- a corresponding lead-created canonical authorization manifest naming the artifact/run scope and exact maximum call count;
- one designated execution lane;
- all other lanes remaining live-model-disabled.

Until that exists, live execution must fail closed before spawning Claude.

## Parallel project work while V0.4 is blocked

V0.4 remains the official product phase, but dependency-safe engineering may continue.

- Core: finish the no-call prepare-only matrix support, then work on SB-V07-001 authorized-host worker packaging/OS scheduling because its accepted dependency SB-V03-006 is already closed.
- Intelligence: finish the narrow SB-V15-001 structural admin-boundary repair already assigned, then stop for lead audit.
- Acceptance/QA: independently review new submissions and help harden heartbeat/host acceptance tooling; no runtime source ownership and no model calls.
- Canary lane: frozen evidence preservation only.

No downstream work may be used to misstate V0.4 as complete.
