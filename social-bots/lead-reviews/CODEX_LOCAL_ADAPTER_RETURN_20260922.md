# LOCAL adapter and CI port — READY_FOR_LEAD_REVIEW

LEAD066 base: `fec97738ec0e9407415f60228f7c3938613396c3` / tree `43e80b92d8ae559db55a41ed33329695e6fd03fc`.

Candidate branch: `codex/bots-ollama-local-20260922`.
Adapter commit: `0365c8a`.
CI port / exact final head: `d8a211fc32802c59b07b1739bef47f9c551ed8dc`.
Tree: `169c386c471b813585e6f441d0be88fcf1ba0158`.
Draft PR18: https://github.com/pri8771/astra-bot-launch/pull/18

## Behavior and scope

The five-case batch can select `ollama-local` through its exact reviewed provider configuration. It binds canonical loopback endpoint `http://127.0.0.1:11434`, installed `qwen3.5:9b` digest `6488c96fa5faab64bb65cbd30d4289e20e6130ef535a93ef9a49f42eda893ea7`, generation options, prompt, timeout and response-size limit. It reads model metadata inside the authorized consumed attempt, then issues one non-streaming generation. No redirects, environment proxies, model pull, remote fallback, retries, tools or daemon control exist.

Local inference remains real model execution through the existing production dispatch/budget gate. The new `_LocalInvocation` exact policy-owned type prevents another callable from claiming LOCAL authority by spoofing its provider identifier. LOCAL results identify `ollama-local-v1`.

Only LEAD066's allowed production surface changed: authorization, divergence_prepare, model_dispatch, new reasoning_local, plus focused tests. Accepted PR15 is an ancestor of fec9773 (independent ancestry check passed). No accepted worker repair was dropped.

The CI port preserves the historical QA workflow's Python3.11, contents:read, no secrets, no schedules, baseline/adaptive-disabled tests and no publishing/deploy. Added candidate branch trigger `codex/bots-**`. The optional graph-validator script is absent on this lineage and is truthfully skipped; JSON parsing and the real unit suite execute.

## Validation and independent review

- Full stdlib suite: 784 tests, 2 existing skips, OK (4.289 seconds on local Python3.14). All inference/HTTP/subprocess provider paths in the new tests use mocks.
- LOCAL focused: 12 passed after settled formatting.
- New provider/tests Ruff and format: clean. `git diff --check`: clean.
- Hosted Python3.11 runs `35773234629` and `35773340055` both SUCCESS on exact d8a211f; latter job `106900212708`. Real unit-test step executed. No billing changes or paid runner added.
- No project-configured full mypy gate or PostgreSQL backend is asserted for this stdlib Bots change.
- Non-implementer recommendation: RECOMMEND_ACCEPT for LOCAL engineering, no remaining bounded-scope finding. Formal acceptance remains with ChatGPT.

Review found a concrete cross-route defect during implementation: a LOCAL manifest could still invoke Claude through the generic shared gate. Both root and independent reviewer reproduced it with a mocked CLI (zero external calls). Settled repair refuses actual Claude and a raw callable with a spoofed LOCAL ID, both before reservation and during adoption of an existing slot. Independent after-check: zero mocked CLI launches, zero new slots, no proposal.

Initial suite failures were a minimal authorization fixture missing the now-required provider-mode binding and a stale subscription-only error assertion; both were updated without weakening rejection of generic model routes. A temporary refactor NameError was corrected before settled tests. Failure evidence is retained locally under `/tmp/bots-local-*20260922*`; final source is clean and pushed.

## Remaining gates

The batch fail-fast defect is confirmed in separate b188f03 evidence and remains unrepaired pending its explicit narrow release. E1 replacement and deterministic E1/E2 extraction lineage remain required by LEAD066. No final acceptance matrix has been rebuilt. No real Ollama/Claude inference, download, daemon action, public effect, scheduler or live proof occurred. This engineering candidate does not clear those gates or promote the version.
