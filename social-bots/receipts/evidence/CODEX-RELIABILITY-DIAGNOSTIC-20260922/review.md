# Bots SB-V11 reliability diagnostic — independent engineering recommendation

project/repository: `social-bots` in the Bots repository

artifact and submission: LEAD-062 read-only SB-V11-001/002 reliability diagnostic; scratch evidence only, no source submission

reviewer actual identity/role: Codex engineering diagnostic workers; root independently repeated both reproductions. This is an engineering recommendation, not formal lead acceptance.

code SHA + relevant production tree/dependency/schema identity: accepted composition `8c86898d1c6641adbf5c9884e1aa7ab2923b1af3`; tree `72bccc0dc5ee9eaf2919dcdfd0ac35b568719c5a`

evidence SHA/run IDs and source refs: file-level SHA-256 values are in `manifest.json`; independent repeats are `bots-lead062-unsafe-reconcile-root.log` and `bots-v11-unavailable-retry-root.log`; original harness outputs are retained separately

contract read from ref/SHA: coordination commit `ed3aee4cf21da403f92ef565f66e48a1824b67c2`, `social-bots/lead-reviews/LEAD-062_2026-09-22T0805.md`

reviewed paths: `runtime/worker.py`, `runtime/leasing.py`, `runtime/decision.py`, relevant state/research/authorization dispatch paths, `tests/test_fencing.py`, `tests/test_production_read_paths.py`, and retained reliability notes/harnesses

checks actually executed + exact commands/exits/log refs:

- Unsafe reconciliation: `python3 /tmp/bots-lead062-unsafe-reconcile-repro.py`; exit 0; original and independent outputs in the corresponding `repro.log` and `root.log` files.
- Unavailable retry: one seed, four immediate fresh Python `run` processes, then one report process against one temporary `SBOTS_HOME`; all exited 0. Exact command is recorded in `bots-v11-reliability-audit-first-gap.md`; original and independent outputs are retained.

worker-reported checks NOT independently repeated: no full suite, genuine scheduler firing, elapsed six-hour/24-hour interval, host restart, cross-host fencing, model/provider/account/public delivery, or unattended operation was run for this packet

positive production-path coverage: existing same-POSIX-host lease acquisition, generation fencing, stale-owner commit refusal and safe takeover tests were inspected. The retry reproduction confirms unavailable adaptive reasoning stays fail closed, performs no provider call or external effect, leaves the signal unresolved, and persists ordinary state across fresh processes.

adversarial coverage:

1. **Unsafe reconciliation ignored.** A stale takeover saw `queue_items=1`, `unauthorized_published=1`, `safe=false`; `run_one_unit` nevertheless called `decision.run_cycle`, wrote a verified finish receipt and released the lease. `runtime/worker.py` records the reconciliation result at lines 85-89, then proceeds unconditionally at lines 94-98. `_reconcile` detects the violation at lines 192-210. The root repeat reproduced the same behavior.
2. **Persistent unavailable retry opportunity.** Four immediate fresh-process invocations against the same runtime each returned `blocked_reasoning_unavailable`, kept the same signal pending and unconsumed, and advanced cycles 1 through 4. No durable attempt ceiling, backoff progression, exhausted state or block/dead-letter file appeared. This proves persistent retry opportunity after restart. It does **not** prove four scheduler firings, a six-hour delay, 24 hours of elapsed operation, or unattended-host behavior.

real-proof evidence type and remaining gates: ENGINEERING synthetic temporary-filesystem evidence only. Genuine scheduler/host time, crash/restart timing, cross-host ownership, provider delivery, external effects and unattended behavior remain unproven and authority-gated.

findings with smallest reproducer/repair:

- First repair candidate: make an unsafe reconciliation verdict authoritative. On `safe is not True`, record a truthful blocked/failure outcome, skip `decision.run_cycle`, create no new candidate/experiment/queue effect, and release only the current owner's lease. Add one narrow adverse regression. This repair is concrete and can be separately released now.
- Retry policy remains specification-blocked. Before implementation, the lead must explicitly choose the durable per-signal blocker identity/fingerprint, attempt ceiling, backoff progression, exhausted/block representation, later-signal fairness, reset triggers, operator reset semantics and how changed provider/route availability re-arms eligibility. Preserve fail-closed no-effect behavior and never infer a fresh live-call grant.

recommendation: **REWORK_FOUND**

formal acceptance authority and requested action: ChatGPT/Bots lead remains formal authority. Request a separate narrow release for unsafe-reconciliation fail-closed repair first. Request an explicit bounded retry ceiling/backoff/reset contract before any unavailable-retry implementation. Do not promote SB-V11 or live product status from these diagnostics.

next bounded independent task: after lead release, reproduce red/green only for the unsafe-reconciliation gate. Retry implementation must wait for the explicit contract. No live, provider, account, public, host, scheduler, spend, merge or deployment action is requested.
