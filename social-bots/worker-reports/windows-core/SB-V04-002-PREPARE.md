# Worker report — SB-V04-002 / SB-V04-004 prepare-only work (Core lane)

- **Artifacts:** SB-V04-002, SB-V04-004
- **Requested status:** `SUBMITTED` for the prepare-only work below.
  **SB-V04-002 and SB-V04-004 themselves remain `BLOCKED_OWNER_AUTHORIZATION`
  and nothing here changes that.** Not self-accepted.
- **Lane:** Core (`windows-core`)
- **Session branch:** `claude/quirky-shannon-t1377u`, branched from
  `claude/social-bots-windows-core-host` @ `c6b67ff`
- **Source SHA:** `af2e00e6995a814a8d62d0352d29a5b369b6e650`
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
| 2 | immutable bounded context JSON per case | `write_prepared` refuses overwrite; atomic + fsync |
| 3 | SHA-256 for evidence bytes, evidence receipt, bounded context, exact prompt | `PreparedCase` digests; `prompts/PROMPT_DIGESTS.json` |
| 4 | automatic single-variable isolation | `isolation_report` / `verify_isolation` (two layers, below) |
| 5 | proposal/receipt validation + material-divergence reporting | `divergence_report` |
| 6 | hard lead-created authorization-manifest requirement | `runtime/authorization.py::authorize` |
| 7 | exact call budget + atomic pre-spawn accounting | `runtime/authorization.py::CallBudget` |
| 8 | no-retry semantics | slots never reused; outcomes write-once |
| 9 | fail closed before spawning Claude | the gate, plus `runtime/live_route_guard.py` |
| 10 | fixtures labeled engineering-only | `provenance_label`; `acceptance_eligible` false for fixtures |

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

Committed digests (`evidence/SB-V04-002-prepare/PREPARE_STATUS.json`, truncated):

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
demonstrates that the digest layer is blind to a summary-only change and that
the prompt layer catches it.

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
- expiry is judged against the real clock — `authorize` takes no caller-supplied
  `now`, deliberately.

Two things no manifest can waive, re-checked at call time: a present
`ANTHROPIC_API_KEY`, and an injected runner.

**Honesty boundary on authorship.** This code cannot cryptographically prove a
manifest was written by the lead rather than by a worker. It records the
manifest's file digest, `created_by` and `owner_authorization_ref` into the
grant and every receipt, and exposes `authorship_attested_by_code: false`.
Authorship is a git-provenance fact for an independent audit.

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

- Exclusive creation is the atomic primitive; concurrent workers cannot share a
  slot. (Verified under an 8-process race during review: exactly `[1,2,3,4,5]`,
  no duplicates.)
- Reservation starts above a **high-water mark**, so deleting a slot file cannot
  buy another call. Removing evidence must never widen an authorization.
- A worker that dies after reserving leaves the slot consumed. Over-counting a
  crashed call is safe; under-counting could exceed the owner's exact
  authorization. `audit()` reports such slots as `reserved_not_recorded`.
- Outcomes are write-once. `provider_unavailable`, `invalid_proposal` and
  `provider_exception` each consume their slot permanently and are recorded
  verbatim. There is no except-and-retry branch anywhere in the execution path.

Committed budget state for this run scope: `consumed: 0`, `remaining: 5`,
`retry_permitted: false`.

## Adversarial review of this session's own code, and what it found

Before submitting, this work was put through an adversarial correctness review.
It found real defects, listed here because they say more about the artifact than
a clean bill of health would. All are fixed at `918c42e` with regressions in
`tests/test_review_hardening.py`.

The two that mattered most:

1. **The gate guarded one code path, not the product.** `authorize` was only ever
   called from `divergence_prepare.execute_batch`. `reasoning.resolve_provider`
   picks a provider from `SBOTS_REASONING` alone, so
   `SBOTS_REASONING=claude-cli` on *any* other entrypoint — including the new
   bounded worker — would spawn the real Claude Code CLI with no manifest, no
   budget and no accounting. The module docstring's claim that "no live
   divergence execution may occur merely because code supports it" was false as
   written. Fixed by `runtime/live_route_guard.py`, which every non-batch
   entrypoint now consults before a provider exists; refusal evidence is at
   `evidence/SB-V04-002-prepare/LIVE_ROUTE_REFUSED.txt` (exit 6).

