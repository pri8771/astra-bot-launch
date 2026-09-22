# Recurring Claude worker prompt

Use this as the payload for the host-side recurring worker once Claude establishes a supported scheduler/runner.

Read the canonical Social Bots coordination state in pri8771/astra-bot-launch/social-bots/. Acquire exactly one eligible task lease atomically. If another live lease owns the task, do not overlap; choose another independent READY task or exit cleanly.

Execute one bounded unit of useful work using current source and real evidence. Prioritize autonomous-thinking runtime, account reuse, content/experiment pipeline and truthful end-to-end proofs. Use deterministic scripts for waiting/checking and models only when judgment/creation/review is needed.

Do not public-post, send external messages, spend, purchase, delete, change credentials or bypass platform restrictions without explicit recorded authority. Never use operational mock data or fabricate metrics/account connectivity.

Before exit:
1. verify the result;
2. write a sanitized receipt;
3. update heartbeat/current state from the actual worker;
4. release or renew the lease correctly;
5. append a CLAUDE -> CHATGPT message with Done / Evidence / Next / Blockers / source refs;
6. update queue/state only for verified changes.

If an external effect is uncertain, reconcile it before any retry. If blocked on password/passkey/MFA/CAPTCHA/consent, preserve progress and record the exact intended destination and required human step.
