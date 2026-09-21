# V2.4–V3.0: detailed implementation and consumption contracts

Execute after genuinely working V2.3 unless the lead releases a small prerequisite early. Reuse existing SB-S24..SB-S30 cards; NR-23..NR-32 supply their missing production consumers. No broad rewrite, speculative cluster, extra platform or unlimited agent pool is required.

## V2.4 institutional memory

Input: accepted experiment lessons, strategy revisions, incidents and attributable source facts. Output: immutable MemoryItem {id, type, scope, statement, evidence_refs, confidence, confirmed_at, validity_interval, seasonal_context, contradiction_refs, supersedes, retention_class, status}. Reuse the existing organizational schema; extend with an explicit version only where required.

Interfaces: record_lesson(item, transaction), retrieve(context_scope, query, now, limit), mark_contradiction(left_ref, right_ref, evidence_ref), propose_retest(hypothesis_ref, changed_conditions). Proposed default decay is configurable half-life by item type; factual supersession differs from audience preference decay. Unknown confidence remains unknown. Retrieval returns explanations/evidence, not a new unsupported fact.

Consumer: the next production reasoning/planning context. Persist retrieval refs in the decision receipt so the effect can be audited. Negative tests: cross-brand read, stale dominant memory, contradictory confident records, seasonal lesson out of season, repeated failed hypothesis without new conditions, deletion/tombstone reappearing from an index. Real-history age is measured; a time-shift test is not a claim of months of operation.

## V2.5 aggregate audience segments

Input: compatible, sufficiently populated aggregate observations grouped by content/topic/format/time window. Do not collect an identity dossier or infer sensitive traits. Output: SegmentHypothesis {id, scope, feature_definition_version, observation_refs, sample_count, window, centroid_or_rules, confidence, status, supersedes}. Cohort minimum and reporting suppression thresholds are configurable policy frozen before live evaluation, not invented confidence percentages.

Interfaces: build_aggregate_features(observations, privacy_policy), propose_segments(features, minimum_support), compare_segment_versions(old, new), propose_segment_strategy(segment_ref, strategy_ref). Use interpretable small aggregates first; add clustering only if evidence justifies it. Missing denominator prevents rate calculation. Do not force two clusters onto sparse data.

Consumer: scoped strategy proposals and experiment design, not individual ad targeting. Tests: sparse/identical data -> insufficient evidence; sensitive feature rejected; metric-window mismatch; unstable split suppressed; contradictory evidence retires/merges a segment; strategy cannot access another persona's segment.

## V2.6 trend intelligence

Input: accepted current-source captures with event time, retrieval time, source identity and hashes. Output: Trend {id, scope, canonical_claim, source_refs, observed_series, velocity_estimate?, saturation_estimate?, relevance, uncertainty, expires_at}. Unknown event time/coverage prevents confident velocity claims.

Interfaces: normalize_trends(captures), estimate_change(time_series, coverage), evaluate_fit(trend, persona, audience_context), propose_timing_experiment(trend_ref, budget). Distinguish multiple reposts of one source from independent corroboration. No mention-volume shortcut to truth.

Consumer: a dependency-ready prospective experiment or NO_ACTION in the same task queue. Tests: duplicate syndication, future timestamp, historical item republished now, irrelevant virality, unverifiable claim, expiry, missed snapshots. Live proof includes actual current evidence and actual queue selection.

## V2.7 cross-platform execution

Input: CanonicalIdea with supported claims and accepted target-route capabilities. Output: PlatformExecution {idea_id, scope, platform, format, source_claim_refs, content_hash, review_refs, sequence_constraints, experiment_ref, publication_ref?}.

Interfaces: plan_variants(idea, available_routes), validate_lineage(variant, idea), plan_sequence(variants, observations, budget), register_execution(variant, transaction). Transform form, not factual support. Actual image/video requirements need an allowed media renderer and asset-policy/rights check; a text brief alone is not proof an uploadable video exists.

Consumer: the existing scheduler and effect wrapper, with per-platform readback and analytics. Do not add LinkedIn or another platform merely because a prose example mentioned it. Tests: changed unsupported fact, duplicate payload, incompatible media/length, invalid destination, sequencing starvation, cross-platform metric conflation. Describe cannibalization only at the strength supported by measurements.

