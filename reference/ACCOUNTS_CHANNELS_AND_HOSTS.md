# BOTS accounts, audience measurement and execution hosts

Owner decision, 12 September 2026. This extends the OPO mission and shared bot operating policy. It is a plan and requested capability contract, not evidence of created accounts, public posts or a Windows migration.

Latest host correction: **R730 is the central hub for Kai/local bots, Windows fallback, and the i9 Mac low-priority staging/secondary fallback only when useful now.** This supersedes older host-preference text below; no migration is claimed. Current owner-direction and focused plans: `../kai-pri-lipi-focus-2026-09-12/`.

## Latest authority

Bots may identify useful platforms, request missing resources and create or reuse accounts where appropriate. The owner delegates routine account/credential organization; reuse this authorization rather than asking for general permission again. A platform-specific owner verification, required consent or unsupported integration remains an actual prerequisite. Do not invent identities or bypass a service's registration requirements. Existing budget limits remain; no paid subscription or broader access is inferred merely from account-creation authority.

One Person Ops retains its agent-facing revenue website. Audience experiments now optimize cumulative followers and post exposure across suitable internet/social channels, not X alone. AI/bot participation remains the preferred OPO audience based on the previous instruction; human and unknown audiences are reported separately when evidence permits. Other missions can choose additional channels toward their own business goals. This does not turn every money-making website into a follower-only challenge.

## Accounts and resource requests

Maintain one owner-controlled account registry with separate entries for each mission and platform: resource ID/URL, purpose, owner, public identity, account type, permitted capabilities, credential reference, recovery owner, cost/limit, verified access date and lifecycle status. The registry contains secret references, never passwords, tokens or recovery codes.

Prefer shared administrative ownership, billing and reusable adapters; separate brand identities, private data, audiences and per-service permissions. Workers receive narrowly scoped credentials through the host's secure credential facility. Do not give every bot the owner's personal password or a fleet-wide master key. Session browser profiles remain distinct where account isolation requires it.

When something is missing, check the registry first. Persist one needs_input record stating exactly what is needed, why, what can be reused, cost/access implications if any, and the owner's next step. Examples: confirm the domain, connect the existing GitHub organization, complete an email verification or establish payment eligibility. Ask through the authorized channel; pause only the dependent action; resume after validated input. Never ask the owner to paste secrets into Jira/chat/docs. Use the existing deduplication contract in AUTONOMOUS_EXPERIMENTS.md.

OPO likely needs a repository, public host/domain, durable message storage, recoverable brand email, analytics access and selected channel identities. Merchant setup follows a concrete offer. Existing handles, repo ownership, hosting access and email control must be inspected before creating duplicates. The pending full 'shivangchordia' domain question remains pending, not reissued here.

## Channel choice

| Surface | Candidate job | Execution condition |
|---|---|---|
| Website and documented API | Agent discovery, communication, service delivery, monetization | Public endpoint and durable records verified |
| GitHub | Source, documentation, releases, issues/discussions and agent integrations | Reuse owner/org repository and scoped app; preserve existing work |
| X | Existing identity, short findings and agent referrals | Verified supported publishing/analytics route; current reply rules apply |
| Substack | Longer experiment reports and an opt-in returning audience | Verified brand publication, delivery and measurement route |
| LinkedIn | Reach relevant builders/operators through a brand Page | Eligible owner/admin account and supported route; no invented personal bot persona |
| Other communities/social services | A bounded experiment with a stated audience hypothesis | Actual audience fit, allowed integration and a measurable result |

Select channels by expected audience benefit, operating cost and evidence. Launch a small measurable set, then expand when a useful experiment justifies it; do not require all platforms before the website can launch. Adapt the format to the venue: documented JSON for service messages, readable summaries for discovery. Avoid sending the same output indiscriminately everywhere.

GitHub Apps can act independently with selected-repository permissions. GitHub's machine-user guidance explicitly says automated user-account registration is not allowed. The default should therefore be a repository under existing ownership plus an app, not bots manufacturing GitHub logins. Substack supports multiple publications and contributor roles under owner control; that does not by itself establish an automated publishing API. LinkedIn prohibits software that automates its website: qualify an allowed API/integration or use a prepared manual publishing step. Website automation is not the fallback for an unsupported route.

## Audience experiment scorecard

Freeze the start/end window, included accounts, baseline, collection route and metric definitions before the test. Platform additions are dated amendments with their own entry baseline. Report:

- Ending follower count and net change per platform. Sum comparable follower counts into **gross cross-platform follows**, explicitly not unique people or verified AI agents.
- Newsletter subscribers and other memberships separately by default. If a combined audience-subscription total is wanted, declare its components before the test; do not mix stars, likes, impressions and followers into it.
- Impressions/views per post and platform over the experiment window, with platform definitions and data coverage. Report unique reach only where supplied; do not add per-post unique counts and label the result unique humans. Email opens are an imperfect proxy and stay separate.
- Claimed/evidence-backed agent participation, human/unknown traffic where available, actual conversations, returning use, referrals and verified revenue.
- Content versions, time, model/tool usage and observed costs. Missing metrics are unknown, not zero. Our own tests and workers are excluded from external-adoption claims.

Every outgoing action and actually received response ties to its channel ID, experiment, source/permalink, timestamps and delivery state. Platform analytics are aggregate observations, not proof of which individual saw a post. Preserve the original baseline even if a tactic or channel changes.

## Execution placement

Windows is the requested primary execution host. The mobile Mac is backup and interactive control. The Intel i9/64GB Mac is a candidate always-on secondary host, pending qualification. A mobile Mac connection must not be required to keep a Windows job running.

Use one durable job queue and authoritative action ledger, with independent local repository clones/worktrees per host. Share versioned artifacts through Git and explicit transfer; do not have Windows/macOS concurrently modify one network-mounted working tree. Inject required credentials on each host through a secure host-local facility; do not copy entire browser profiles or credential files.

One active operator per mission owns external writes. Host leases/heartbeats, action IDs and destination readback prevent duplicate publication or Jira writes. A disconnected primary's uncertain actions must be reconciled before backup promotion; a timed-out heartbeat alone does not establish that the primary stopped. Failover must fence the old owner, preserve results and retain exactly one Jira writer. Do not expand consumed launch/model allowances by migrating.

Migration acceptance: validate Windows runtime/auth on a bounded task; persist the result; recover after a process restart; test a Mac-disconnected interval; test controlled takeover without duplicate effects. UI-only jobs also require a usable local desktop session. Connection via TeamViewer from the Mac proves remote control, not independent scheduling or autonomous failover. No migration is complete until these checks pass.

## Research sources checked 12 September 2026

- [GitHub Apps](https://docs.github.com/en/apps/creating-github-apps/about-creating-github-apps/about-creating-github-apps)
- [GitHub machine-user registration constraints](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys)
- [Substack publications](https://support.substack.com/hc/en-us/articles/360037824371-Can-I-create-multiple-publications-under-the-same-account)
- [Substack team roles](https://support.substack.com/hc/en-us/articles/360039016832-Can-my-Substack-publication-have-multiple-authors-or-contributors)
- [LinkedIn automated activity](https://www.linkedin.com/help/linkedin/answer/a1340567/automated-activity-on-linkedin?lang=en)
