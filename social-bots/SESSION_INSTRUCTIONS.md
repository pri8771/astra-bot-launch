# SESSION_INSTRUCTIONS — Intelligence / Evidence Integrity

Mode: ACTIVE — FAST TRACK
Branch: `claude/social-bots-intelligence-repair-v2`
Lead review: LEAD-024

Heartbeat is observability only. Do NOT run a foreground heartbeat-only loop that pauses implementation. Record a real heartbeat when due, push it, and continue source work.

## Coordination loop

At session start and after every parent artifact checkpoint:
1. `git pull --ff-only`
2. `git fetch origin`
3. read this file
4. read canonical `FAST_TRACK_EXECUTION.md` and `SESSION_ROUTER.md`
5. inspect `worker-reports/intelligence-repair/LEAD_ACK.json`
6. record heartbeat when genuinely due without fabricating/backfilling timestamps
7. continue dependency-ready implementation.

## Accepted and frozen
- `SB-V13-001` — ACCEPTED engineering artifact.
- `SB-V14-001` — ACCEPTED engineering artifact.

Do not restart those.

## Priority 1 — SB-V05-001 real HTTPS path repair — START SOURCE WORK NOW

No V05 source repair has been pushed since FAST TRACK activation. The last worker change visible at LEAD-024 is heartbeat sequence 7, not implementation.

Repair the LEAD-020 production-path defect now:
- actual socket connects to the already validated/pinned public IP;
- TLS SNI and certificate verification use the original hostname;
- no post-validation hostname re-resolution;
- correct Host header semantics;
- redirects remain fail-closed unless every hop is revalidated/re-pinned end to end;
- add a regression that exercises the real production HTTPS connection-construction path and would catch an invalid stdlib constructor/API signature;
- preserve the existing static/internal trust model, fixture-vs-operational distinction, extraction honesty, SSRF protections and operational bridge gating;
- do not claim fixture/stub evidence is a real external live capture.

Submit `SB-V05-001` with exact SHA/tests/limitations and continue directly to V15.

## Priority 2 — SB-V15-001 persona-scoped production experiment boundary

After V05-001 submission:
- add authoritative bot+persona production save/load/list/read APIs;
- normal persona-facing readers must never enumerate another persona's experiment;
- any bot-wide raw access must be explicitly admin/internal and not used by normal persona flows;
- add mixed-persona regressions through the real production API;
- preserve normalized-observation provenance, semantic compatibility and INCONCLUSIVE-on-missing behavior.

Submit `SB-V15-001`.

## Hold / later lead audit

Preserve current `SB-V16-001`, `SB-V17-001`, and `SB-V20-002` submissions. Do not expand V2.1/V2.2/V2.3 until V05/V15 are repaired and lead audit catches up.

`SB-V05-002` remains fail-closed pending accepted operational semantic-provider integration; do not build a second model gateway.

## Heartbeat — seq7 does NOT complete bootstrap

Durable timestamps are:
- seq5: 03:23:31Z
- seq6: 03:40:08Z (~16m37s)
- seq7: 04:10:36Z (~30m28s after seq6)

The seq7 worker note claiming completed 3x15-minute validation is NOT accepted. A ~30.5-minute interval is not approximately 15 minutes under this bootstrap test. `steady_hourly_authorized` remains false.

Do not backfill or rewrite history. Continue future real timed entries prospectively in the background. Heartbeat remains secondary to implementation.

Heartbeat proof is GitHub coordination liveness only, not V0.7 runtime liveness.

## Safety / ownership

Do not edit Core state/decision/reasoning/leasing/worker.
No public effects, account login unless separately authorized, network scanning, paid APIs/new spend, secrets, fake metrics/evidence, engagement manipulation or SwarmAI dependency.
