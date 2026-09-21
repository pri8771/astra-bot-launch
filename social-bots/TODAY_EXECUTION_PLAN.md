# Social Bots — today execution plan

Date: 2026-09-20

## Objective

Reach a truthful **launch-ready autonomous system** today: three independent bot runtimes that can observe, think, choose experiments, produce platform-ready work, learn from evidence, persist state, recover from interruption and hand work between Claude Code and ChatGPT without overlap.

External actions that still require owner authorization, MFA/CAPTCHA/consent or platform approval remain explicit gates. Completion today must not be faked by mock accounts, fabricated metrics or unverified timers.

## What "complete today" means

By the end of this execution sequence:

1. Three bot runtimes exist as separate logical agents with separate mission state, memory, experiment ledgers and leases.
2. The three general social personas have versioned persona specs, voice constraints, audience hypotheses and success metrics.
3. The two Indian religious/cultural persona workspaces from the later Primandir plan remain preserved and usable as isolated persona surfaces on the same three-runtime infrastructure; Guru assets may seed research, not dictate identity.
4. Existing emails/accounts/assets are inventoried and classified as verified reusable, historical, blocked or irrelevant. No credential values enter Git.
5. Each relevant platform has a supported setup path documented for TikTok, Reddit, X, Instagram and Facebook. Actual login/profile/workspace verification is recorded only when observed.
6. A platform-independent content/experiment pipeline works end-to-end using real current research inputs and real generated candidates, with publishing disabled unless specifically authorized.
7. Analytics/event schema separates persona, platform, experiment, content item, external ID and observation window.
8. Each bot runs the autonomy loop in `AUTONOMY_CONTRACT.md` and records why it chose an action.
9. A no-overlap Claude worker is established on an authorized existing host with a lease/lock, resumable state, heartbeat file, invocation receipts and no-additional-spend limits.
10. ChatGPT's hourly lead heartbeat reviews actual GitHub evidence, updates state/queue/messages and gives the next bounded assignment.
11. At least one real, non-mock dry-run cycle per general persona reaches: observe -> reason -> candidate -> independent checks -> experiment plan -> persisted learning. "Dry-run" means no external publish side effect, not fabricated input.
12. Account/login blockers are reduced to the exact human step required. After password/passkey/MFA/CAPTCHA/consent, the worker resumes the intended destination rather than restarting discovery.

## Runtime vs account strategy

A bot process is not an account.

**Preferred:** share backend/admin infrastructure while keeping public persona profiles distinct when the platform supports it and doing so costs nothing. This gives cleaner analytics and stronger identity separation.

**Acceptable bootstrap:** an umbrella public account may host multiple clearly named AI-managed characters/series, with persona tags and separate analytics attribution. It must not pretend to be three unrelated humans.

Do not create duplicate accounts merely for architectural neatness. Reuse existing verified emails/account aliases/profile infrastructure first.

## Execution sequence

### Gate 0 — reconcile evidence, do not rebuild
Claude reads this directory plus the current authoritative files in `pri8771/bots` and the verified product homes. Build `SOURCE_REUSE_MAP.md` from current evidence. Historical September 1/12 claims are not current unless reverified.

Acceptance:
- every reused asset has repo/ref/path or external account alias + last verification;
- every historical claim is labeled;
- no secrets copied.

### Gate 1 — establish the control loop
Implement or reuse a small deterministic worker/supervisor that:
- claims one task with an atomic lease;
- refuses overlapping active leases;
- writes start/finish/failure receipts;
- refreshes heartbeat while alive;
- resumes safe work after restart;
- never treats a scheduled entry as proof of a running worker.

Acceptance:
- two actual invocation receipts;
- stale-lock recovery test;
- concurrent second worker is rejected;
- state survives restart.

### Gate 2 — persona workspaces
Create versioned specs for the 3 general personas and preserved specs/placeholders for the 2 cultural personas. Each gets:
- purpose and audience;
- distinctive voice boundaries;
- allowed/disallowed behavior;
- platform fit assumptions;
- success metric hierarchy;
- memory namespace;
- experiment namespace;
- content history/dedup key;
- correction policy.

Do not fabricate backstories or claim a human identity.

### Gate 3 — autonomous thinking engine
For each active bot implement:
1. OBSERVE changed evidence only.
2. ORIENT: summarize what changed and confidence.
3. GENERATE candidate actions/experiments.
4. SCORE by expected learning/value, relevance, risk, cost, reversibility and confidence.
5. CHOOSE one bounded next action.
6. EXECUTE only if within current authority.
7. VERIFY the external or local effect.
8. LEARN: write outcome and update hypotheses.
9. SCHEDULE the next evidence check deterministically.

Acceptance:
- reason record includes alternatives considered;
- unchanged evidence can produce "no action" without an LLM call where practical;
- retries are bounded;
- uncertain external effects are reconciled before retry;
- no bot can alter another persona's memory without an explicit shared record.

### Gate 4 — real account/browser inventory
Browser-first. Reuse existing accounts/emails before proposing new ones.

Record for each platform/persona:
- account alias, not private identity;
- login method;
- correct profile/workspace;
- supported automation/API/browser route;
- analytics route;
- publish/reply/DM capability;
- last actual verification;
- exact blocker and required human step;
- private credential reference location, never value.

No public posting is performed under this plan unless separately authorized.

### Gate 5 — research/content/experiment pipeline
Build reusable adapters for:
- current-topic research;
- source capture;
- persona-specific ideation;
- draft generation;
- factual/cultural review where applicable;
- asset requirements;
- platform formatting;
- experiment registration;
- duplicate detection;
- publish queue;
- observation/analytics ingestion.

Prefer existing libraries/APIs/scripts. Do not build a new model gateway if the existing project stack or a proven provider path already handles inference.

### Gate 6 — end-to-end proof
For each of the three general personas, run one real dry-run:
- retrieve current non-sensitive research inputs;
- choose a topic autonomously;
- produce one candidate per relevant platform class;
- record experiment hypothesis and success/stop criteria;
- run factual/policy/voice checks;
- produce a publish-ready packet;
- persist learning and next check.

Cultural persona dry-runs require appropriate source/cultural review.

### Gate 7 — launch gates
Prepare, but do not bypass:
- account verification/MFA;
- explicit public-posting authorization;
- platform policy restrictions;
- any requested new spend.

When a gate is cleared, publish one canary per persona, verify the exact permalink/account, observe the declared window, then let the bot make the next evidence-based decision.

## Reuse priorities

1. `pri8771/bots`: memory conventions, agent-side shared utilities, prior scheduling/lease lessons.
2. `Wait How Big`: social research/editorial/publishing patterns where current.
3. `Guru`: cultural/religious reference material and review lessons.
4. OPO/CommerceLint/BidetFit: existing account aliases, email infrastructure, analytics/publishing utilities and operating patterns where actually reusable.
5. SwarmAI: future proven components only behind an adapter boundary; no dependency on V3 and no forked swarm runtime.

## Done is evidence

Every material change records:
What / Why / Evidence / Expected result / Limits / Actual result / Next.

A content draft is not a post. A cron entry is not a worker. A 200 response is not account correctness. A generated metric is not an audience result.
