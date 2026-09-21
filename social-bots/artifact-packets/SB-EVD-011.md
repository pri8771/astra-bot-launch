# Artifact packet — SB-EVD-011

Artifact: Persona B canary publication/readback/analytics packet  
Milestone: V0.9  
Owner: Claude-Canary  
Story points: 3  
Planned status: BLOCKED

## Purpose

Execute exactly one owner-authorized bounded real public canary for social-b, verify exact destination/permalink/readback and open a real analytics observation window.

## Dependencies

- SB-ACC-001
- SB-ACC-007

## Required implementation / evidence

- Preserve Social Bots independence from SwarmAI.
- Reuse existing runtime, evidence, analytics, policy and artifact contracts before creating parallel infrastructure.
- Keep deterministic policy in charge of authority, effects, deduplication, scheduling, verification and stop conditions.
- Keep persona-private state structurally isolated; any cross-persona/admin surface must be explicit and auditable.
- Record attributable inputs, outputs, code/config refs, timestamps and limitations appropriate to this artifact.
- Add focused success, failure and adversarial tests; include at least one test that proves the artifact fails closed at its most important trust/authority boundary.
- Do not silently retry operational/model/public actions until they pass; preserve first-attempt truth and explicit retry authorization when applicable.
- Operational acceptance requires the exact explicitly authorized public effect plus external readback/permalink/analytics evidence. Fixtures or request-success alone do not count.

## Acceptance

- All declared dependencies are accepted or the packet remains blocked.
- The artifact's purpose is demonstrated by source/tests/evidence rather than documentation alone.
- Failure/uncertain paths cannot produce a stronger authority/effect than the success path permits.
- Exact source SHA/ref, commands/tests, evidence refs and known limits are returned.
- No credentials/secrets are committed.
- No unauthorized public effect, paid/PAYG fallback, destructive action or engagement manipulation occurs.
- Worker may request SUBMITTED; only ChatGPT lead may mark ACCEPTED.

## Return contract

Return:
- artifact ID: SB-EVD-011;
- exact resulting SHA/ref;
- focused/full test commands and results;
- evidence locations;
- operational-vs-fixture classification;
- limitations/blockers;
- requested status (normally SUBMITTED).
