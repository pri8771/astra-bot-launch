# Worker report — SB-V04-002 / SB-V04-004 prepare-only work (Core lane)

- **Artifacts:** SB-V04-002, SB-V04-004
- **Requested status:** `SUBMITTED` for the prepare-only work below.
  **SB-V04-002 and SB-V04-004 themselves remain `BLOCKED_OWNER_AUTHORIZATION`
  and nothing here changes that.** Not self-accepted.
- **Lane:** Core (`windows-core`)
- **Session branch:** `claude/quirky-shannon-t1377u`, branched from
  `claude/social-bots-windows-core-host` @ `c6b67ff`
- **Source SHA:** `c2fe1f8e22767dadaf657223f3420b28d6c1f33d`
- **Canonical coordination SHA read:** `671abbc`
  (`chatgpt/social-bots-plan-20260920`), lead review **LEAD-038**
- **Contract followed:** `social-bots/CLAUDE_EXECUTION_TO_V07.md` Phase A and
  `social-bots/V04_DIVERGENCE_ACCEPTANCE_PLAN.md` "Prepare-only work authorized now"

## The headline, stated plainly

**No adaptive/model provider was constructed or invoked in this session.**
Current canonical GitHub state contains neither a fresh explicit owner
authorization nor a lead-created canonical authorization manifest, so the gate
below denies live execution. That denial is the expected, correct outcome, and
it is what the committed evidence records.

Empirical SB-V04-002 / SB-V04-004 acceptance still requires the five real
adaptive invocations in the plan's matrix. This work makes those five
invocations executable, budgeted and auditable the moment they are authorized.
It does not make them happen and does not substitute for them.

## Plan items delivered

The ten prepare-only items in `V04_DIVERGENCE_ACCEPTANCE_PLAN.md` and
`CLAUDE_EXECUTION_TO_V07.md` Phase A:

| # | Item | Where |
|---|---|---|
| 1 | five-case matrix (P0/P1/P2/P3/E0) | `runtime/divergence_prepare.py::build_matrix` |
| 2 | immutable bounded context JSON per case | `write_prepared` refuses overwrite; `PREPARED_MATRIX.json` |
| 3 | SHA-256 for evidence bytes, evidence receipt, bounded context, exact prompt | `PreparedCase` digests; `prompts/PROMPT_DIGESTS.json` |
| 4 | automatic single-variable isolation | `isolation_report` / `verify_isolation` (two layers, below) |
| 5 | proposal/receipt validation + material-divergence reporting | `divergence_report` |
| 6 | hard lead-created authorization-manifest requirement | `runtime/authorization.py::authorize` |
| 7 | exact call budget + atomic pre-spawn accounting | `runtime/authorization.py::CallBudget` |
| 8 | no-retry semantics | slots are never reused; outcomes are write-once |
| 9 | fail closed before spawning Claude | `execute_batch` gates before constructing a provider |
| 10 | fixtures labeled engineering-only | `provenance_label`; `acceptance_eligible` is false for fixtures |

## The matrix

Exactly the plan's cases, with objective, pending count, duplication state,
prior hypotheses and policy posture held constant across all five:

| case | persona | evidence | role |
|---|---|---|---|
| P0 | social-a | E1 | persona baseline |
| P1 | social-b | E1 | persona-only variant |
| P2 | social-c | E1 | persona-only variant |
| P3 | cultural-primandir-atman | E1 | persona-only variant (cultural) |
| E0 | social-a | E2 | evidence-only variant |

Required comparisons: `P0|P1`, `P0|P2`, `P0|P3` (persona) and `P0|E0` (evidence).

Committed digests (`evidence/SB-V04-002-prepare/PREPARE_STATUS.json`, truncated here):

| case | context_sha256 | prompt_sha256 | evidence_bytes_sha256 |
|---|---|---|---|
| P0 | `6398886b19fc7acb…` | `798bc69917687ccf…` | `ecb20894f18ca71b…` |
| P1 | `295f7c25385cea5a…` | `c990a6f0ac8873c8…` | `ecb20894f18ca71b…` |
| P2 | `5d04d0efdf592041…` | `939a3acb8eec392d…` | `ecb20894f18ca71b…` |
| P3 | `34d2ed346b2980ff…` | `6f0936318c482d3d…` | `ecb20894f18ca71b…` |
| E0 | `6697b546c432bc69…` | `337966a952ee3482…` | `2f9d45e54c7f0f6c…` |

P0–P3 share E1's evidence digest exactly, as a persona-only comparison requires;
only E0 differs.

## Isolation is checked on two layers, because one was not enough

A defect found and fixed during this work, worth the lead's attention:

`reasoning_receipt.bounded_context` — the projection the acceptance metric and
receipt matching use — **omits the signal `summary`**. The exact production
prompt does not. So two cases could share an identical `context_sha256` while
sending materially different evidence text to the model, and a "persona-only"
comparison could have silently varied the evidence too.

`isolation_report` therefore asserts both:

1. **digest layer** — exactly the expected variable differs in the bounded
   context projection (`differing_variables`);
2. **prompt layer** — exactly the corresponding key differs in
   `reasoning_cli.prompt_context(ctx)`, the exact bounded facts embedded in the
   production prompt.

Both must hold, and all five contexts must be distinct. `build_matrix` refuses
to return a non-isolated matrix at all. `tests/test_v04_divergence_prepare.py`
contains a regression that demonstrates the digest layer is blind to a
summary-only change and that the prompt layer catches it.

`reasoning_cli.py` gained one public function, `prompt_context()`. No behaviour
in the existing provider changed.

## The authorization gate

`runtime/authorization.py` requires a canonical manifest under
`social-bots/authorizations/` naming the artifact, lane, run scope and exact
maximum call count. Validation is strict:

