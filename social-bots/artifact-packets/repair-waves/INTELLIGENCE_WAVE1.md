
## Same-host concurrency rule

If multiple Claude sessions run simultaneously on the same Windows machine, they MUST NOT share one Git working tree.

Use separate local directories/clones (or carefully configured Git worktrees) per session. Recommended simple layout:
- Windows Core session: `astra-bot-launch-core`
- Intelligence session: `astra-bot-launch-intelligence`

Each session owns its own working directory and branch. Never let one session run `git switch`, merge, reset, clean, or checkout inside the other session's working tree.

Shared remote repository is fine; shared local working tree is not.

# Repair wave — Intelligence / Evidence Integrity

Worker instance: second Claude environment
Suggested branch: `claude/social-bots-intelligence-repair-v2`

## Order

### 1. SB-V05-001 trusted capture
- operational-live provenance may only be produced by collector-owned trusted transports;
- arbitrary custom Fetcher cannot create operational-live evidence;
- restrict live retrieval to validated public HTTP(S);
- reject loopback/private/link-local/multicast/reserved destinations;
- validate redirects/final destinations;
- add extraction_status; extraction failure cannot be used as extracted factual support.

### 2. SB-V05-002 factual support assessor
- caller does not get to assert operational stance=supports;
- add SupportAssessor protocol/provider result;
- bind claim -> evidence excerpt/span/hash -> assessor identity/version -> support status;
- fixture/manual stance remains explicitly fixture/test-only;
- no assessor operationally => UNKNOWN/WITHHELD.

### 3. SB-V13-001 metric semantics
Every raw/normalized metric declares one of:
- cumulative_snapshot
- delta
- gauge
- rate

Aggregation rules are semantic-aware.
Required regression:
- cumulative snapshots 100 then 150 != 250;
- explicit deltas 100 then 50 may sum to 150;
- snapshot-to-delta derivation requires comparable previous observation and records derivation.

### 4. SB-V14-001 persona-scoped audience memory
- Hypothesis carries bot + persona/workspace;
- persistence is persona scoped;
- safe segment dimensions use an allowlist, not sensitive-attribute blacklist;
- forked hypothesis does not treat contradiction of A as positive evidence for arbitrary B.

### 5. SB-V15-001 evidence-linked experiments
- baseline/treatment bind to normalized metric observation IDs/evidence refs;
- metric semantic/window compatibility validated;
- learning ref traces to measurements.

### 6. SB-V16-001 content intelligence
- fact Segment binding must resolve to acceptable ClaimSupportResult;
- content-intel history records persona/workspace;
- novelty search defaults persona scoped.

### 7. SB-V17-001 community
- operational read-only signal requires capture/platform receipt ref;
- memory/themes persona scoped;
- audience evidence includes persona/workspace.

### 8. SB-V20-002 typed growth inputs
- construct GrowthOpportunity from accepted metric/experiment/audience records;
- validate refs/freshness/persona scope;
- arbitrary numeric OpportunityInput is test-only;
- invalid/stale evidence => learning/no recommendation, never growth optimization.

## Reporting

One report per artifact under `worker-reports/intelligence-repair/`.
Do not edit Core files or canonical artifact state.
