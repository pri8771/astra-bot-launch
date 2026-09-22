# Social Bots host-test repair — prepared, not handed off

State: **OWNER_APPROVAL_REQUIRED_FOR_FABLE_HANDOFF**. Owner authorized isolated local fixes and explicitly withheld Fable handoff approval. Codex authored this test-only repair and cannot independently accept it. ChatGPT/Mac Acceptance retain formal/independent review; Fable remains integration owner.

- Artifact: SB-R07-072 portable host-test isolation, SP1. Minimum live target V0.7; native ceiling V1.7, then stop.
- Canonical instructions/state: `chatgpt/social-bots-plan-20260920@4a56a57dd70bb2448c9f8c4b286c373e016f2019`, `AGENTS.md`, `coordination/codex/START.md`, native recovery and `delivery/V17_ACCEPTANCE.md`.
- Expected worker base: `fable/social-bots-v23-fasttrack-20260921@e9678f8bead4f872c199bdf09dbf709a8f649159`, unchanged on refresh. Worker process/dirty state UNKNOWN; not touched.
- Local repair: `codex/bots-host-tests-20260922@7acc1695d2961267580a156f31df6a5991476654`; clean separate worktree, no upstream configured, no push.
- Only changed file: `social-bots/tests/test_host_preflight.py`. Production host suitability predicates and grants are unchanged.

The tests now explicitly simulate Linux or Darwin and clear inherited environment markers. All seven original tests remain; four scheduler-presence/absence cases were added. Positive host/attestation tests still yield only a candidate, never LIVE acceptance. Ephemeral-host and absent-scheduler negatives remain.

Exact Mac full suite: **711 run / 709 passed / 0 failures / 0 errors / 2 skipped**. Host module: 11 passed. The preserved skips require an enabled real HTTPS freeze capture and an actual SB-V04-005 canary receipt; they are not passing live evidence.

Evidence: [manifest](../receipts/evidence/CODEX-REPAIR-20260922/manifest.json), [full suite](../receipts/evidence/CODEX-REPAIR-20260922/bots-final-checks.txt), [commands/exits](../receipts/evidence/CODEX-REPAIR-20260922/bots-final-checks.json), [source/environment](../receipts/evidence/CODEX-REPAIR-20260922/bots-repair-environment.json).

Canonical STATE/ARTIFACT_INDEX at `4a56a57` record ChatGPT LEAD-052's narrow ACCEPTED verdict for SB-R07-041, based on the earlier independent evidence. Preserve that verdict; it does not accept this new host-test repair or a version. The referenced `social-bots/lead-reviews/LEAD-052_2026-09-22T0236.md` is absent at that canonical ref; use the exact STATE/ARTIFACT_INDEX commit as the observed verdict evidence and ask the lead to persist its missing detailed record. No lead review was invented here.

Recommendation on original host tests: **REWORK_FOUND**. This authored repair is **REVIEW_BLOCKED** pending independent review and an authorized verdict. V0.7 remains blocked on its genuine V0.4–V0.7 predecessors, fresh bounded model manifest, source/reviewer chain, designated persistent owner host, three native firings, failure/recovery evidence and two genuine development/lead/later-worker cycles.

After explicit owner approval only: deliver the one-file diff and evidence to the existing Fable session and lead; refresh its current branch, reconcile non-force, capture ACK, and rerun exact-source host/full checks after integration. No runtime change, scheduler installation, model call, account/public action or new grant is part of this packet. SESSION_ONCE remains once per fresh session; this resumed session emitted none.
