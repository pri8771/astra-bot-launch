# Canonical idea lineage schema

Supports V1.6/V2.7 cross-platform content intelligence.

## CanonicalIdea

- idea_id
- bot/persona
- thesis
- evidence_refs[]
- factual_claim_refs[]
- created_at
- originating_experiment
- novelty_key
- status

## PlatformExecution

- execution_id
- idea_id
- platform
- format
- transformation_version
- content_hash
- claim_lineage[]
- platform_constraints_applied[]
- experiment_id
- publication_id when authorized/published
- derived_from_execution_id when repurposed
- created_at

## Rules

- A transformation may change form, not factual support.
- Every factual claim preserves source lineage.
- Cross-platform outputs are separate executions, not copy/paste aliases.
- Dedup/novelty checks operate on both canonical idea and platform execution levels.
