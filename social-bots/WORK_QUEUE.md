# Work queue — LEAD-066 — target LIVE V1.7

Current official version remains **V0.4.x**. Owner development target/ceiling is now **LIVE V1.7**, with genuine live tests and a hard stop at accepted V1.3. This supersedes the prior V1.7 ceiling but grants no model/public/account/host/scheduler/spend/deploy/merge authority.

## Current lane truth

- **Fable — HISTORICAL EVIDENCE ONLY / NO ACTIVE HANDOFF.** Preserve prior branch/evidence; owner directs new Social Bots implementation to Codex. Do not route, message, assign or hand off new work to Fable.
- **Mac Acceptance — independent review-only.** No runtime source edits; author tests never self-accept.
- **Cursor/Core/Intelligence — PARKED / evidence-only.** No overlapping source work.
- **V0.4 canary — FROZEN / evidence preservation.** No further model call authorized.
- **worker-pc — outside critical path** until private-repo clone/auth is demonstrably repaired.

## Immediate order

1. **Codex direct repair mode:** concrete review findings are implemented only in isolated Codex repair branches and returned for ChatGPT formal acceptance. No Fable handoff.
2. **SB-R07-072 remains ACCEPTED** at exact `7acc1695...` as the portable host-test isolation repair only.
3. **V1.7-era due-rotation crash-window repair remains ACCEPTED ENGINEERING** at exact `84f8f05...`; it is reusable infrastructure evidence, not a V1.3 live gate.
4. **PR #8 content-integrity repair is ACCEPTED ENGINEERING** at exact `9d497b4567e022a8e7f93a3ee890af206272b5be`: separate scoped final-review receipt anchor + strict measured-baseline validation. This does not prove receipt immutability or genuine baseline provenance.
5. **PR #9 finite-metrics repair is ACCEPTED ENGINEERING** at exact `30a2ebdfb45110b2bc6fea0f3d50876583487f9c`: invalid fresh/legacy metric values and arithmetic overflow fail closed without losing raw provenance.
6. **PR #10 route freshness/community health repair is ACCEPTED ENGINEERING** at exact `ccfbaf7865557ba30d9148bcce6839b71e9159f1`; LEAD-056 24h/+5m policy is implemented, community unhealthy/stale routes fail closed, zero effects remain zero.

7. **PR #11 route-selection repair is ACCEPTED ENGINEERING** at exact `3f10d0f6eb031c00fff679aae18aa8045d8bd025`: unique eligible route selection, fail-closed zero/multiple matches, platform+alias community scope.
8. **SB-V13-002 is ACCEPTED ENGINEERING** at exact `be0262713eec03c2e7e6b411c2754a7538bad9a6`: provenance/time-window/compatibility/legacy fail-closed boundaries now verified with synthetic/local evidence.
9. **PR #12 route_type schema repair is ACCEPTED ENGINEERING** at exact `a4e7926c79231bfadfc55b56a70a741cc85a2b4e`: documented enum enforced at registry ingest; unknown type rejects whole registry; valid `unsupported` remains parsed/ineligible.
10. **PR #14 composition is ACCEPTED ENGINEERING** at exact `8c86898d1c6641adbf5c9884e1aa7ab2923b1af3`: exact accepted PR12 + PR13 changes compose without new behavior.
11. **LEAD-061 live-readiness audit CONFIRMED** at native evidence `b58ba6d79192e676ac24c06ed2bdbd8d01959ea0`: live promotion remains REVIEW_BLOCKED; ten rows separate accepted engineering/live proof, missing live proof, owner gates and safe offline work.
12. **SB-V11 diagnostic REWORK_FOUND:** unsafe reconciliation can proceed to decision/finish; unchanged reasoning-unavailable signal lacks durable retry ceiling/backoff/exhausted state.
13. **Codex SP1 RELEASED — persistent unsafe-reconciliation gate only:** run existing read-only reconciliation before every unit; unsafe blocks decision/effects/finish receipt across fresh processes and releases only own lease. Retry implementation remains held.
14. **Retry policy SPECIFIED / HELD:** max 3 attempts per unchanged persona+signal blocker fingerprint; 15m then 60m backoff; third => EXHAUSTED; later eligible signals may proceed; only changed blocker fingerprint or explicit audited operator reset rearms.
15. **V0.4 five-call approval request PREPARED / NOT AUTHORIZED:** dormant request + manifest template only; prior one-call grant remains consumed; zero live calls authorized.
16. Preserve and satisfy every genuine V0.4→V1.3 gate in sequence; final LIVE V1.3 promotion requires independently accepted genuine evidence.

## Submitted evidence awaiting independent review

- `0bca4e...` R07-041 — **ACCEPTED narrowly** by LEAD-052; no-scope/ENGINEERING-scope seam repair independently supported on Mac.
- `b5fd038...` scheduler due-work anti-starvation — submitted engineering evidence.
- `c4d31fee...` C05/C06/C07 final-content review binding + prospective experiments — submitted engineering evidence.
- `3da19a9c...` selected V1.7 producer consolidation — submitted engineering evidence.
- `af3fded...` read-only host/provider/account gate dossier — useful blocker evidence only.
- `7acc1695...` SB-R07-072 portable host-test isolation — **ACCEPTED test-only** by LEAD-053; production host predicates unchanged; not host qualification.

## Operational blockers remain factual

Operational/live prerequisites remain factual and unwaived: persistent owner host, native scheduler/session evidence, applicable model/source/reviewer/time inputs, and subsequent V0.8→V1.3 gates must be satisfied with genuine evidence. Synthetic/fixture checks remain engineering evidence only.

## Authority and heartbeat

No new live product-model call, scheduler installation, public effect, account mutation, spending, destructive action, secret exposure, main/public release or SwarmAI dependency is authorized. No new Fable assignment or handoff is authorized. The prior V0.4 exactly-one canary authorization is consumed.

Canonical heartbeat policy is **ONE SESSION = ONE HEARTBEAT**. The old FAST_5M/SOAK experiment is superseded. A resumed/compacted continuation of the same session must not emit another heartbeat; V0.7 recurring liveness is proven by separate OS-scheduled bounded invocations on a real persistent host.


## LEAD-066 current releases

- **PR17 capture integrity ACCEPTED; final pair suitability REWORK_REQUIRED.** Keep E2 TikTok (published Sep 14). Replace E1 Meta (published Jun 4) with a materially distinct public Social Bots-domain source published within 30 days unless later lead-approved otherwise. For both, bind deterministic extraction/signal lineage to exact raw bytes and receipts. Do not rebuild the final matrix until suitability returns.
- **LOCAL provider adapter ENGINEERING RELEASED.** Accepted base: `fec97738ec0e9407415f60228f7c3938613396c3` / tree `43e80b92d8ae559db55a41ed33329695e6fd03fc`. Expected files: `runtime/authorization.py`, `runtime/divergence_prepare.py`, new `runtime/reasoning_local.py`, and `runtime/model_dispatch.py` only if necessary, plus focused tests. Codex direct owns implementation. No real inference.
- **LOCAL provider contract:** distinct `ollama-local` mode; loopback-only `127.0.0.1:11434`; initial model `qwen3.5:9b`; exact endpoint/model/config included in execution binding; no remote fallback, API/OpenRouter fallback, pull/download, daemon start/restart or fallback model; five durable attempts, no retries, no sixth attempt.
- **Fail-fast batch diagnostic RELEASED:** offline reproduction only. Confirm whether a non-`proposal_received` case permits the next case to reserve/execute. No source edit until confirmed and separately released.
- **Retry/backoff implementation remains HELD.**
- **SB-R07-073/074 remain PLANNED.**
