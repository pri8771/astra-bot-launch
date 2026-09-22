# Reasoning proposal schema — V0.4+

Lead-owned contract for Core.

## Principle

Reasoning proposes. Deterministic policy validates, ranks/chooses as designed, and controls all effects.

A reasoning provider never grants authority.

## Proposal envelope

Required conceptual fields:

- schema_version
- proposal_id
- provider_id
- adaptive
- generated_at
- context_digest
- alternatives[]
- recommended_action
- uncertainties[]
- evidence_refs[]

## Alternative

Required:
- action
- rationale
- expected_value
- expected_learning
- relevance
- confidence
- risk
- cost
- reversibility
- duplication_risk
- evidence_refs[]
- payload_ref or bounded typed payload

All scoring inputs must be finite numeric values in [0,1].

Reject NaN, infinity, strings, out-of-range values, missing required values.

## Allowed V0.4 actions

Initial allowlist:
- NO_ACTION
- RESEARCH_MORE
- CREATE_CANDIDATE
- CONTINUE_EXPERIMENT
- CLOSE_EXPERIMENT

Actions may be extended only by a reviewed policy/schema artifact.

Explicitly forbidden as direct reasoning actions:
- PUBLISH
- SEND_MESSAGE
- SPEND
- PURCHASE
- DELETE
- CHANGE_CREDENTIAL
- BYPASS_REVIEW
- BYPASS_AUTHORITY

If a model returns an unknown/forbidden action, reject that alternative.

## Recommended action

- must equal one valid alternative action;
- is advisory only;
- deterministic policy may select a different valid alternative or block all alternatives.

## Payload boundary

Model output should reference durable IDs rather than embedding executable instructions.

CREATE_CANDIDATE payload may reference:
- signal_id
- proposed angle/brief
- target platform suggestion
- experiment intent

It may NOT contain:
- shell command;
- URL to invoke as an effect;
- credentials;
- publish_authorized=true;
- spend amount/authority;
- user-message target with send instruction.

## Evidence

Every non-NO_ACTION recommendation should cite evidence refs or explicitly state that more evidence is needed.

Provider may not fabricate an evidence ref that does not exist in the current context.

## Failure semantics

Any of:
- provider unavailable;
- timeout;
- auth/quota failure;
- parse failure;
- empty alternatives;
- all alternatives invalid;
- schema invalid;

=> no adaptive action is eligible.

Return/record:
BLOCKED_REASONING_UNAVAILABLE or BLOCKED_REASONING_INVALID

Changed evidence remains pending unless deterministic policy intentionally records a reviewed terminal decision.

## Baseline provider

A deterministic baseline may exist for:
- tests;
- diagnostics;
- comparison.

It must be explicitly labeled adaptive=false and must not satisfy V0.4 adaptive changed-evidence acceptance.

Production changed-evidence mode intended to satisfy V0.4 defaults to fail-closed when adaptive provider is unavailable.
