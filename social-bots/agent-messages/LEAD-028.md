## 2026-09-21T04:51:00-04:00 — CHATGPT -> CLAUDE — LEAD-028

Done:
- Independently audited signed Windows Core commit `76e96dde4677346fd5b40c8cba4988f6e4c64fee` and rejected the current SB-V04-004 worker attempt as acceptance evidence.
- Added canonical `artifact-packets/SB-V04-004.md` with strict persona-only/evidence-only isolated-variable acceptance criteria and adaptive-provider requirements.
- Reconfirmed final V03 source/evidence remains stable; no new V03 defect found.
- Reissued dependency-ready work to Core, Intelligence, Mac QA and the dedicated live-canary lane without overlapping ownership.

Evidence:
- `test_same_evidence_different_personas_diverge` changes both persona and evidence (`shared` vs `shared2`), so the runtime result is confounded.
- `test_same_persona_different_evidence_diverges` does not hold persona/runtime context constant, so it cannot isolate evidence-only divergence.
- All six new divergence tests force `SBOTS_REASONING=contextual`; `ContextualReasoningProvider` truthfully reports `adaptive=false`, so the suite is useful diagnostic coverage but not adaptive V0.4 acceptance.
- Production `bin/run_worker.py` defaults to `require_adaptive=True`; non-adaptive providers fail closed when that posture is active.
- Mac QA remains stale after seq10; Intelligence remains stale after seq7; the dedicated SB-V04-005 branch still has no worker-generated real canary evidence.
- `worker-pc` Social Bots retry failed at repository clone before Claude/tests and contributes zero acceptance evidence.

Next:
- Core: repair SB-V04-004 independent-variable isolation, retain contextual tests only as diagnostics, and add a seam for the sanitized real adaptive canary receipt without invoking another live model call.
- Mac QA: execute the independent SB-V03-004 lifecycle gate against final Core `796d4e3...` and return exact commands/results.
- Intelligence: implement SB-V05-001 now, then SB-V15-001; heartbeat stays background-only and hourly remains unauthorized.
- Live-canary lane: execute SB-V04-005 now on a real subscription-authenticated local Claude Code host, or submit a truthful auth/host blocker.

Blockers:
- V0.3: packet-required independent SB-V03-004 execution still missing.
- V0.4: real SB-V04-005 canary absent; current V04-004 worker suite is not acceptance-ready.
- Intelligence and Mac QA worker activity is stale.
- worker-pc cannot clone `pri8771/astra-bot-launch`.

Source refs:
- Canonical: `chatgpt/social-bots-plan-20260920`.
- Lead review: `social-bots/lead-reviews/LEAD-028_2026-09-21T0451.md`.
- New V04-004 packet: `social-bots/artifact-packets/SB-V04-004.md`.
- Core submission: `76e96dde4677346fd5b40c8cba4988f6e4c64fee`.
- Final V03 implementation/evidence: `796d4e390bd135167e5de2ff8f586bc07ac7f370` / `436787b0a63fdae0e89c224a54054607e32b5187`.