2. **The batch never bound what it invoked to what it prepared.**
   `execute_batch` rebuilt each context from caller-supplied personas and
   snapshots and sent it without checking it matched the prepared case — while
   still writing the *prepared* digest into the budget slot. A batch could
   therefore invoke different personas or different evidence, and the durable
   ledger would record a digest for a call that was never made, making the whole
   isolation proof decorative. Fixed: both the context digest and the prompt
   payload digest are checked before the slot is reserved, so a mismatch costs
   no authorization.

The fix for (1) went in twice, because the first attempt was incomplete. Adding
the guard to `bin/worker_once.py` closed that entrypoint and left every other
one open — `reasoning.resolve_provider` builds the CLI provider from an
environment variable, so guarding callers one at a time is a losing game. The
guard now also sits **at the spawn point**: `ClaudeCodeReasoningProvider`
refuses unless a valid canonical manifest is in force, whenever it would launch
the real CLI. An injected runner spawns nothing and is exempt, which is what
keeps the existing `test_reasoning_cli` seam working (50 reasoning tests still
pass unchanged, `evidence/.../REASONING_REGRESSION.txt`).

Both layers are demonstrated in `evidence/.../LIVE_ROUTE_REFUSED.txt`: the
entrypoint exits 6, and independently `resolve_provider` returns a provider
whose `available()` is `False` and whose `propose()` returns `None`.

Also fixed: an expired manifest could be revived through a caller-supplied
clock; deleting a slot file freed budget; `acceptance_evidence_eligible` could
be reached from entirely hand-authored files (it now additionally requires a
call-budget ledger binding each case to a slot that actually returned a
proposal); `verify` skipped the prompt bytes by default, which is the layer that
catches an edited prompt file; and the "immutable" artifacts were written
non-atomically.

## Evidence

`social-bots/worker-reports/windows-core/evidence/SB-V04-002-prepare/`

- `PREPARED_MATRIX.json` — the five cases, contexts, digests, isolation report
- `prompts/P0..P3,E0.prompt.txt` + `PROMPT_DIGESTS.json` — the exact prompts
- `PREPARE_STATUS.json` — isolation, digests, gate state, budget state
- `GATE_OUTPUT.json` — the gate denying live execution right now
- `VERIFY_OUTPUT.json` — independent re-derivation of every digest, prompt bytes included
- `LIVE_ROUTE_REFUSED.txt` — a live reasoning mode refused on the bounded worker
- `PREPARE_STDOUT.txt`, `FOCUSED_TESTS.txt`, `HARDENING_TESTS.txt`, `FULL_SUITE.txt`

## Exact commands and results

```
$ python3 bin/prepare_divergence_matrix.py prepare \
    --out-dir worker-reports/windows-core/evidence/SB-V04-002-prepare \
    --run-scope v04-divergence-prepare --lane windows-core --home /tmp/.../budget-home2
  planned_call_count: 5   all_isolated: true
  live_execution_permitted: false   live_execution_performed: false
  acceptance_eligible: false                                          (exit 0)

$ python3 bin/prepare_divergence_matrix.py verify \
    --matrix .../PREPARED_MATRIX.json
  verified: true   prompt_bytes_verified: true   isolation.all_isolated: true   (exit 0)

$ python3 bin/prepare_divergence_matrix.py gate --lane windows-core \
    --run-scope v04-divergence-prepare
  live_execution_permitted: false   manifests_present: []             (exit 0)

$ SBOTS_REASONING=claude-cli python3 bin/worker_once.py --lane windows-core ...
  LIVE ROUTE REFUSED: live reasoning mode 'claude-cli' requested but not
  authorized: no canonical authorization manifest ...                 (exit 6)

$ python3 -m unittest tests.test_v04_authorization_gate tests.test_v04_divergence_prepare -v
  Ran 53 tests ... OK

$ python3 -m unittest tests.test_review_hardening -v
  Ran 42 tests ... OK

$ python3 -m unittest tests.test_reasoning_cli tests.test_reasoning_contract \
      tests.test_reasoning_receipt -v
  Ran 50 tests ... OK      (pre-existing reasoning tests, unchanged behaviour)

$ python3 -m unittest discover -s tests
  Ran 312 tests in 4.615s
  OK (skipped=1)
```

