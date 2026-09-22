# Due-rotation crash-window repair

State: READY_FOR_LEAD_REVIEW; author candidate REVIEW_BLOCKED pending independent verdict. Direct Codex SP1 repair of submitted due-rotation artifact `b5fd038`, under the owner's no-Fable/direct-completion instruction and canonical LEAD-053 routing. No runtime was scheduled or activated.

- Canonical router/queue: `chatgpt/social-bots-plan-20260920@290eaefab581901c9643e7de8719829150c59acf`.
- Source base: accepted test-only `7acc1695d2961267580a156f31df6a5991476654`, worker ancestor `e9678f8bead4f872c199bdf09dbf709a8f649159`.
- Candidate `codex/bots-rotation-durability-20260922@84f8f05b22d33dcfc1edd0d2fc8d98ddcc3e1b6d`. Original worker checkout untouched.
- Three-file write surface: `social-bots/bin/worker_once.py`, `social-bots/runtime/worker.py`, `social-bots/tests/test_due_rotation.py`.

The prior launcher recorded rotation only after run_one_unit completed and released the lease. A cursor-write failure/crash could leave a completed bot first in line again. The worker now accepts an optional claim callback, invoked under its current ownership fence after lease acquisition and before reconciliation/useful work. The launcher durably records the claimed bot there. Write failure aborts and releases the lease before any cycle; a later cycle failure leaves the successful claim cursor in place. Busy candidates do not advance it. A claim is counted even if its later work fails; this is rotation of claims, not a completion ledger.

Two new failure-window regressions fail against the base. Focused worker/rotation/worker_once tests:39pass. Exact-source full suite: **713run/711pass/2existing genuine-evidence skips**, exit0; git diff check passes. [Commands/tree](../receipts/evidence/CODEX-ROTATION-20260922/checks.json), [logs](../receipts/evidence/CODEX-ROTATION-20260922/checks.txt), [manifest](../receipts/evidence/CODEX-ROTATION-20260922/manifest.json). All provider inputs and state are synthetic/temporary; no real model, SESSION_ONCE, scheduler, public action or host qualification.

Original due-rotation source recommendation: REWORK_FOUND. Request ChatGPT's exact-SHA review; Codex will repair findings directly. LEAD-053 host-test acceptance remains narrow and unchanged. No V0.7 live acceptance, new grant, Fable dispatch, merge or deployment is requested.

## Actual authorized verdict

Canonical `8ac5bc60a5f13c659b17fda8709c19e0d9d7d79c` contains `LEAD-054_2026-09-22T0418.md`: **ACCEPTED ENGINEERING at exact84f8f05b22d33dcfc1edd0d2fc8d98ddcc3e1b6d**. ChatGPT independently inspected the exact diff and author red/green evidence. The separate mechanical reviewer's unpersisted49-test report was explicitly excluded from formal independent-execution evidence. This resolves the candidate review hold only; no real-host, SESSION_ONCE, V0.7 or version acceptance was granted.
