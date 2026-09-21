# Lane 3 — Environment & Heartbeat Truthfulness Note

This lane was assigned as "Actual local Mac with working Claude Code subscription
authentication" running a 24-hour `gh`-backed heartbeat reporter. The actual
execution host differs from that premise. This note records the real state
truthfully rather than fabricating a heartbeat or a Mac run. No evidence in this
lane is faked.

## Actual host

- Platform: **Linux** (`Linux vm 6.18.44-fc-v37 x86_64`), a remote/ephemeral CCR
  container — **not** a macOS host.
- Working dir: `/home/user/astra-bot-launch`; the repo was cloned fresh; the
  container is reclaimed after inactivity, so long-lived background processes do
  not survive.
- `python3` 3.11.15; `claude` CLI 2.1.278 present and usable; `ANTHROPIC_API_KEY`
  absent (verified boolean only).

## Heartbeat reporter — NOT started (and why)

The assignment's heartbeat step could not be run as specified, and it was **not**
faked:

1. **`gh` is not installed** on this host (`command -v gh` → not found). The
   `heartbeat_reporter.py` design and the `gh auth status` verify step both depend
   on the GitHub CLI. GitHub access in this session is via the GitHub **MCP**
   tools, not `gh`.
2. **No durable 24h background process.** A `nohup … &` reporter cannot post
   every 15 min for 24h from an ephemeral session container that is reclaimed on
   inactivity; starting one would produce a reporter that dies silently — worse
   than not starting it.
3. Per the packet/session rules, **heartbeat is observability only and must not
   block or delay Mission A/B**, and only **real timed records** may be pushed
   (no backfill). Since no real timed heartbeat stream is possible here, none was
   fabricated.

**Net effect:** Missions A and B were completed and evidenced regardless, exactly
as the protocol allows ("Heartbeat does not block Mission A/B"). Private Issue #3
was not posted to from this host because that requires the `gh`-based reporter; if
the operator wants live Issue #3 visibility, run the reporter from the intended
Mac host, or ask this session to post a one-shot status via the GitHub MCP tools.

## Git delivery

Authorized session branch: **`claude/social-bots-mac-qa-lane3-ordpt6`**. Session
git policy pins pushes to this branch, so the Mission A report (intended for
`claude/social-bots-mac-qa-control`) and the Mission B canary evidence/report
(intended for `claude/social-bots-v04-live-canary`) are delivered here. The
lead/operator can fast-forward, cherry-pick, or merge them onto the control and
canary branches; all content is branch-location independent.

## Safety posture (honored)

No Core runtime edits. No public posts/replies/messages. No API/PAYG/new spend
(the canary used the subscription route with `ANTHROPIC_API_KEY` absent). No
purchases. No secrets committed. No fabricated evidence. No destructive actions.
No SwarmAI dependency.
