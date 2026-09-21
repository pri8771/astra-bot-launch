# SESSION_INSTRUCTIONS — Mac QA / Integration Control

Mode: ACTIVE — FAST TRACK
Branch: `claude/social-bots-mac-qa-control`

Heartbeat is background observability. Do not pause QA/integration work waiting for heartbeat acceptance.

## Existing accepted work
- SB-CTL-012 artifact validator: accepted.
- SB-CTL-006 GitHub CI/control: accepted.

Preserve those.

## Current work

### 1. Heartbeat proof — background
Continue real prospective ~15-minute heartbeat entries when due.
Do not burst/backfill.
Heartbeat does not block other work.

### 2. Integration acceptance preparation
Continue improving the non-runtime V2 acceptance harness and integration checklist:
- merge-order checklist for Core + Intelligence;
- CI commands;
- traceability assertions;
- persona isolation assertions;
- missing/stale/authority/no-public-effect scenarios;
- fixture-vs-operational evidence distinction.

Do NOT edit Core/Intelligence runtime source.

### 3. Audit assistance
When Core/Intelligence push new submissions:
- run branch-compatible validator/tests where possible;
- document failures with file/symbol/scenario;
- do not self-accept artifacts.

## V0.4 canary
You no longer own the live canary.
Dedicated local lane:
`claude/social-bots-v04-live-canary`

Do not switch this QA branch to the canary branch automatically.

## Heartbeat
Continue the existing bootstrap proof until lead authorizes hourly, but do not stop useful QA work between check-ins.

## Safety
No runtime feature implementation, public/account effects, paid API/new spend, secrets, fake evidence, or SwarmAI dependency.
