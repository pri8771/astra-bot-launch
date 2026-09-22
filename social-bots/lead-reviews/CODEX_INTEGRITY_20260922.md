# Content review and baseline integrity — Codex repair

State READY_FOR_LEAD_REVIEW; recommendation REVIEW_BLOCKED pending actual ChatGPT lead verdict. Original C05/C06/C07 defects REWORK_FOUND. Author Codex; bounded mechanical agent checks are not independent acceptance. No Fable handoff.

Canonical routing: chatgpt/social-bots-plan-20260920@0e390f147ed86d8c09aa34269ffc0d9be1f9a601. Preserve LEAD-053 host-test and LEAD-054 rotation engineering acceptance; official version/live gates do not advance. Candidate codex/bots-review-integrity-20260922@9d497b4567e022a8e7f93a3ee890af206272b5be is [draft PR8](https://github.com/pri8771/astra-bot-launch/pull/8), isolated and stacked on accepted84f8f05, not a canonical application-snapshot merge. Worker base e9678f8 unchanged; no writer or runtime takeover.

Bounded SP2 surface: runtime/pipeline.py, runtime/receipts.py, two focused test files. Recomputed hashes stored beside modified queue text previously bypassed verification. Final-review bindings now include a reference to a separately persisted scoped review receipt, whose digest is reloaded by enqueue and queue consumers. Cultural reviewer attribution is included in the bound material. Missing, corrupt, transplanted and symlinked receipts fail closed. Old queue entries without an anchor need genuine re-review; no approvals are backfilled.

Distinct `review` receipt kind avoids worker start/finish/failure semantics and invocation counts. A mechanical review caught that collision in the first draft; native fencing/takeover tests pass after correction. The local receipt store is an audit anchor, not an external signature or protection against a writer who controls both stores.

Prospective measured baselines now require matching metric, finite numeric value (excluding booleans), timezone-aware ISO timestamp, MEASURED status and nonempty source reference. A null baseline cannot claim MEASURED. Existing schema and empty prospective baseline remain supported; these shape checks do not prove a genuine source measurement.

**723 tests run /721 passed/2 existing genuine-evidence skips**, plus separate agent89focused checks with zero skips. Compile/diff checks pass. [Source/tree/commands/hashed logs](../receipts/evidence/CODEX-INTEGRITY-20260922/manifest.json). No real model/provider/publication action or host firing occurred.

Next native assignment: Codex SP1 response to actual review findings; ChatGPT to review exact9d497b4 and issue verdict. Scope remains liveV0.7 minimum/V1.7 ceiling. Owner-designated persistent host/existing scheduler, bounded model manifest, source/reviewer prerequisites and genuine three-firing/two-interval plus review-cycle proof remain open. SESSION_ONCE remains once per fresh session; none emitted on this continuation.
