# Work queue — LEAD-060 — target LIVE V1.3

Current official version remains **V0.4.x**. Owner development target/ceiling is now **LIVE V1.3**, with genuine live tests and a hard stop at accepted V1.3. This supersedes the prior V1.7 ceiling but grants no model/public/account/host/scheduler/spend/deploy/merge authority.

## Current lane truth

- **Fable Integrator — EXISTING OWNERSHIP PRESERVED / NO NEW HANDOFF.** Owner explicitly directs Codex to finish concrete fixes directly. Do not route, message, assign or hand off new Social Bots work to Fable without fresh owner approval.
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
10. **Codex composition RELEASED:** from accepted base `3f10d0f6...`, compose exact accepted PR12 + PR13 changes only; verify hashes/diffs, run route+metrics focused suites and full suite; no semantic edits beyond mechanical conflict resolution.
11. Preserve and satisfy every genuine V0.7→V1.3 gate in order; final LIVE V1.3 promotion requires independently accepted genuine evidence.

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
