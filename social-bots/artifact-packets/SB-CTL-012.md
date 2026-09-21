# Artifact packet — SB-CTL-012

Artifact: Artifact graph validator and readiness reporter
Milestone: engineering control
Lane: Mac QA / Integration Control
Story points: 3
Status: READY

## Goal

Make artifact-first project management mechanically auditable instead of relying on humans/agents to notice registry/manifest drift.

This artifact is intentionally independent of Core and Intelligence runtime implementation.

## Scope

Create a small local tool, preferably stdlib-only Python, that validates:

1. ARTIFACT_INDEX.json parses and every artifact id is unique.
2. Every status is in the allowed lifecycle vocabulary.
3. Every depends_on artifact id exists.
4. Dependency graph is acyclic.
5. Every canonical_ref under social-bots/ that is meant to be a repository file exists where validation can determine it.
6. Every artifact packet referenced under artifact-packets/ exists.
7. Milestone manifest artifact ids exist in ARTIFACT_INDEX.json.
8. ACCEPTED artifacts may have blocked/planned future dependents, but an artifact cannot be considered milestone-ready when required dependencies are not ACCEPTED.
9. Detect contradictory status combinations such as ACCEPTED with an explicit evidence note saying unresolved/changes-required when machine-readable evidence supports detecting this.
10. Detect duplicate ownership/collision warnings for active IN_PROGRESS artifacts that target the same explicitly declared owned paths when such metadata is present.
11. Produce a deterministic version/readiness report from MILESTONE_MANIFEST.md + artifact statuses.
12. Distinguish:
    - engineering readiness;
    - operational promotion;
    where the manifest defines them separately (especially V2.0 / SB-V20-099 vs SB-V20-004).

## Outputs

- validation exit code;
- human-readable report;
- optional machine-readable JSON report;
- current first incomplete artifact/milestone blockers;
- no mutation of canonical status.

Suggested paths:
- social-bots/bin/validate_artifacts.py
- social-bots/tests/test_artifact_graph.py
- social-bots/worker-reports/mac-qa/

## CI relation

This may be used by SB-CTL-006 CI.

The validator itself must:
- use no secrets;
- call no network;
- perform no GitHub mutation;
- perform no deployment/external effect.

## Acceptance

Create regressions for:
- duplicate id;
- missing dependency;
- cycle;
- bad status;
- manifest references missing artifact;
- valid graph;
- V2.0 engineering-ready vs operational-blocked distinction.

Expected return status: SUBMITTED.
