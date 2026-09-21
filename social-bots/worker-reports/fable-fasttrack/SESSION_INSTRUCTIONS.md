# Fable fast-track — SESSION_INSTRUCTIONS — LEAD-047

Branch: `fable/social-bots-v23-fasttrack-20260921`
Canonical coordination: `chatgpt/social-bots-plan-20260920`
Canonical release commit: `eece1d3a62417802e4316f028fbec098f3220128`
Official phase: **V0.4.x / V0.4 in progress**

## Current state

The prior LEAD-045/046 pause and LEAD-043 new-files-only restriction are **superseded**. Fable is now the sole primary implementation/integration owner for the released delivery campaign, including shared recovery/runtime integration. Preserve all submitted evidence through material checkpoint `a204ad0827748a4e9661f1945b8e025d53d0ae09`; current pre-release branch head `72a55319cf41f9910c5d3b9623129de3ac0eea31` is a lead-authored pause acknowledgement, not new worker implementation.

## Start here

Fetch canonical coordination and read these files from the fetched canonical ref before editing:
- `social-bots/delivery/FINAL_RUN.md`
- `social-bots/delivery/ACTIVE_EXECUTION.json`
- `social-bots/delivery/TASKS.json`
- `social-bots/delivery/reviews/LEAD047_AUDIT.md`
- `social-bots/delivery/reviews/LEAD047_PROBES.json`
- `social-bots/STATE.json`
- `social-bots/SESSION_ROUTER.md`
- `social-bots/MILESTONE_MANIFEST.md`
- `social-bots/ARTIFACT_INDEX.json`
- latest `social-bots/AGENT_MESSAGES.md`

Start a genuinely fresh top-level worker session and emit exactly one real durable `SESSION_ONCE` heartbeat after reading current coordination. Do not run a periodic heartbeat loop and do not treat a lead comment as worker acknowledgement.

## Immediate implementation order

Follow `delivery/FINAL_RUN.md`. First reproduce the LEAD-047 negative scenarios against the **actual current modules**, then repair before expanding:

1. **R07-041 direct callable authorization:** every live-capable callable/provider path must fail closed without a valid canonical scoped authorization manifest. Use harmless local sentinels only; zero real model calls.
2. **Specialist capability/fixture bypass:** production must not trust caller-supplied `adaptive`/fixture labels to bypass authorization. Prove refusal through the real production construction path.
3. **Shared durable pre-dispatch budgets:** reserve atomically before dispatch across concurrency, reentry, wrappers/processes and restart; exceptions/crashes consume or remain uncertain; check expiry/revocation at dispatch.
4. **Retained-output integrity:** verify canonical path/type and the exact bytes/hash actually consumed; cover wrong scope, replacement, symlink and late-write cases.
5. Then repair hard deadline/finalization, crash-consistent fenced strategy publication, final-content review binding, and the missing S20/S21/S22 + H1–H4 / DEVELOPMENT_ARTIFACT integration required by `FINAL_RUN.md`.

Run focused regressions and the actual full suite on the pinned candidate. Report exact discovered/pass/fail/error/skip counts and exact source/evidence SHAs. Worker-local success never self-accepts an artifact.

## Ownership / handoff

- Cursor and legacy implementation lanes are parked. Before shared-file edits, fetch their latest refs and preserve any newer material checkpoint rather than resetting or overwriting it.
- QA/Acceptance is review-only and must not be used as an implementation lane.
- Use the C01–C31 delivery queue plus existing SB feature packets as the one closure queue; prior NR-* files are supporting reference, not a second campaign.
- Prioritize genuinely working integrated V2.3 before later V3.0 scaffolding.

## Hard authority limits

No live Claude/adaptive/product-model call, public posting/reply/message, new account action beyond separately scoped necessary owner-approved setup, PAYG/new spend, destructive action, credential exposure, fabricated operational evidence, engagement manipulation, main/public release, or SwarmAI dependency is authorized by this release. The prior exact-one canary authorization is consumed.
