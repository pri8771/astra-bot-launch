# Worker report — SB-V03-005 production persona read boundary (LEAD-021 fast-track P2)

- **Artifact ID:** SB-V03-005 (Priority-2 read boundary slice)
- **Lane:** Windows Core (`claude/social-bots-windows-core-host`), fast-track LEAD-021
- **Requested status:** SUBMITTED (not self-accepted)
- **Ownership:** edited only `runtime/isolation.py` (Core-owned) + new tests. No
  Intelligence-owned module touched (collector/factcheck/metrics/audience/
  experiment_engine/content_intelligence/community/growth_evaluator untouched).

## Priority 1 (SB-V03-004 migration fencing) — re-affirmed, already on branch

LEAD-021 lists P1 first, but it was already implemented and the lead acknowledged
it (commit `175f741`): `PersonaState.load` is side-effect free, legacy migration
is staged in memory and persisted (persona file + runtime marker) ONLY inside the
ownership-fenced `_commit`; a stale owner that loses the fence writes nothing;
migration is crash-safe/idempotent (persona-file-existence gate). Regressions:
`tests/test_fencing.py::test_stale_owner_in_migration_path_leaves_no_write` and
`::test_decision_log_and_last_decision_written_inside_fence`,
`tests/test_isolation.py::test_run_cycle_commits_runtime_with_final_migration_marker`
and `::test_migration_recovers_when_marker_set_but_persona_file_missing`. No
rework needed — re-affirming rather than redoing.

## Priority 2 (persona-scoped production read boundary) — this submission

The six persona-scoped readers already existed in `runtime/isolation.py`
(`persona_content_history`, `persona_publish_queue`, `persona_experiments`,
`persona_analytics`, `persona_action_history`, `persona_decisions`) with per-store
no-bleed regressions in `test_isolation.py` (+ the Intelligence-contributed
`test_isolation_decisions.py`). The remaining gap the lead named — "raw
whole-runtime reads may remain only as explicitly named admin/internal APIs" — is
now closed:

- **Authoritative registry:** `PERSONA_SCOPED_READERS` maps every store in
  `PERSONA_SCOPED_STORES` to its persona reader; `persona_records(bot, persona,
  store)` is the sanctioned dispatcher for production persona-facing reads.
- **Admin/internal raw reads renamed & fenced off in naming:** the old private
  `_READERS` is now `_ADMIN_READERS`, exposed only through the explicitly named
  `admin_all_records(bot, store)`, documented as audit/admin/diagnostics only and
  "not a persona-facing production read". `audit()` uses it. There is no unnamed
  public whole-runtime reader.
- **Docstring** updated to state the boundary: production persona reads MUST go
  through `persona_*` / `persona_records`; raw enumeration is admin-only.

## New regression (`tests/test_persona_read_boundary.py`, 4 tests)

- every `PERSONA_SCOPED_STORES` entry has an authoritative persona reader AND an
  admin reader;
- `persona_records` dispatch equals the corresponding named reader;
- unknown store rejected by both `persona_records` and `admin_all_records`;
- for a real mixed general+cultural runtime (multiple `decision.run_cycle`s),
  across ALL six stores at once: each persona view is strict (no foreign records)
  and the two persona views partition the admin whole-runtime read (nothing lost
  or double-counted); `audit()` reports clean.

## Test commands & results

```
cd social-bots && python3 -m unittest discover -s tests
```

- **122 passed** (was 118; +4 read-boundary tests). `isolation.py` is the only
  runtime source changed; behavior of the existing readers is unchanged (the
  refactor is additive + a private-name change).

## Known limits

- Logical (not physical) isolation is unchanged: records live in the runtime's
  shared append-only stores, partitioned by the mandatory `persona` field +
  persona-derived collision-free ids. The boundary guarantees production reads go
  through strict persona filters; it does not physically nest per-persona files.

## Requested status

**SUBMITTED** — SB-V03-005 Priority-2 read boundary; SB-V03-004 re-affirmed.
Next fast-track step: SB-V03-006 acceptance-bundle regeneration (once V03-005 is
accepted), then V04-001/003 reconciliation.