## V2.8 allocation

Input: opportunities, real capacity, quotas, budgets, reliability work and existing commitments. Output: AllocationDecision {policy_version, scope, candidates, selected, reservations, estimated_value, uncertainty, reason, expires_at}. Model value estimates remain estimates.

Interfaces: rank(opportunities, evidence), allocate(ranked, budget, reserves), reserve_allocation(decision, ledger), release_unused(reservation, terminal_evidence). The scheduler must consume the reservations. Shared ceilings cover parent plus specialists; account rate limits cannot be evaded by switching identities/providers.

Consumer: actual claimed work and deferred tasks. Tests: exhausted pool, concurrent allocation race, infeasible all-zero budget, revoked account, reliability reserve, exploration starvation, double reservation after restart, invalid/non-finite score. Real allocation proof traces a changed budget to changed actual execution, not merely a sorted list.

## V2.9 self-evaluation

Input: decision/quality/experiment/incident/availability evidence. Output: ImprovementProposal {finding_id, evidence_refs, bounded_change, affected_artifacts, expected_outcome, risk, tests, rollback, review_required}. Detection windows and thresholds are versioned.

Interfaces: detect_drift(strategy, executed_work), audit_experiments(records), detect_repetition(content_lineage), evaluate_slo(receipts), propose_repair(findings). Prevent recursive self-audit loops with per-window dedup and a fixed proposal cap. Inadequate telemetry means UNKNOWN, not healthy.

Consumer: the same lead-reviewed work queue; no direct code edits/deployment from a detector. Tests: known defect found, normal variance not overclaimed, duplicate proposals coalesced, private evidence not leaked, user text cannot inject a tool action, detector cannot self-approve repair. Validate with real telemetry and separately labeled seeded failures.

## V3.0 brand isolation and migration

Brand is a durable scope with an explicit mapping to existing bot/persona IDs and verified public routes. Do not assume two personas with the same string across brands are the same identity. Plan keys become unambiguous tuples/references; storage readers use an approved Scope object rather than free-form paths.

Interfaces: register_brand(contract), resolve_scope(brand, bot, persona), migrate_legacy_namespace(mapping, backup, transaction), verify_scope_access(requester, reference). Migration is additive/idempotent, tested on a copy, preserves input/output hashes and has rollback. No brand-private state becomes shared by default. Test collision, missing mapping, partial migration, repeated migration, interrupted restore and stale worker generation.

## V3.0 shared knowledge

Sharing is explicit allowlisting of public facts or approved generalized lessons, with evidence, publisher scope, audience scope, policy and revocation. Shared facts are not shared account identity, raw community data or confidential strategy.

Interfaces: propose_share(memory_ref, policy), publish_shared_fact(approved_ref, transaction), resolve_shared(ref, consumer_scope), revoke_shared(ref). Revocation must invalidate retrieval caches and derived permission, while retaining lawful audit history without retaining unnecessary personal content. Test secret-containing ref, private hypothesis, unauthorized consumer, revoked cache entry and altered source hash.

## V3.0 portfolio operation

Portfolio planning reuses the V2.2 planner, V2.8 allocator and V2.3 specialist runner. It does not build a second orchestration framework. A portfolio goal decomposes into brand-scoped tasks; every task carries explicit authority/budget/context. Specialists can serve different brands only via separate scoped invocations. No shared mutable conversation memory.

Consumer: persistent scheduler, result adoption and organizational memory. NR-31 must trace portfolio goal -> allocation -> actual brand task -> specialist -> result -> next portfolio decision. NR-32 combines two persistent brands, multiple personas, a permitted shared fact, a rejected private access, a recovery event and a bounded self-improvement proposal on a pinned candidate.

## Operational support required throughout

Provide a local read-only status/evidence command showing exact version, candidate ref, active grants, due/blocked tasks, last real invocation, review queue and missing acceptance predicates. Do not build a cosmetic fake dashboard. Retain zero-spend behavior, explicit provider unavailability, one start heartbeat per session, bounded queues and evidence retention. Keep the existing single-host architecture unless measured constraints justify a reviewed change.
