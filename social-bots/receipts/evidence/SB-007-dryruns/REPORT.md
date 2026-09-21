# SB-007 dry-run report

Real current research inputs, real autonomous decisions, real persisted state, **no external publication**.

## social-a — decision: CREATE_CANDIDATE -> outcome: **withheld** (PASS)
- **Observe:** 1 unconsumed of 1 total; changed = True
- **Orient:** 1 unconsumed signal(s); deciding on the oldest this cycle
- **Alternatives considered:** CREATE_CANDIDATE(2.25), RESEARCH_MORE(1.36), NO_ACTION(0.745)
- **Decision reason:** highest net score 2.25 from baseline-deterministic-v1 (baseline); clears authority and reversibility bar
- **Withheld:** gate stopped the candidate; within_platform_limit=None; no experiment/queue entry (correct fail-closed behavior).
- **Learning:** no hypothesis registered; a withheld candidate is not evidence of a launch
- **Next observation:** in 6h (deterministic timer + new-signal event)

## social-b — decision: CREATE_CANDIDATE -> outcome: **candidate_created** (PASS)
- **Observe:** 1 unconsumed of 1 total; changed = True
- **Orient:** 1 unconsumed signal(s); deciding on the oldest this cycle
- **Alternatives considered:** CREATE_CANDIDATE(2.25), RESEARCH_MORE(1.36), NO_ACTION(0.745)
- **Decision reason:** highest net score 2.25 from baseline-deterministic-v1 (baseline); clears authority and reversibility bar
- **Candidate:** instagram | published=False | authorized=False
    - preview: [Tidepool] Ordinary sunlight turned into a source of quantum entanglement

Angle (everyday-object-as-hook): Scientists turned ordinary sunlight into a source of quantum entanglemen
- **Experiment:** exp-c-8b1d40a963fd — metric `shares`, window 48h
    - hypothesis: Sensory, non-alarmist science earns shares from people who rarely share 'science'.
- **Learning:** hypothesis registered; confidence updates only after real post-window evidence
- **Next observation:** in 6h (deterministic timer + new-signal event)

## social-c — decision: CREATE_CANDIDATE -> outcome: **candidate_created** (PASS)
- **Observe:** 1 unconsumed of 1 total; changed = True
- **Orient:** 1 unconsumed signal(s); deciding on the oldest this cycle
- **Alternatives considered:** CREATE_CANDIDATE(2.25), RESEARCH_MORE(1.36), NO_ACTION(0.745)
- **Decision reason:** highest net score 2.25 from baseline-deterministic-v1 (baseline); clears authority and reversibility bar
- **Candidate:** tiktok | published=False | authorized=False
    - preview: [Switchboard] 2026 feeds split: maximalist-playful vs stripped-down-unproduced

Angle (hot-take-then-caveat): Sept 2026 platforms reward creator-led, authentic, lower-follower voic
- **Experiment:** exp-c-999530ca5437 — metric `early-engagement-velocity`, window 48h
    - hypothesis: A distinct comedic voice with a real point of view retains better than trend-chasing alone.
- **Learning:** hypothesis registered; confidence updates only after real post-window evidence
- **Next observation:** in 6h (deterministic timer + new-signal event)

## cultural-primandir-atman (cultural) — review gate
- review_passed = False (expected False)
- cultural status = **WITHHELD** — no named cultural reviewer and/or source; WITHHELD per contract
- gate held: PASS
