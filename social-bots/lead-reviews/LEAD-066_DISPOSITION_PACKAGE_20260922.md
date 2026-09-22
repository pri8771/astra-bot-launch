# LEAD-066 disposition package

Official product remains **V0.4.x**. Owner target/hard stop is **accepted LIVE V1.7**. Codex owns newly released work; no Fable dispatch. ChatGPT remains formal acceptor.

## PR17
PR17 exact `da53159704e3e1dfefb8d7e4d2518fdc889317fb` / tree `32a7e6c18f2fea4e6f6f32b5d7ae65af56f18e6d`.

- Capture-package integrity: **ACCEPTED**.
- Final E1/E2 divergence-pair suitability: **REWORK_REQUIRED**.
- E2 TikTok (published 2026-09-14): retain, pending extraction/signal-lineage binding.
- E1 Meta (published 2026-06-04): replace for recency.
- Replacement E1: public Social Bots-domain source published within 30 days unless a later lead explicitly accepts otherwise; materially distinct from E2.
- Both final signals must be deterministically derived from frozen raw bytes with raw/receipt/extraction/signal digests and publication metadata.
- Final P0/P1/P2/P3/E0 rebuild remains blocked until lead approves the corrected pair.

## LOCAL provider engineering release
Worker: **Codex direct**. Independent recommendation role: **Codex-Acceptance-Review** (no implementation edits).

Base: accepted PR16 `fec97738ec0e9407415f60228f7c3938613396c3` / tree `43e80b92d8ae559db55a41ed33329695e6fd03fc`.

Allowed source:
- `runtime/authorization.py`
- `runtime/divergence_prepare.py`
- new `runtime/reasoning_local.py`
- `runtime/model_dispatch.py` only if required
- focused tests

Contract: distinct `ollama-local` provider, loopback-only `127.0.0.1:11434`, initial exact model `qwen3.5:9b`, exact endpoint/model/config included in execution binding, no remote/API/OpenRouter fallback, no model pull/download, no daemon change, five durable P0/P1/P2/P3/E0 attempts, no retries/no sixth attempt, no public/account/effect tools. **Adapter/tests only; no real inference authorized.**

## Fail-fast diagnostic
Codex may reproduce offline whether a failed/non-`proposal_received` case allows the next case to reserve/execute. No source edit until separate lead release. Intended rule if confirmed: first failed case stops batch; failed slot stays consumed; later slots remain unconsumed; no retry.

## SB-V07-001 prepare-only release
Dependency SB-V03-006 is accepted. Codex may prepare a Mac-first worker-once/host runbook and read-only preflight. This does not designate the Mac as the accepted persistent scheduler host. No scheduler install/firing, watcher or new SESSION_ONCE. SB-R07-073/074 remain PLANNED.

## Minimal CI port release
Codex may port the read-only `.github/workflows/social-bots-ci.yml` from historical `claude/social-bots-mac-qa-control` to an accepted-lineage candidate: Python 3.11, contents:read, no secrets, artifact validation + unit tests, adaptive/provider disabled, no deploy/publish/model effects, no auto-merge.

## Zero-spend platform bootstrap rule
The first three general personas may bootstrap on **three qualified routes**, not all five platforms. Each route needs fresh exact destination readback, persona/destination fit, fresh credentials-free registry metadata, required capability, zero-new-spend compatibility, and separate public-effect authority. Unproven route artifacts remain open and later cross-platform contracts may require more.

Route priority: Buffer-first if current workspace/channels are freshly verified; direct Meta/TikTok/Reddit remain fallbacks/design work. **X direct API remains BLOCKED_NO_SPEND** unless an existing compatible approved zero-spend route (for example a freshly verified Buffer-connected X channel) qualifies. Do not buy credits.

## Resource inventory
Owner Mac: Apple M5 Pro, 48 GiB unified memory, Ollama on loopback `127.0.0.1:11434`, local manifests `qwen3.5:9b`, `qwen3.5:4b`, `gemma3:4b`. No inference/download/model-load/daemon change performed by this disposition. Public-repo GitHub Actions is owner-approved as the intended zero-cost CI route.

Retry/backoff implementation remains HELD. No live model/public/account/scheduler/spend/merge/deploy grant is created here.
