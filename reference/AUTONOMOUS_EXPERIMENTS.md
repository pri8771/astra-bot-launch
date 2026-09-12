# BOTS autonomous experimentation contract

Updated 12 September 2026 after direct owner instruction. Owner wants bots to originate experiments, document them in Jira, execute within their business mission, observe results and decide the next move. Profile/design/content/channel/strategy changes are included. Posting and interaction should serve a business purpose. Cron is acceptable. This establishes the target behavior; the implementation and per-account runtime qualification are not complete. No jobs, schedules, Jira writes or external actions were started by this document.

Authoritative goal correction: [MISSION_GOALS.md](MISSION_GOALS.md). Product choices and first tests do not replace the original website-income or Twitter/social mission.

## Business ownership and autonomous decisions

Every mission has a versioned charter containing its original objective, target audience, business constraints, primary metric, available action capabilities, account/data boundaries, resource budget and stop controls. Each experiment must state how it advances that objective. The agent may change its tactics, design, profile image, content format, channel mix or strategy within that charter. Changing the business objective, exceeding a budget or making commitments outside its grant is a charter change. The latest owner grant allows organizing/creating/reusing appropriate platform accounts: apply ACCOUNTS_CHANNELS_AND_HOSTS.md and verify the actual route, identity and scope. Access outside that grant still requires a charter change. Prior authorizations remain valid; a qualified routine category does not need general approval again for every experiment.

Existing mission examples: CommerceLint preserves its adopted cash/business objective with qualified scanner engagement as supporting evidence; Wait, How Big? measures useful repeat audience attention; One Person Ops measures revenue and qualified outside-agent use plus its explicitly requested multi-platform follower/exposure experiment; Contract Check is an optional service; BidetFit distinguishes useful fit guidance from verified affiliate proceeds; Sadhana prioritizes trustworthy relevant content and its audience goal. A generic follower target must not displace every mission's original objective.

A bot should make a concise visible decision record: what it observed, its hypothesis, why it chose this experiment, a relevant alternative, expected outcome, actual result and next decision. This is a business rationale with evidence, not a continuous internal-monologue transcript.

## The operating loop

1. Observe new metrics, user feedback, delivery failures, changed sources or elapsed review windows through bounded approved inputs. Ordinary code collects and deduplicates observations.
2. Decide whether any evidence warrants a new proposal, evaluation, correction or no action. Invoke a model only when a reasoning decision is eligible. Lack of enough data usually enters waiting_for_evidence, without repeated model calls.
3. Propose an experiment with the original mission, hypothesis, baseline, comparison, planned intervention, success/stop criteria, budget and observation window. Compare options using a stated heuristic (likely business benefit, available evidence, cost/risk and reversibility); scores are estimates, not measured facts.
4. Register the plan before action. The bot owns the content; the designated Jira writer performs create/update and verified readback. Use a stable experiment ID to avoid duplicates. Persist a compact local ledger and outbox for restart recovery. Failure to establish the required Jira record blocks launch, rather than running an unrecorded experiment.
5. Validate capability, dependencies, account identity and budget. Acquire one experiment lease; bind the exact design/content/code version and original configuration for rollback. A previously observed uncertain effect is reconciled at its destination before retry.
6. Execute the admitted action, automatically within its qualified charter. Record the actual attempted action and verify the external or product result. A queued post, HTTP acceptance, live permalink and measured audience response are separate observations.
7. Observe until the predeclared window and evidence threshold are met, or a guardrail stops the experiment. Waiting is elapsed time, not agent work time. Record metrics with timestamps, denominators and collection failures; missing is not zero.
8. Evaluate as supported, not supported, inconclusive or invalidated. Separate observed change from the proposed explanation. Retain confounders, alternative explanations and limitations; do not claim causal proof from a simple before/after sample.
9. Decide continue, adopt, extend within remaining budget, revert or stop; propose the next experiment if justified. An extension or changed criterion is a dated amendment, never a retroactive rewrite. A failed experiment with trustworthy evidence can be complete work.
10. Publish the final evidence and attributable review through the writer. Promote a useful lesson only with scope/provenance and an appropriate review. Preserve the original experiment rather than overwriting it as the next one.

## Missing inputs are part of autonomous operation

A bot must ask for genuinely missing information rather than invent it or wait silently. Examples include the store URL to scan, intended publication account, source document, required audience, account connection, budget decision or a necessary business preference.

First check the mission registry, current experiment and authorized relevant records. Reuse a still-valid prior answer. If ambiguity remains, ask one concise question naming the missing item, why it is needed and the affected experiment. Request the least information sufficient; never request a password, access token or private credential pasted into chat.

Persist a needs_input entry with question ID, experiment/job ID, intended respondent, minimum required answer and next action. Ask through the appropriate authorized conversation. Pause only dependent actions and continue independent work when useful. Do not repeatedly rephrase or resend the same question on every scheduled check; notify again only on a material change or an agreed reminder rule.

Bind replies to the correct user, mission and question; validate the answer using the appropriate narrow capability. A supplied URL identifies a resource but does not automatically authorize unrelated data access or account actions. Save the useful answer with its source/access scope, clear the resolved blocker, recheck preconditions and resume from the checkpoint. Silence or timeout never supplies an answer or approval. Corrections to prior answers remain versioned evidence.

## Experiment integrity and evidence

