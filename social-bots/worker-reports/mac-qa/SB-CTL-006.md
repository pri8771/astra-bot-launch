# Worker report — SB-CTL-006 (Mac QA / Integration Control lane)

- **Artifact ID:** SB-CTL-006 — Social Bots CI verification workflow
- **Lane:** Mac QA / Integration Control (`claude/social-bots-mac-qa-control`)
- **Requested status:** SUBMITTED (not self-accepted)
- **Story points:** 2
- **Workflow path:** `.github/workflows/social-bots-ci.yml`

## Ownership check (per instruction, before implementing)

Confirmed the Windows Core lane did NOT implement CI: `origin/claude/social-bots-windows-core-host`
contains only the SB-CTL-006 **packet** (`social-bots/artifact-packets/SB-CTL-006.md`),
no `.github/workflows/` and no SB-CTL-006 worker report. The Windows lane's own
messages explicitly dropped CI, and `SESSION_ROUTER.md` assigns CI/control to Mac.
No duplication.

## What the workflow does (packet requirements)

- Triggers on `push` and `pull_request` for Social Bots branches
  (`chatgpt/social-bots-**`, `claude/social-bots-**`, `dev`, `main`), scoped to
  changes under `social-bots/**` (and the workflow file).
- Python **3.11** (runtime baseline).
- Step 1: parse `social-bots/ARTIFACT_INDEX.json` as JSON (fails CI on parse error).
- Step 2: run `social-bots/bin/validate_artifacts.py` (the SB-CTL-012 validator;
  structural graph errors fail CI).
- Step 3: `python3 -m unittest discover -s tests -v` from `social-bots/`
  (present-branch test suite; failures fail CI).
- Each step is guarded with a `-f`/`-d` existence check so it runs on any branch
  regardless of which files that branch carries (validator/tests live on some
  branches, the index on all).

## Safety (packet: no secrets / network / model / deploy / public effect)

- `permissions: contents: read` — the job token is read-only; it cannot push,
  release, or deploy.
- No `${{ secrets.* }}` reference anywhere.
- No provider/model/network calls: the steps only parse JSON and run stdlib
  unit tests. `SBOTS_REASONING=baseline` + `SBOTS_REASONING_REQUIRE_ADAPTIVE=0`
  are exported so no test could accidentally take an adaptive/paid route.
- `actions/setup-python` fetches a Python build (standard CI infrastructure);
  the tests/validator themselves make no network calls.
- `concurrency` cancels superseded runs on the same ref.

## Acceptance evidence (proven locally; no broken file committed to canonical)

- Known passing branch → success: on this branch the three steps run green —
  index parses, validator exits 0, `unittest discover` = **18 tests OK**.
- Artifact JSON parse failure fails: `python3 -c "json.load(open(bad))"` exits 1.
- Deliberately failing test fails the workflow: a synthetic failing test makes
  `unittest discover` exit 1.
- Cannot publish/deploy/spend: read-only token, no secrets, no deploy steps.

## Return fields

- Workflow path: `.github/workflows/social-bots-ci.yml`
- Commit SHA: recorded in the submission commit (see git log / AGENT_MESSAGES).
- First CI run URL/status: to be confirmed from the repo Actions tab after push
  (recorded in the follow-up note if GitHub Actions is enabled for the repo).
- Exact test count on this branch: 18 (artifact-graph validator regressions).
  Implementation branches run their own runtime suites via the same discovery.
- Known platform differences: runner is `ubuntu-latest` (Linux). The Windows-lane
  recurring/host proofs are separate artifacts; CI here is platform-neutral
  (stdlib only) and does not attempt Windows/WSL-specific execution.

## Requested status

**SUBMITTED**.
