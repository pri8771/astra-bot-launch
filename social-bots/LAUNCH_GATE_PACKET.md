# Launch gate packet (SB-008)

**Compiled:** 2026-09-20 by Claude Code. Prepares — does not bypass — every gate.
No public post, no spend, no account creation is performed by this packet.

A persona is **not** "launched" because a draft exists. Real launch acceptance
requires, per persona: correct account + correct persona + correct destination +
real external permalink/content id + analytics hookup + duplicate protection +
rollback/correction path + a declared observation window + actual post-publication
evidence. None of that is claimed here.

## Current readiness

- Runtime, autonomy loop, personas, pipeline, analytics, worker: **built + tested**
  (26 unittest cases green; SB-002 + SB-007 evidence runs pass).
- Publish queue holds reviewed, **unpublished, unauthorized** candidates only.
- Cultural personas: candidates **WITHHELD** by the review gate (correct).

## Each blocker reduced to one exact human action

| # | Gate | Exact human action | Owner? | Blocks |
|---|---|---|---|---|
| G1 | Recurring worker on always-on host | Deploy `bin/run_worker.py` as a recurring job on an authorized host (R730 or Windows) with a local credential facility; confirm two real invocation receipts + heartbeat from that host. | Owner | Continuous autonomy off-session |
| G2 | Account confirmation | Name the existing account/handle/Page per persona (reuse before create). | Owner | All publishing |
| G3 | Platform API authorization | Authorize: Reddit OAuth app; Meta app + review (IG/FB); TikTok dev app; decide X tier. | Owner | Publishing per platform |
| G4 | X write tier cost | Decide whether to use X write API (paid) or manual-assisted posting. **No new spend authorized.** | Owner | X publishing |
| G5 | Public-posting authorization | Grant explicit per-persona, per-platform posting authority (currently `posting_authorized=false`). | Owner | Any external post |
| G6 | Named cultural reviewer | Bind a named cultural reviewer + licensed/public-domain sources for the two cultural personas. | Owner | Cultural persona posting |

## Canary plan (prepared, not executed)

For the **three general personas**, once G1–G5 clear for one platform each:

1. Publish exactly **one** canary from the reviewed queue (`publish_authorized`
   flipped by the owner-authorized path only).
2. Verify the real permalink/content id, the correct account, and correct persona
   attribution (`analytics.emit(... "published", publication_id=<real id>)`).
3. Observe the declared window (48h) using the experiment's success/stop criteria.
4. Let the bot make the next evidence-based decision (LEARN updates the hypothesis
   from real post-window analytics, not before).

**Rollback/correction path:** each persona's `correction_behavior` is defined
(explicit correction, original stays visible, correction logged as a learning
event). Pre-publish rollback = delete the local queued draft; no external
permalink exists until G5 is cleared.

Cultural personas do **not** canary until G6 is satisfied.

## What ChatGPT (lead) should verify

Commits + receipts under `receipts/evidence/`, heartbeat freshness on the chosen
host (G1), test suite green, and that `STATE.json` `public_actions.posting_authorized`
remains `false` until the owner grants it. Claude does not mark its own work
accepted.
