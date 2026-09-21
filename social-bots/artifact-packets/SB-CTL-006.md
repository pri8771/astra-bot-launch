# Artifact packet — SB-CTL-006

Artifact: Social Bots CI verification workflow
Milestone: engineering control
Lane: Core
Story points: 2
Priority: after current V0.3 correctness repairs, or earlier only if it does not delay them.

Goal: provide independent GitHub-hosted verification for Social Bots unit/regression tests and artifact metadata sanity.

Required:
- GitHub Actions workflow scoped to Social Bots changes;
- Python version matching supported runtime baseline;
- run from social-bots directory;
- execute complete unittest discovery;
- validate ARTIFACT_INDEX.json as JSON when present on branch;
- no secrets;
- no network/model/provider calls;
- no public/external effects;
- deterministic fixtures only.

Acceptance:
- workflow triggers on PR/push for Social Bots implementation branches;
- known passing branch reports success;
- deliberately failing test would fail the workflow (can be proven via workflow design/test, no need to commit a broken test to canonical);
- artifact JSON parse failure fails;
- workflow cannot accidentally publish/deploy/spend.

Return:
- workflow path;
- commit SHA;
- first CI run URL/status if available;
- exact test count;
- known platform differences.

Expected return status: SUBMITTED.
