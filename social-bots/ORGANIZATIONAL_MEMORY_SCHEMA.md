# Organizational memory schema

Target contract for V2.4 and V3.0.

## MemoryItem

- memory_id
- scope: persona | bot | brand | shared_public | portfolio
- type: fact | hypothesis | strategy_lesson | experiment_lesson | incident | platform_change | source_trust | runbook_lesson
- statement
- evidence_refs[]
- confidence
- created_at
- last_confirmed_at
- decay_policy
- seasonal_context
- contradiction_refs[]
- supersedes[]
- access_policy
- status: ACTIVE | STALE | CONTRADICTED | SUPERSEDED | ARCHIVED

## Sharing boundary

Shared_public may contain reusable public facts/platform knowledge/generalized lessons only.

It must not contain:
- credentials/account secrets;
- private persona identity state;
- confidential brand strategy;
- raw community personal data;
- unsupported assumptions copied from another brand.

History is append/version oriented. Contradictions do not erase the earlier record.
