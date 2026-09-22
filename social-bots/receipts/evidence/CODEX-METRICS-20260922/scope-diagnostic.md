# Bots V1.3 bounded diagnostic — 2026-09-22

## Exact sources

- Canonical coordination: `origin/chatgpt/social-bots-plan-20260920` at `0e390f147ed86d8c09aa34269ffc0d9be1f9a601`.
- Fetched worker branch: `origin/fable/social-bots-v23-fasttrack-20260921` at `e9678f8bead4f872c199bdf09dbf709a8f649159`.
- Locally reviewed candidate source: `/Users/pchordia/Downloads/swarm_codex/review/bots-integrity-source/social-bots` at `9d497b4567e022a8e7f93a3ee890af206272b5be`.
- Native contracts: `social-bots/RECOVERY_TO_V07.md`, `social-bots/V07_TO_V17_EXECUTION.md`, `social-bots/MILESTONE_MANIFEST.md`, `social-bots/delivery/V17_ACCEPTANCE.md`, and `social-bots/artifact-packets/v07-v17/SB-S08-001.md` through `SB-S13-003.md` at canonical SHA above.
- The owner's V1.3 target supersedes the prior V1.7 ceiling as session authority, but this fetched canonical still says V1.7 and has not yet recorded that scope update.

## Native dependency chain and current evidence state

- V0.7 must close through `SB-R07-07A`: persistent owner-controlled host, native scheduler invocations, no-overlap/crash/restart/stale takeover, canonical-direction consumption, and two genuine lead/later-worker cycles. Host and scheduler evidence remain absent; no permission to create it here.
- V0.8 requires `SB-S08-001..005`: credentials-free account registry, read-only route probes, persona/destination lock, analytics route verification, lead evidence index. `runtime/account_routes.py` exists, but all five slices remain `PLANNED`; genuine account readback is still required.
- V0.9 requires `SB-S09-001..006`: authorization compilation, exactly-once effect wrapper, one authorized public canary per persona, then real-window analytics/learning. Public canaries remain blocked on explicit grants; no public action is authorized.
- V1.0 requires `SB-S10-001..005`: three-bot scheduled harness, reconciliation/idempotency, owner-gate evidence, measurement-to-next-decision chains, and no-SwarmAI-dependency proof. Worker infrastructure exists (`runtime/worker.py`, `bin/worker_once.py`), but parent artifacts remain planned and require genuine scheduled operation.
- V1.1 requires `SB-S11-001..004`: fault matrix, restart/idempotency, outage degradation, unattended bounded live run. No dedicated runtime/test files matching fault/reliability were found; slices remain planned.
- V1.2 requires `SB-S12-001..004`: capability registry, platform scorer, explicit no-platform result, choice-divergence acceptance. `runtime/platform_selection.py` and `tests/test_platform_selection.py` exist, but slices/parent acceptance remain planned and route evidence cannot be inferred from code.
- V1.3 requires accepted `SB-V13-001` plus `SB-S13-001..003`: metric semantic registry, real adapter conformance, incompatible-comparison guard. `runtime/metrics.py` and 21 passing fixture tests implement normalized kinds, missing/not-supported distinction, provenance fields, snapshot/delta rules and aggregation. `SB-V13-001` is accepted engineering; `SB-V13-002` and all S13 slices remain planned. No real adapter evidence is present.

## One reproducible defect: invalid numeric metric values are accepted

At `runtime/metrics.py` in `normalize`, the predicate `isinstance(raw_value, (int, float))` accepts Python booleans and non-finite floats. It converts `True` to `1.0`, and preserves `NaN`/`Infinity` as `PRESENT`. `aggregate_semantic` repeats the same broad numeric predicate, allowing non-finite results into accepted aggregates. This violates the V1.3 semantic/provenance boundary because these values are neither valid observed counts nor honest missing values, and can poison comparisons.

Observed at exact source `9d497b4` with temporary `SBOTS_HOME` only:

```text
True present 1.0 cumulative_snapshot
nan present nan cumulative_snapshot
inf present inf cumulative_snapshot
aggregate value: inf
```

The existing `python3 -m unittest -v tests.test_metrics` passes 21/21, demonstrating missing negative coverage rather than a pre-existing failing suite.

## Smallest diagnostic/reproduction plan

1. Add no production changes initially. Write one temporary regression that calls `metrics.normalize(platform="x", raw_metrics={"impressions": value}, ...)` for `True`, `NaN`, `Infinity`, and `-Infinity`.
2. Assert each becomes `MISSING` (preserving raw payload and raw name) or is rejected fail-closed with one consistently documented contract; assert no invalid value reaches `aggregate_semantic`.
3. Confirm the regression fails at `9d497b4`; run the existing 21 metric tests to preserve legitimate zero and finite-number behavior.
4. Root-cause boundary is input normalization plus defensive aggregation. Any later repair should use explicit `not isinstance(value, bool)` and `math.isfinite(float(value))`, with the same guard on persisted/legacy observations read by aggregation.
5. Keep validation synthetic and local. This needs no model, account, public effect, scheduler, host, or reviewer grant.

No source, coordination, scheduler, model, account, or public state was changed.
