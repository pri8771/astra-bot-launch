# V2 strategy and revision schema

Lead-owned contract connecting Intelligence evidence to Core strategy state.

## StrategyState

Fields:
- schema_version
- strategy_id
- version
- bot
- persona
- objective
- priority_audiences[]
- priority_topics[]
- platform_weights{}
- format_weights{}
- experiment_priorities[]
- active_hypotheses[]
- constraints[]
- evidence_refs[]
- created_at
- supersedes
- status

Weights are relative priorities, not spending authority.

## StrategyRevisionProposal

Fields:
- proposal_id
- bot
- persona
- current_strategy_id/version
- changes[]
- reason
- evidence_refs[]
- expected_effect
- expected_learning
- confidence
- uncertainty[]
- reversibility
- rollback_condition
- required_authority
- created_at

## Change operations

Initial typed operations:
- SET_PLATFORM_WEIGHT
- SET_FORMAT_WEIGHT
- ADD_TOPIC_PRIORITY
- REDUCE_TOPIC_PRIORITY
- ADD_EXPERIMENT_PRIORITY
- RETIRE_EXPERIMENT_PRIORITY
- UPDATE_AUDIENCE_FOCUS
- NO_CHANGE
- REQUEST_MORE_EVIDENCE

No arbitrary dictionary merge into strategy state.

Every operation has bounded parameters.

## Revision policy

Deterministic Core policy enforces:
- max change magnitude per revision;
- no negative weights;
- normalization rules;
- no new unavailable platform execution;
- no monetary spend;
- no public authority;
- evidence minimum/confidence threshold;
- rollback condition;
- separate bot/persona state.

## Anti-overreaction

A single anomalous observation must not create an unbounded strategy swing.

Policy should support:
- evidence count/quality floor;
- confidence floor;
- maximum delta per revision;
- contradictory evidence handling;
- cooldown or observation requirement where appropriate.

## No-data semantics

Missing evidence:
- does not become zero;
- cannot prove failure/success;
- yields NO_CHANGE or REQUEST_MORE_EVIDENCE.

## History

Every accepted revision:
- creates a new immutable strategy version;
- links previous version;
- records proposal/evidence/policy verdict;
- preserves rollback path.

## Cross-lane boundary

Intelligence produces:
- GrowthOpportunity
- AudienceHypothesis
- ExperimentRecord
- NormalizedMetricObservation

Core produces/owns:
- StrategyState
- StrategyRevisionProposal adoption/rejection
- revision history

Intelligence must not directly mutate StrategyState.
