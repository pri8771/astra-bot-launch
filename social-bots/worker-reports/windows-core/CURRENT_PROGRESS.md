# Core lane — current progress

**Session:** `s-20260921T174817Z-0e532933` (SESSION_ONCE, 2026-09-21T17:48:17Z)
**Branch:** `claude/quirky-shannon-t1377u`, branched from
`claude/social-bots-windows-core-host` @ `c6b67ff`
**Canonical read:** `671abbc` / **LEAD-038**
**Contract:** `social-bots/CLAUDE_EXECUTION_TO_V07.md`
**Source SHA for both submissions:** `a73b7b58de8f3669795b81637bff55247d67943c`

## Heartbeat

Exactly **one** durable `SESSION_ONCE` heartbeat was appended to
`HEARTBEAT_LOG.jsonl` and mirrored to `HEARTBEAT.json`, per the LEAD-038 owner
policy. No periodic loop, no soak, no daemon. The record was written by the new
`runtime/session_heartbeat.py`, which needs no `gh` and structurally refuses a
second record for one `session_id`.

Transport truth: `gh` is absent on this host, so the record accurately says
`issue_comment_posted: false, reason: "gh CLI not found on PATH"`. The Issue #3
visibility comment was posted afterwards through this session's GitHub MCP
transport. The durable record was **not** rewritten to claim otherwise.

## Model-call gate

Canonical state contains **neither** a fresh explicit owner authorization **nor**
a lead-created canonical authorization manifest (`social-bots/authorizations/`
does not exist; a repo-wide search found only prose references).
**No adaptive/model call was made this session.**

That is now enforced in two layers rather than assumed. An adversarial review of
this session's own code found that `SBOTS_REASONING=claude-cli` was enough to
make any entrypoint spawn the real Claude Code CLI with no manifest, no budget
and no accounting — the V0.4 gate only ever guarded the divergence batch.
`bin/worker_once.py` now refuses such a mode with exit 6 before any provider
exists, and `ClaudeCodeReasoningProvider` itself refuses at the spawn point
unless a valid manifest is in force. Evidence:
`evidence/SB-V04-002-prepare/LIVE_ROUTE_REFUSED.txt`.

## Submitted this session — `SUBMITTED`, not self-accepted

| Work | Report |
|---|---|
| V0.4 prepare-only divergence matrix, hashing, two-layer isolation, authorization gate, exact call budget, no-retry | `SB-V04-002-PREPARE.md` |
| SB-V07-001 host worker package, scheduler adapters, session heartbeat, invocation receipts, direction consumption, real SIGKILL crash/restart proof | `SB-V07-001.md` |

Tests: `python3 -m unittest discover -s tests` → **312 passed, 1 skipped**
(was 160/1 at session start; the one skip is the pre-existing real-canary intake
skip, unchanged).

## Artifact status — unchanged by this session

- **SB-V04-002** — `BLOCKED_OWNER_AUTHORIZATION`. Prepare-only work is done; the
  five real adaptive invocations are not authorized and were not made.
- **SB-V04-004** — `BLOCKED_OWNER_AUTHORIZATION`, same reason.
- **SB-EVD-002** — `WITHHELD`.
- **SB-V07-001** — submitted for lead review.
- **SB-V07-002** — remains `BLOCKED`: no owner-authorized always-on host, and no
  OS scheduler was registered anywhere. This session's invocations are direct
  CLI runs on a Linux CCR container, labeled engineering demonstration only.

## Lanes not touched

Intelligence (`claude/social-bots-intelligence-repair-v2`), Acceptance
(`claude/social-bots-mac-qa-control`) and the frozen canary branch were not
edited. `bin/run_worker.py` and `bin/dry_run.py` were left unmodified to avoid
disturbing other lanes' committed evidence; they inherit the spawn-point refusal
but do not carry the explicit exit-6 signal.

## What the lead needs to decide

1. Accept or reject the two submissions above.
2. If a live V0.4 batch is ever to run: write a canonical authorization manifest
   under `social-bots/authorizations/` (schema and validation in
   `runtime/authorization.py`; `tests/test_v04_authorization_gate.py` shows a
   valid fixture shape), after a fresh explicit owner authorization. The code
   records but cannot attest lead authorship — that is a git-provenance fact.
   Note that with no manifest present, **all** live model calls are now refused
   repo-wide, which is the intended posture but is worth knowing before the next
   authorized batch.
3. Whether to write `social-bots/directions/<lane>.json` files. Scheduled
   sessions read them in preference to the `STATE.json` fallback, and an explicit
   `halt` boolean is more reliable than the fallback's keyword heuristic. The
   fallback now refuses to guess when a lane matches more than one branch, so an
   ambiguous lane name fails closed rather than silently missing a halt.
4. Whether to retire `bin/heartbeat_reporter.py` and `bin/worker_heartbeat.py`,
   both superseded for new sessions but left in place so committed lane history
   stays readable.
5. Whether to extend the exit-6 signal to `bin/run_worker.py` and
   `bin/dry_run.py`, which would need touching another lane's evidence surface.
