# Social Bots session start — LEAD-047

Canonical coordination: `chatgpt/social-bots-plan-20260920`.

Current execution: **`social-bots/delivery/FINAL_RUN.md`**. Read it from the freshly fetched canonical ref; older local pause instructions are superseded by this release, not by guessing a branch head.

Read only root CLAUDE.md, compact state/CURRENT.md, your assignment and the active delivery/SB artifact card. Do not preload every roadmap. Use historical conversation/memory only when available and relevant; verify current status against Git.

Fable is the primary shared-runtime integrator. Cursor/legacy implementation is parked at a safe handoff; preserve incoming local/just-pushed code. QA is independent review-only. The lead still owns acceptance. Existing SB milestone requirements remain; Cxx delivery cards are integration/verification support, not replacement features. Old NR cards are supporting reference, not a second execution queue.

One fresh session emits one durable SESSION_ONCE heartbeat after current coordination is read. A resumed session does not duplicate it. Native scheduled invocation and task lease renewal are different things. No kept-open chat or periodic heartbeat watcher is required.

Implementation target: integrated, genuinely working V2.3 first, then V3.0. Current official version remains V0.4.x. No extra live product-model/public/spend authority is granted. See delivery/OWNER_GATES.md for the preserved necessary account/alias setup allowance and separate external gates.
