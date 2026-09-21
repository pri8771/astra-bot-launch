# Social Bots cross-lane interface contract

Lead-owned contract. Claude Core and Claude Intelligence should implement behind these interfaces instead of editing each other's modules.

## 1. EvidenceRef

Purpose: stable reference from any derived judgment back to captured evidence.

Required fields:
- evidence_id
- source_id or URL
- captured_at
- content_hash
- provenance
- collector_version
- status

Rules:
- status distinguishes success / partial / failed.
- fixtures are explicitly provenance=fixture.
- failed evidence cannot support a factual claim.

## 2. CaptureReceipt

Produced by Intelligence source collector.

Fields:
- receipt_id
- evidence_ref
- retrieval_status
- http_or_provider_status
- mime/content type when known
- extracted_text_or_summary
- extraction_version
- tags
- safe error detail when failed

Core may consume the resulting Signal, but must not mutate the receipt.

## 3. ClaimSupportResult

Produced by Intelligence factual-review layer.

Fields:
- candidate_id
- claim_id
- claim_text
- classification: SUPPORTED | PARTIAL | UNSUPPORTED | CONFLICTED | UNKNOWN
- evidence_refs[]
- reviewer_version
- reviewed_at
- notes

Policy:
- required material claim in UNSUPPORTED/CONFLICTED/UNKNOWN => candidate withheld unless product policy explicitly allows uncertainty-labeled publication later.

## 4. NormalizedMetricObservation

Produced by Intelligence analytics layer.

Required:
- observation_id
- bot
- persona
- account_alias
- platform
- content_id
- experiment_id
- publication_id
- observed_at
- window_start/window_end
- raw_metrics: list of {name,value,unit,source}
- normalized_metrics: map where every value includes semantic category, value, derivation/version and whether cumulative/delta/rate
- missing_metrics[]
- provenance/evidence refs

Critical semantics:
- missing != zero.
- cumulative snapshot != event delta.
- never sum cumulative snapshots as if they were independent events.
- cross-platform normalization must preserve raw metric names and meaning.

## 5. AudienceHypothesis

Produced/updated by Intelligence audience memory.

Fields:
- hypothesis_id
- bot/persona scope
- statement
- context/segment description
- confidence
- support_refs[]
- contradiction_refs[]
- freshness
- decay policy/version
- last_updated
- status

No sensitive-person profiling.

## 6. ExperimentRecord

Produced by Intelligence experiment engine.

Fields:
- experiment_id
- bot/persona
- hypothesis_ref
- baseline
- intervention
- primary_metric
- secondary_metrics
- observation_window
- stop/safety criteria
- status
- result
- evidence_refs[]
- decision/learning refs

Rules:
- missing outcome data => INCONCLUSIVE.
- never infer success from a queued/unpublished candidate.

## 7. GrowthOpportunity

Produced by Intelligence V2 evaluator.

Fields:
- opportunity_id
- bot/persona
- opportunity_type
- target platform/format/experiment where relevant
- expected_growth_value
- expected_learning_value
- confidence
- uncertainty[]
- required_authority
- evidence_refs[]
- operational_availability
- cost_class

No artifact grants spend or public authority.

## 8. StrategyRevisionProposal

Produced/owned by Core V2 strategy engine.

Fields:
- proposal_id
- bot/persona
- current_strategy_version
- proposed_changes[]
- reason
- evidence_refs[]
- expected_effect
- uncertainty
- reversibility
- rollback_condition
- required_authority
- created_at

Core deterministic policy validates proposal before strategy state changes.

## 9. Boundary rules

Intelligence owns evidence interpretation / metrics / audience / experiments / content/community/growth opportunities.
Core owns runtime safety / authority / reasoning orchestration / durable strategy / worker lifecycle.

Integration must occur through typed records above, not direct cross-lane mutation of private stores.

Shared records should be append-only or versioned where practical.

## 10. Versioning

Each record type carries schema_version.
Breaking changes require a migration/read-compatibility decision before merge.
