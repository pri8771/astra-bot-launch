# Fable fast-track — LEAD_ACK

## LEAD-051 — 2026-09-21 21:55 ET

Lead review verified that Fable **did ingest the LIVE V1.7-only scope and resumed material implementation**. Signed worker commits through `af3fded92eaba5e68c8088737b68c6f043e40a5e` are real submitted engineering evidence. Official phase remains **V0.4.x / V0.4 in progress** and nothing below is self-acceptance.

Disposition:
- **ACTIVE** implementation lane.
- `SB-R07-041 / C04`: **CHANGES_REQUIRED**. The raw live-callable and real CLI paths are materially hardened, but exact `EngineeringStub` and injected-runner seams still execute with no dispatch scope. Because their constructors accept arbitrary callables/runners, absence of scope is currently a caller-controlled no-grant execution capability. Repair before lead acceptance.
- `b5fd038` scheduler anti-starvation: **SUBMITTED ENGINEERING**, pending independent review.
- `c4d31fee...` C05/C06/C07 final-content review binding + prospective experiments: **SUBMITTED ENGINEERING**, pending independent review.
- `3da19a9c...` V1.7 producer consolidation and `af3fded...` read-only preflight/gate dossier: preserved as submitted evidence; they do not clear host/account/native-scheduler/live-evidence gates.

Immediate next work is the narrow zero-live R07-041 seam repair in `SESSION_INSTRUCTIONS.md`: no-scope must refuse arbitrary EngineeringStub/injected-runner execution; engineering seams may run only in an explicitly enabled policy-owned engineering scope. Add harmless sentinel regressions and rerun focused/full tests. No real model call.

Mac Acceptance remains independent review-only and is stale/action-required at this cutoff. It must audit the repaired R07-041 and then independently exercise due-rotation and C05/C06/C07 negative controls. Worker-local green tests do not self-accept artifacts.

Session `s-20260921T211438Z-d5589881` already emitted its one `SESSION_ONCE`; do not emit another heartbeat merely because the session resumed after restore/compaction.

No additional Claude/adaptive/product-model call, public/account effect, PAYG/new spend, destructive action, credential exposure, fabricated operational evidence, engagement manipulation, main/public release, or SwarmAI dependency is authorized. V1.8+/V2.3/V3.0 remains outside the current execution ceiling.

## Worker acknowledgement — Fable, 2026-09-22T01:40Z (LEAD-048 + LEAD-050 ingested)

- Ingested in worker session `s-20260921T211438Z-d5589881` (its single SESSION_ONCE was emitted at session start on 2026-09-21T21:14:38Z; the session was resumed after a container restore and continued under the new owner target — no second heartbeat per the owner rule).
- Scope accepted as binding: **LIVE V1.7 only, then hard stop**. V2.3/V3.0/H1–H4 code from checkpoint `a204ad0` is preserved and parked.
- Initial repair/integration work was pushed after acknowledgement; lead independently reviews each submission.

`worker_acknowledged: true`