The one skip is the pre-existing real-canary intake skip, unchanged. The suite
was 160 passed / 1 skipped before this session.

## Known limitations — read these before accepting anything

1. **This is not empirical divergence evidence.** No model was called. The
   prepared matrix proves design and controls, not causation.
2. **The committed snapshots are engineering fixtures**, labeled
   `engineering-fixture`, which forces `acceptance_eligible: false`. A real batch
   must supply real captured E1/E2 through `--evidence-bundle`, produced by the
   accepted current-source collector.
3. **No real authorization manifest exists and I did not write one.** Writing one
   is the lead's act, not a worker's. The gate is only as strong as the
   provenance of the file it reads.
4. **Authorship is not cryptographically attested** (see above).
5. **`CallBudget` atomicity is proven on this POSIX host only.**
   `O_CREAT|O_EXCL` is also atomic on Windows local filesystems, but that is not
   tested here, and it is not guaranteed over some network filesystems.
6. **The budget ledger lives under `SBOTS_HOME`.** "Survives process restart"
   holds only while that root is stable; a different `--home` for the same run
   scope starts a fresh ledger. A scheduled install must pin it.
7. **Synthetic seam receipts remain engineering-only.** `divergence_report`
   reports `acceptance_evidence_eligible: false` whenever any receipt is not a
   `sanitized-real-canary`, and now also whenever no call-budget ledger binds
   each case to a slot that returned a proposal.
8. **`differing_variables` compares six named keys.** A key added to a bounded
   context outside that set is invisible to the digest layer. Low impact — the
   prompt layer compares the full key union of what is actually sent — but it is
   a real bound on the digest-layer claim.
9. A prepared matrix binds receipts by `context_digest`. If a future authorized
   batch alters the prompt template, previously prepared digests become invalid
   and the matrix must be rebuilt — deliberately, so a stale prompt cannot be
   reused silently.
10. **The spawn-point guard covers the `claude-cli` route only.** That is the
    route that definitely launches a billable subprocess. `SBOTS_REASONING=model`
    with a host-registered live callable is covered at the entrypoint
    (`bin/worker_once.py`) but not at the spawn point, because the runtime cannot
    tell a live callable from the receipt-replay callable SB-V04-004 legitimately
    registers. A host that wires a real model callable must not rely on the
    backstop.
11. **The guard keys on the real launcher captured at import.** Monkeypatching
    `reasoning_cli._default_cli_runner` — a documented test seam — is therefore
    exempt by design. That is deliberate (a patched runner spawns nothing) but it
    does mean the guard protects against a configuration mistake, not against
    someone editing the module.
12. `bin/run_worker.py` and `bin/dry_run.py` were not themselves modified, to
    avoid disturbing other lanes' committed evidence. They inherit the
    spawn-point refusal, so `SBOTS_REASONING=claude-cli` on those now fails
    closed to BLOCKED_REASONING_UNAVAILABLE rather than spawning — but they do
    not carry the explicit exit-6 signal that `worker_once.py` gives a
    scheduler.

## Authority

Worker submission only. ChatGPT lead owns acceptance and version promotion.
SB-V04-002 and SB-V04-004 remain `BLOCKED_OWNER_AUTHORIZATION`; SB-EVD-002
remains `WITHHELD`. No public effect, no spend, no API-key route, no injected
runner, no fabricated evidence and no SwarmAI dependency.
