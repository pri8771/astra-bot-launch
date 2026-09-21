# SB-V04-005 sanitized adaptive-receipt intake

This directory is the **acceptance seam** for SB-V04-004. It is where the SB-V04-005
lane (Lane 3 live canary) drops the **sanitized** real adaptive reasoning receipt(s)
produced by the one authorized live subscription invocation.

## What belongs here

One or more `*.json` files, each a receipt validated by
`runtime.reasoning_receipt.validate_receipt`, with:

- `"receipt_kind": "sanitized-real-canary"`
- `"adaptive": true`
- `"provider_id"` identifying the real adaptive route (e.g. `claude-code-subscription-v1`)
- a bounded, inert `"context"` block and a matching `"context_digest"`
- `"alternatives"` whose numeric estimates are finite and in `[0, 1]`
- no authority keys anywhere, and no fabricated evidence refs

Receipts must be sanitized: no secrets, no credentials, no raw chain-of-thought,
no un-bounded free text — only the bounded proposal envelope.

## How the acceptance suite uses it

`tests/test_v04_divergence_acceptance.py` calls
`reasoning_receipt.load_real_canary_receipts()`. When real-canary receipts are
present here, the suite **replays them through the adaptive provider path**
(`ModelReasoningProvider`, `adaptive=True`) and asserts the persona-only /
evidence-only divergence and authority invariants against real adaptive output.

Until SB-V04-005 has run, this directory holds no real-canary receipt, and the
real-canary acceptance test **skips** with a clear "awaiting real canary" message.
The seam machinery itself is fully verified now against clearly-labeled
`synthetic-seam-fixture` receipts (never represented as the canary).

## Boundaries

- Core (Lane 1) does **not** create real receipts here — it only consumes them.
- A `synthetic-seam-fixture` receipt is never valid final-acceptance evidence.
- Nothing here grants authority: a receipt is inert replay data only.