Start with one primary experiment per mission. Concurrent independent tests are possible only when their audiences/surfaces do not contaminate each other and the capability permits it. Prefer randomized comparisons when traffic, platform support and practical conditions allow. Otherwise label the design as sequential/observational and state its limits. Changing photo, bio and content together is a bundled strategy test; it cannot establish which component caused a result.

Record baseline count/window, the primary business outcome, secondary measures and harm/quality guardrails before launch. Choose the minimum informative exposure from baseline/traffic and the hypothesis; do not invent a universal visitor count or significance level. A low-traffic avatar test may be less informative than a direct user observation. Qualitative feedback and small samples are useful but cannot establish population-wide effects.

Example: a profile-image experiment might hypothesize that a clearer original illustration increases qualified profile-to-follow conversion. It needs a saved old/new asset, stable surrounding content where feasible, measured profile visits/follows if genuinely accessible, and a stated observation window. If profile visits are unavailable, do not invent a conversion rate. Report a weaker proxy or choose a more measurable experiment.

Business scorecards must distinguish reach, relevant engagement, qualified users, useful outcomes, retention and actual money. OPO now explicitly measures cumulative followers and post exposure across platforms under ACCOUNTS_CHANNELS_AND_HOSTS.md: gross follows are not unique participants, and impressions are not unique people. Financial records retain refunds/fees where in scope; gross sales, pending affiliate balances and settled net proceeds are not interchangeable. Strategy responds to the declared goal and observed evidence without substituting a different metric after the test.

## Social interaction policy

Allowed target behavior: adapt tone, vocabulary, hooks, design and positioning to the audience; find truthful common ground; acknowledge good arguments; change a position when evidence warrants; answer relevant inbound questions; propose helpful participation when the platform and mission permit it. Account personas must remain consistent with their real disclosed identity and original charter.

Do not optimize through invented agreement, fabricated expertise/results/testimonials, fake followers, coordinated bot-to-bot engagement or indiscriminate replies. Such tactics undermine the evidence about real audience interest. Bots may share permissioned capabilities and public findings, not pretend to be independent customers endorsing one another.

Platform rules constrain the actual adapter. X's current official rules prohibit scripted website automation and unsolicited keyword-triggered reply campaigns. AI-powered automated reply bots require prior written explicit approval from X; recipient opt-in rules also apply. Until an account/route is qualified, research and reply drafts can proceed, but the automated reply is not enabled. This is a concrete platform prerequisite, not a new request for generic owner approval. Source: https://help.x.com/en/rules-and-policies/x-automation (checked 12 September 2026).

## Scheduling and token controls

Cron versus event-driven describes the trigger, not whether the bot makes decisions autonomously. Prefer webhooks/new-data events when available; a deterministic scheduled collector is an acceptable fallback. Proposed pilot defaults: one active experiment per mission, at most one bounded planning pass per day when new usable evidence/opportunity exists, and evaluation only when its window/threshold or exception makes it due. These are proposed defaults, not an installed schedule.

Persist next_check_at, observed-data version and decision fingerprint. A timer checks these cheaply before any model call; unchanged input and a not-yet-due decision cost no inference. Slow-changing businesses need appropriately sparse observation. Enforce job, mission and daily model/spend budgets, finite tool calls and a bounded repair. Insufficient quota stops/queues the work without paid fallback or reattempt storms.

Use existing deterministic validators and affordable local inference where quality has been demonstrated. Stronger reasoning/review is reserved for consequential strategy or correctness decisions that need it. Log actual model, effort, machine, tokens and provider counters when available. Shared author-session usage is recorded once; no invented allocation across tasks. Coordinator/subagent usage outside the ledger remains separately unknown.

## Jira and review contract

Use existing Task issues with a proposed `bot-experiment` label and an exact mission identity initially; a custom Experiment issue type is optional later. The live writer must validate types, labels, field contexts and existing matches. This document creates no new Jira fields or issues.

Native planning fields follow the existing project contract: human accountability, scope/components, story points and original estimate, estimated dates, ownership and dependencies before starting. Planned model/effort remain distinct from observed attempts. Actual start/end, work time, model changes, reviewer identity, machine and usage are recorded only after they are observed. Elapsed observation days are not fabricated worklogs.

The description contains the predeclared experiment. Linked implementation tasks bind real commits; subsequent execution and review comments contain dated evidence. Logical experiment states map to existing Jira workflow semantics, not an assumed new workflow. Research/observation can be complete with an inconclusive conclusion; Done requires its acceptance and distinct-model review evidence where mandated. A business result being disappointing does not automatically mean an engineering task failed.

The bot generates experiment content and follows its outcome; writer task `6046ab83-8402-47e3-b832-f4fe478da7f1` is the current designated Jira projection owner, subject to availability verification. Long-term a deterministic adapter can fill that role after qualification. It should not need a coordinator LLM to manually relay every experiment. Until then retain the single-writer queue and do not launch unrecorded experiments.

## First implementation slice

Latest priority is One Person Ops per OPO_AGENT_BUSINESS.md. Reconcile its baseline, mission charter and affected Jira specifications, then prove one experiment record -> execution receipt -> measured result -> independent assessment -> next decision. Start with discovery and a durable, attributable message exchange. Label synthetic clients as tests; verify real outside-agent participation separately and do not infer demand or revenue from a working endpoint. Contract Check is an optional utility, not the mission itself. The previous CommerceLint-first proposal is superseded. Do not expand all missions or increase existing service allowances merely by saving this policy.

After that slice works, reuse the same experiment record and adapters for the other mission charters. The objective is independent business decisions with traceable evidence and low idle cost.
