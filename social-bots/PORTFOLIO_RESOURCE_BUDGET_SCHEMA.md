# Portfolio resource budget schema

Supports V1.9, V2.8 and V3.0 resource allocation.

## ResourceBudget

- budget_id
- scope: run | bot | brand | portfolio
- period
- compute_time_limit
- model_call_limits by provider/class
- storage_limit
- platform_rate_limit_reservations
- worker_concurrency_limit
- public_effect_limit
- spend_limit_usd
- exploration_reserve
- reliability_reserve
- created_at
- evidence_refs[]

## AllocationDecision

- decision_id
- budget_id
- candidate_work[]
- selected_work[]
- expected_growth_value
- expected_learning_value
- opportunity_cost
- risk
- rationale
- evidence_refs[]
- policy_version

No allocation grants public/spend authority. When a budget is exhausted, work is deferred/blocked rather than silently switching providers or spending.
