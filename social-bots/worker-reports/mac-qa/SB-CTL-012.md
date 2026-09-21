# Worker report — SB-CTL-012 (Mac QA / Integration Control lane)

- **Artifact ID:** SB-CTL-012 — Artifact Graph Validator & Readiness Reporter
- **Lane:** Mac QA / Integration Control (`claude/social-bots-mac-qa-control`)
- **Requested status:** SUBMITTED (not self-accepted; lead owns acceptance)
- **Story points:** 3
- **Branch base:** started from the existing remote lane branch (lead-seeded from
  `chatgpt/social-bots-plan-20260920`) and merged latest canonical
  `origin/chatgpt/social-bots-plan-20260920` (no rebase, no force). Work done in a
  **separate git worktree** so no active working tree is shared with another lane.
- **Ownership:** QA/control only. NO runtime module was edited.

## Deliverable

- `social-bots/bin/validate_artifacts.py` — stdlib-only validator + readiness
  reporter. No network, no secrets, no GitHub mutation, no deployment, no model
  call, and it NEVER mutates canonical artifact status. CLI: `--repo-root`,
  `--json`; exit 0 iff no hard errors.
- `social-bots/tests/test_artifact_graph.py` — 18 regressions (all pass).
- `social-bots/worker-reports/mac-qa/readiness_report.json` — machine-readable
  readiness snapshot of the current canonical registry.

## Checks implemented (SB-CTL-012 scope 1–12)

Structural (hard ERRORS → non-zero exit / CI fail):
- ARTIFACT_INDEX.json parses; `artifacts` present;
- artifact ids unique;
- statuses in the index's own `status_values` vocabulary;
- every `depends_on` target exists;
- dependency graph acyclic (deterministic DFS; reports the cycle path);
- referenced artifact **packets** (`canonical_ref` under `artifact-packets/`) exist.

Drift (WARNINGS → reported, do not fail CI):
- `MILESTONE_MANIFEST.md` ids not yet in the index (expected forward roadmap);
- missing non-packet `canonical_ref` files under `social-bots/`;
- contradictory ACCEPTED states — ACCEPTED depending on a non-ACCEPTED artifact,
  or ACCEPTED with an evidence note signalling unresolved/changes-required.

Readiness (deterministic, by version):
- per-version engineering vs operational required lists, ready booleans, blockers;
- milestone prerequisites ("accepted Vx.y") gate OPERATIONAL promotion;
- **V2.0 ENGINEERING READINESS (SB-V20-099) is kept strictly distinct from V2.0
  OPERATIONAL PROMOTION (SB-V20-001..004); the two are never collapsed.**

### Severity rationale (design decision, flagged for lead)

Only structural graph breakage hard-fails. Manifest-roadmap drift and transient
lead-owned status inconsistencies are WARNINGS, so CI does not go permanently red
on an intentionally in-progress registry while still surfacing every issue. If the
lead prefers manifest-ref or contradiction checks to be blocking, that is a
one-line severity flip — happy to change it on direction.

## Findings on the CURRENT canonical registry (informational, not fixed by me)

Validator result: **PASS (0 errors, 32 warnings)**. Notable warnings for lead
reconciliation (I do not own or mutate these):
- Contradictory state: `SB-V03-002` and `SB-V03-003` are ACCEPTED but depend on
  `SB-V03-001`, currently `CHANGES_REQUIRED`.
- Manifest references ~28 roadmap ids not yet in ARTIFACT_INDEX.json (V0.5–V1.0
  future artifacts, e.g. SB-V04-005, SB-EVD-002, SB-V06-*, SB-ACC-*, SB-V10-*).
- `SB-V03-001` `canonical_ref` `social-bots/runtime/` is a directory that does not
  exist on the canonical branch (runtime source lives on the Core lane branch).

## Test commands & results

```
cd social-bots
python3 -m unittest tests.test_artifact_graph      # 18 passed
python3 bin/validate_artifacts.py                  # human report, exit 0
python3 bin/validate_artifacts.py --json           # machine report
```

Required regressions present: duplicate id, invalid status, missing dependency,
dependency cycle (incl. self-cycle), manifest references unknown artifact, valid
graph, missing packet reference, and **V2.0 engineering-ready while operational
blocked** (plus prereq-milestone gating and contradiction detection). A meta-test
asserts the validator stays PASS on the real registry so a future change cannot
silently make CI hard-fail on intentional drift.

## Known limits

- File-existence checks only cover repo-relative refs under `social-bots/`;
  cross-branch refs (e.g. runtime source on the Core lane) are reported as
  warnings, not resolved across branches.
- Contradiction detection is intentionally conservative (specific evidence-note
  markers) to avoid false positives.

## Requested status

**SUBMITTED** — for lead (ChatGPT) review.
