# Social Bots version roadmap

Authoritative product-version contract established 2026-09-20 by ChatGPT lead.

This roadmap describes the Social Bots project only. Social Bots is and must remain fully operational without SwarmAI. No milestone may depend on SwarmAI code, queues, services, memory, models, gateways, releases, or availability unless the owner later makes a separate explicit integration decision.

## Version model

- V0.x = build and prove the machine.
- V1.x = operate three autonomous social bots reliably in the real world.
- V2.x = turn operation into an autonomous growth system.
- V3.0 = operate as an autonomous multi-brand media organization.

Current lead-assigned version: **V0.3.x — runtime foundation under correctness repair.**
Immediate target: **V0.4 — real autonomous thinking.**
Near-term engineering target: **V0.7 — always-on Claude/ChatGPT development + bot-operation loop.**
First major product target: **V1.0 — three real autonomous social bots.**

Owner-selected strategic checkpoints:
- **V1.7** — autonomous operator with community intelligence.
- **V2.3** — growth strategist + goal decomposition + temporary specialist workers.
- **V3.0** — autonomous multi-brand media organization.

Current acceleration target:
- **V2.0 engineering-ready today** if implementation/review throughput permits.
- Operational V2.0 promotion remains evidence-gated and still requires real account/public/measurement evidence where the milestone contract requires it.
- Engineering readiness must never be reported as operational promotion.

## V0.x — build the machine

### V0.1 — Project/control foundation
Done when:
- canonical coordination home exists;
- ChatGPT lead / Claude implementation-worker roles are explicit;
- three-runtime scope, five persona-workspace scope and safety boundaries are documented;
- no conflicting coordination authority exists.

Status: DONE.

### V0.2 — Runtime/persona architecture
Done when:
- social-a, social-b and social-c are separate logical runtimes;
- three general personas exist;
- two cultural/Primandir persona workspaces exist;
- runtime identity is separated from public account identity;
- private persona state cannot silently contaminate another persona.

Status: DONE directionally; correctness regressions may reopen details.

### V0.3 — Durable runtime foundation
Done when:
- durable state/memory/experiments/content/analytics exist;
- receipts and process heartbeats exist;
- no-overlap leases are race-safe;
- restart/recovery and uncertain-effect reconciliation work;
- signal consumption cannot lose evidence;
- failed review cannot leak into experiment/publish queues;
- general/cultural workspaces cannot concurrently corrupt shared runtime state.

Status: CURRENT — foundation exists, SB-R0 correctness repair is required before acceptance.

### V0.4 — Real autonomous thinking
Done when:
- changed evidence is interpreted contextually;
- alternatives are generated from persona + objective + current evidence/state;
- estimates/reasons materially differ when the situation differs;
- bots may choose NO_ACTION;
- deterministic code owns safety, authority, no-change, dedup, scheduling and verification;
- uncertain interpretation/creative prioritization can use an available no-additional-spend reasoning model;
- if no reasoning model is available, the system fails closed to NO_ACTION/BLOCKED instead of pretending adaptive autonomy;
- no SwarmAI dependency exists.

### V0.5 — Real research + evidence layer
Done when:
- current information is acquired by an actual collector;
- capture receipts include source/URL, retrieval timestamp, status and content/response hash;
- provenance is created by the collector, not caller-declared;
- factual support is checked beyond URL existence;
- claims distinguish known / inferred / uncertain.

### V0.6 — Honest end-to-end dry runs
Done when each of the three general personas independently completes:
observe -> orient -> generate alternatives -> choose -> create -> factual/voice/platform review -> register experiment -> persist learning -> schedule next check,
using newly acquired current evidence, with:
- no publication side effect;
- all required checks passing;
- independent attributable review of final candidates;
- no mock operational evidence.

### V0.7 — Always-on development/operation loop
Done when:
- Claude worker is installed on an authorized existing always-on host at zero additional spend;
- worker wakes on supported schedule/event, claims one task safely, executes one bounded unit and exits;
- actual host-side heartbeat + invocation receipts prove recurring liveness;
- ChatGPT hourly lead review audits the receipts and assigns the next bounded work;
- Claude consumes new lead direction without owner manually relaying each task;
- crash/restart/no-overlap behavior is proven on the host.

