# Dormant Activation Proposal — V0.4 Mac Local Controlled Divergence

**Status**: **PREPARATION_ONLY — DORMANT**
**Current Authority**: `authorized: false`, `manifest_created: false`, `consumed_slots: 0`, `live_calls_authorized: 0`
**Location**: Outside `social-bots/authorizations/` (canonical manifest created only after explicit owner approval).

---

## 1. Exact Bounded Request for Product Owner

> **Request**: Authorize one bounded V0.4 controlled-divergence batch of **at most 5 sequential local Ollama calls** using the accepted local route on Mac, with **zero new spend**, for SB-V04-002 and SB-V04-004 empirical evaluation.
>
> - **Provider**: Local Ollama at literal loopback `127.0.0.1:11434`
> - **Model**: Pinned `qwen3.5:9b`, digest `6488c96fa5faab64bb65cbd30d4289e20e6130ef535a93ef9a49f42eda893ea7`
> - **Limits**: Max 5 sequential calls, timeout 120s, max 1024 output tokens, temperature 0.0, seed 0, context 8192, think false, stream false, keepalive 0
> - **Failure Policy**: First failure, error, or non-proposal stops batch immediately. No retries, no API fallback, no model downloads.
> - **Safety**: Zero spend, no cloud API tokens, no account mutation, no public posting/DM/effect, no scheduler installation.
> - **Expiry**: 2 hours from activation.

---

## 2. Frozen Matrix Inputs Bound to Execution

- **Source Commit**: `3bad0541fde8afb584bc6e396ea093b5d1f3c407`
- **Source Tree**: `781fc16b1b0a982c7014ea04942437d6ada803e6`
- **Execution Matrix Digest**: `sha256:30e0fe731b9f8cf00ead92cfbf9a2e4412e0834b0cd3fdeb9706d2ed813b740f`
- **Prepared Matrix File SHA256**: `1549df4070e8c172cdeaa393cfc2d2d46c615e649f6691f9c99f0032b6cfe4a1`
- **Run Scope**: `v04-mac-local-20260922`
- **Evidence E1**: Meta Threads live capture (Sept 16, 2026), raw SHA `2d51040128376b474391f4527c326d0d62255f61ce55da4fc0d1e334db2dc3b6` (publisher whitespace preserved)
- **Evidence E2**: TikTok/Amplify live capture (Sept 14, 2026), raw SHA `72aefb0b9d06e72f08e10a12e18df6d81108ce430f0b7a5ffec941c31c410cce`

### Matrix Cases

| Case | Persona / Workspace | Evidence | Changed Variable | Target Prompt SHA256 |
|---|---|---|---|---|
| **P0** | `social-a` | E1 | Baseline | `b089e36e451b56344be80f3f42c7b679e93c075da164a2b61ac898ac08bb8a58` |
| **P1** | `social-b` | E1 | Persona | `f777fb3e1f1448d04a335b6fe8f3b23698735e895dc4a0ac8e687e9d0925583f` |
| **P2** | `social-c` | E1 | Persona | `ab0aa0968611923c7d9e0549ee9b000297ac1e47f4ae506efbbfe77bafc3ca38` |
| **P3** | `cultural-primandir-atman` | E1 | Persona | `c782349217a63f05aa9d1e34f16192b2a1ab254b40351cad5b78067cc838285d` |
| **E0** | `social-a` | E2 | Evidence | `e3ce101df3d210cfe719236faf7e9e01e2443e7b2705db522f10644eb8906861` |

---

## 3. Pending Decisions to Clear Before Canonical Manifest Activation

1. **Owner 5-Call Grant**: Explicit owner grant authorizing the 5 local model calls defined above. (Mac selection does not constitute a model execution grant).
2. **Named Cultural Reviewer**: Owner nomination of the cultural review alias or review method for P3 (`cultural-primandir-atman`) final content validation:
   - Option A: Owner self-review (default)
   - Option B: Named designated reviewer alias
