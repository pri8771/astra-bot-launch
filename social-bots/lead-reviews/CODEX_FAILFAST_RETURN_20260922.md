# LEAD-067 fail-fast return — 2026-09-22

READY_FOR_LEAD_REVIEW. PR19 https://github.com/pri8771/astra-bot-launch/pull/19

Source `f65bf96` on accepted PR18 `d8a211fc32802c59b07b1739bef47f9c551ed8dc`; exact tree `735a2c59fc5557cb15bbd1adfe84222e6264b049`. Separate isolated branch `codex/bots-failfast-20260922`.

Only execute_batch and a focused offline regression file changed. Append each result, then stop immediately on any outcome other than proposal_received. The failed slot remains consumed with its true outcome; no subsequent case context/reservation/provider invocation occurs. Stopped batches include case, outcome and unattempted_cases. Successful five-result reports remain unchanged. Scope is restored in finally. No retry, authorization, LOCAL binding or CallBudget changes.

Independent exact-tree review: RECOMMEND_ACCEPT, no findings. Formal acceptance remains ChatGPT's.

Validation: baseline 4 failing regressions plus 1 successful control; repaired 5/5 pass. Real authorize/reserved/deep-dispatch/durable budget paths use temporary fixture grants/source identity and an in-process provider sentinel only. First unavailable/exception/invalid case consumes exactly1slot; middle exception consumes3; valid consumes5. Full suite789tests2existing live skipsOK. New-test Ruff/format and diff checks clean. Hosted exact-head CI pending readback.

No real model/HTTP/account/scheduler/public action. The Mac and accepted Ollama adapter remain prepared, not live-tested. Source suitability, final matrix and exact five-call grant remain separate gates. Retry/backoff remains held.