### V0.8 — Real account connectivity
Done when:
- existing accounts/emails are reused before new account creation;
- exact X/Instagram/TikTok/Reddit/Facebook account/profile/workspace mappings are freshly verified;
- supported API/browser/manual routes are known;
- credentials remain outside Git;
- MFA/passkey/CAPTCHA/consent stops are reduced to exact owner actions;
- analytics collection routes are proven where available;
- public posting remains gated until separately authorized.

### V0.9 — Controlled live canaries
Done when, after explicit owner authorization:
- each general persona performs one bounded real public canary on an approved platform;
- exact account/persona/destination/permalink are verified;
- analytics/observation window are real;
- duplicate/correction/recovery controls work;
- the next decision uses real post-publication evidence.

### V1.0 — Autonomous Social Bots
Done when all three bots can continuously:
observe -> research -> reason -> choose -> create -> review -> act where authorized -> verify -> measure -> learn -> update memory -> decide next action -> recover,
on real social presences, while:
- remaining independent from SwarmAI;
- requiring the owner only for genuine authority/account gates;
- preserving truthful evidence and separate persona state.

## V1.x — reliable autonomous operation

### V1.1 — Reliability hardening
Long unattended runs, fault injection, idempotency, rollback/corrections, stale-worker recovery, account/API outage handling.

### V1.2 — Multi-platform intelligence
Bots decide which platform deserves an idea instead of blind cross-posting.

### V1.3 — Analytics brain
Unified content/experiment/audience analytics and comparable metrics across platforms without mixing incompatible measures.

### V1.4 — Audience memory
Evidence-backed audience models: topics, formats, timing, saves/shares/replies/follows and confidence/decay.

### V1.5 — Autonomous experiment engine
Bots define hypotheses, baselines, interventions, observation windows, success/stop criteria and close experiments honestly.

### V1.6 — Content intelligence
Platform-native hooks, series, media concepts, reuse/repurposing, novelty/dedup controls and quality feedback.

### V1.7 — Community operation
Safely observe comments/replies, identify useful conversations, respond where authorized and maintain community memory.

### V1.8 — Cultural personas operational
Both Indian religious/cultural personas have validated sourcing, named cultural review, community workflows and appropriate Primandir-adjacent learning without becoming disguised advertising.

### V1.9 — V1 stabilization
Long unattended acceptance runs, observability, account health, cost/resource controls, runbooks and no known supported-path defects.

## V2.x — autonomous growth system

### V2.0 — Autonomous Growth Engine
Bots not only operate; they change strategy from measured evidence to improve relevant audience growth.

### V2.1 — Dynamic strategy
Each bot maintains and revises an explicit strategy rather than static instructions.

### V2.2 — Goal decomposition
Bots translate high-level goals into their own bounded research/actions/experiments.

### V2.3 — Temporary specialist workers
Bots can invoke independent temporary researcher/analyst/writer/reviewer/media workers when useful. These are Social Bots components, not SwarmAI.

### V2.4 — Long-term learning
Months of experiment history become structured institutional memory with decay, contradictions, seasonality and failed hypotheses.

### V2.5 — Audience segmentation
Evidence-backed audience clusters and differentiated content strategy without deceptive personal profiling.

### V2.6 — Trend intelligence
Detect trends, estimate persona relevance, reject irrelevant virality and choose timely experiments.

### V2.7 — Cross-platform strategy
One idea becomes platform-native executions rather than copy/paste posts.

### V2.8 — Growth allocation
Allocate attention/time across platforms, formats and experiments by expected value, learning value and opportunity cost.

### V2.9 — Self-evaluation
Bots detect strategy drift, repetition, poor experiments and reliability problems, then propose bounded self-improvements for review.

## V3.0 — Autonomous multi-brand media organization

Done when the Social Bots system operates like a small autonomous media organization:
- multiple persistent brands/personas with separate strategies and durable memory;
- shared infrastructure only where sharing is beneficial and safe;
- temporary specialist workers created/retired as needed;
- portfolio-level analytics and learning;
- cross-brand shared facts without cross-persona identity contamination;
- independent editorial/growth strategies;
- bounded autonomous planning and execution;
- human intervention mainly for authority, identity, legal/policy and strategic-owner decisions;
- fully independent of SwarmAI.

## Promotion rule

Version promotion is evidence-based, not implementation-self-declared. ChatGPT lead accepts a version only after the acceptance evidence is inspectable. Passing unit tests, a scheduler entry, a draft, or a claimed run is not by itself a version milestone.