- every required field must be present — a missing safety posture is invalid,
  never defaulted permissive;
- `retry_allowed`, `public_effect_allowed`, `spend_authorized`,
  `api_key_allowed` and `injected_runner_allowed` must each be exactly `False`;
- `provider_mode` must be `claude-cli` (existing subscription route only);
- `max_calls` is clamped to a hard ceiling of **5**;
- an expired manifest is not an authorization.

Two things no manifest can waive, re-checked at call time: a present
`ANTHROPIC_API_KEY`, and an injected runner. A real authorized batch must use
the real provider on the subscription route.

**Honesty boundary on authorship.** This code cannot cryptographically prove a
manifest was written by the lead rather than by a worker. It records the
manifest's file digest, `created_by` and `owner_authorization_ref` into the
grant and every receipt, and exposes `authorship_attested_by_code: false`.
Authorship is a git-provenance fact for an independent audit, not something the
gate asserts.

Current state, committed at `evidence/SB-V04-002-prepare/GATE_OUTPUT.json`:

```
"manifests_present": []
"live_execution_permitted": false
reason: no canonical authorization manifest in .../social-bots/authorizations.
        A live adaptive batch requires BOTH a fresh explicit owner authorization
        AND a lead-created canonical manifest ... Failing closed before spawning.
```

## Call budget, and why no-retry is structural

`CallBudget` reserves each slot by creating `slot-NNNN.json` with
`O_CREAT | O_EXCL` **before** a provider is constructed or a subprocess spawned.

- Exclusive creation is the atomic primitive, so two concurrent workers cannot
  take the same slot.
- A worker that dies after reserving leaves the slot consumed. Over-counting a
  crashed call is safe; under-counting could exceed the owner's exact
  authorization. `audit()` reports such slots as `reserved_not_recorded` rather
  than reclaiming them.
- Outcomes are write-once. An `provider_unavailable`, `invalid_proposal` or
  `provider_exception` result consumes its slot permanently and is recorded
  verbatim. There is no except-and-retry branch anywhere in the execution path.

Committed budget state for this run scope: `consumed: 0`, `remaining: 5`,
`retry_permitted: false`.

## Evidence

`social-bots/worker-reports/windows-core/evidence/SB-V04-002-prepare/`

- `PREPARED_MATRIX.json` — the five cases, contexts, digests, isolation report
- `prompts/P0..P3,E0.prompt.txt` + `PROMPT_DIGESTS.json` — the exact prompts
- `PREPARE_STATUS.json` — isolation, digests, gate state, budget state
- `GATE_OUTPUT.json` — the gate denying live execution right now
- `VERIFY_OUTPUT.json` — independent re-derivation of every digest
- `PREPARE_STDOUT.txt`, `FOCUSED_TESTS.txt`, `FULL_SUITE.txt`

## Exact commands and results

```
$ python3 bin/prepare_divergence_matrix.py prepare \
    --out-dir worker-reports/windows-core/evidence/SB-V04-002-prepare \
    --run-scope v04-divergence-prepare --lane windows-core --home /tmp/.../budget-home
  planned_call_count: 5   all_isolated: true
  live_execution_permitted: false   live_execution_performed: false
  acceptance_eligible: false

$ python3 bin/prepare_divergence_matrix.py verify \
    --matrix .../PREPARED_MATRIX.json --prompts-dir .../prompts
  digests_verified: true   prompt_bytes_verified: true   verified: true   (exit 0)

$ python3 bin/prepare_divergence_matrix.py gate --lane windows-core \
    --run-scope v04-divergence-prepare
  live_execution_permitted: false   manifests_present: []   (exit 0)

$ python3 -m unittest tests.test_v04_authorization_gate tests.test_v04_divergence_prepare -v
  Ran 53 tests ... OK

$ python3 -m unittest discover -s tests
  Ran 269 tests in 3.392s
  OK (skipped=1)
```

The one skip is the pre-existing real-canary intake skip, unchanged. The suite
was 160 passed / 1 skipped before this session.

## Known limitations — read these before accepting anything

1. **This is not empirical divergence evidence.** No model was called. The
   prepared matrix proves design and controls, not causation.
2. **The committed snapshots are engineering fixtures**, labeled
   `engineering-fixture`, which forces `acceptance_eligible: false` on the
   artifact. A real batch must supply real captured E1/E2 through
   `--evidence-bundle`, produced by the accepted current-source collector.
3. **No real authorization manifest exists and I did not write one.** Writing
   one is the lead's act, not a worker's. The gate is only as strong as the
   provenance of the file it reads.
4. **Authorship is not cryptographically attested** (see above).
5. **`CallBudget` atomicity is proven on this POSIX host only.** `O_CREAT|O_EXCL`
   is also atomic on Windows local filesystems, but that is not tested here, and
   it is not guaranteed over some network filesystems.
6. **Synthetic seam receipts remain engineering-only.** `divergence_report`
   reports `acceptance_evidence_eligible: false` whenever any receipt is not a
   `sanitized-real-canary`, even when every comparison is materially divergent.
7. A prepared matrix binds receipts by `context_digest`. If a future authorized
   batch alters the prompt template, previously prepared digests become invalid
   and the matrix must be rebuilt — deliberately, so a stale prompt cannot be
   reused silently.

## Authority

Worker submission only. ChatGPT lead owns acceptance and version promotion.
SB-V04-002 and SB-V04-004 remain `BLOCKED_OWNER_AUTHORIZATION`; SB-EVD-002
remains `WITHHELD`. No public effect, no spend, no API-key route, no injected
runner, no fabricated evidence and no SwarmAI dependency.
