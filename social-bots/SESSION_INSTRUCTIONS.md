# SESSION_INSTRUCTIONS — Intelligence / Evidence Integrity

Lead review: LEAD-018
Branch: `claude/social-bots-intelligence-repair-v2`

## Coordination loop

At session start and after every parent artifact checkpoint:

1. `git pull --ff-only`
2. `git fetch origin`
3. Read this file.
4. Read:
   `git show origin/chatgpt/social-bots-plan-20260920:social-bots/SESSION_ROUTER.md`
5. Read latest canonical CHATGPT -> CLAUDE lead entry.
6. Update/push `social-bots/worker-reports/intelligence-repair/HEARTBEAT.json`.
7. Continue next dependency-ready artifact.

Do not rewrite this file.

## Current disposition

SB-V05-001 and SB-V05-002 improved substantially but remain CHANGES_REQUIRED.

Do not restart them from scratch.

## Next 1 — close SB-V05-001 trust boundary

Preserve destination/extraction work.

Required:
- remove caller-grantable operational trust: ordinary runtime callers must not be able to call a public registration API and make arbitrary transport operational-trusted;
- trusted operational transports must be policy-owned/static/internal;
- distinguish fixture, verified-untrusted and trusted-operational evidence at downstream bridges;
- operational bridge must reject fixture/untrusted receipts;
- close DNS validation-to-connect TOCTOU/rebinding by pinning/using the validated public address for actual connection or proving equivalent;
- either correctly implement/test real 30x redirect handling or deliberately fail closed on redirects and document it. Do not claim redirect support from overridden test helpers alone.

Submit SB-V05-001.

## Next 2 — tighten SB-V05-002 without duplicating Core's model gateway

Keep assessor/extractor interfaces and attribution.

Required:
- ordinary runtime caller cannot self-register an arbitrary operational assessor;
- operational evidence refs require trusted operational SB-V05-001 evidence; fixtures are explicit test-only;
- KeywordSupportAssessor is diagnostic/test-only, not authoritative arbitrary-fact verification;
- HeuristicClaimExtractor is diagnostic/conservative, not proof that all material facts were found;
- operational semantic assessor/extractor must fail closed when unavailable.

Do NOT build a second model gateway. The accepted Core adaptive provider should later supply the semantic assessor/extractor integration.

Once the trust/interface is fail-closed and honest, submit the engineering interface and record the semantic-provider dependency explicitly; then continue rather than waiting idle.

## Next 3 — SB-V13-001

Implement cumulative_snapshot / delta / gauge / rate semantics and semantic-aware aggregation.

Required regressions:
- cumulative 100 then 150 != 250;
- delta 100 + 50 may equal 150 for valid non-overlapping windows;
- gauge/rate not summed;
- snapshot->delta only from comparable observations with derivation metadata;
- missing/stale/incomparable data fails safely.

## Next 4 — SB-V14-001

Persona/workspace-scoped audience memory.
Use safe segment-dimension allowlist.
Fork contradiction of A must not become positive evidence for arbitrary B.

## Next 5+

Continue:
- V15 evidence-linked experiments;
- V16 validated ClaimSupport + persona-scoped history/novelty;
- V17 receipt-backed persona-scoped community memory;
- V20-002 typed accepted-evidence growth inputs.

Do not edit Core state/decision/reasoning/leasing/worker.

## Heartbeat / lead coordination

Read `social-bots/HEARTBEAT_ASSIGNMENT_PROTOCOL.md`.

This lane starts in `BOOTSTRAP_15M` mode.

While this Claude session is active:
- check in every 15 minutes for the bootstrap phase, even if the current artifact has not finished;
- after each parent-artifact submission or blocker, check in immediately instead of waiting;
- after 3 consecutive approximately-15-minute heartbeats, REMAIN on 15-minute cadence until `social-bots/worker-reports/intelligence-repair/LEAD_ACK.json` says `steady_hourly_authorized=true`;
- once authorized, switch to hourly check-ins;
- do not exit merely because one artifact finished: pull instructions and take the next dependency-ready assignment unless blocked or explicitly told to stop.

For every heartbeat:
1. pull/fetch your branch;
2. re-read this SESSION_INSTRUCTIONS file;
3. inspect `social-bots/worker-reports/intelligence-repair/LEAD_ACK.json`;
4. run the heartbeat helper;
5. append the generated record to `social-bots/worker-reports/intelligence-repair/HEARTBEAT_LOG.jsonl`;
6. commit and push the heartbeat files;
7. set a notification reason for any new submission, blocker, completed artifact, changed assignment, or important finding.

Use:
`social-bots/bin/worker_heartbeat.py`

The heartbeat is a GitHub coordination signal, not proof of artifact correctness.

If the lead updates this file between heartbeats, follow the newest pulled version.



Path:
`social-bots/worker-reports/intelligence-repair/HEARTBEAT.json`

State-transition pushes only.

## Safety

No public effects, account login unless separately authorized, network scanning, paid APIs/new spend, secrets, fake metrics/evidence or SwarmAI dependency.
