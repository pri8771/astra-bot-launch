# CODEX current public capture preparation — LEAD-065 submission

Release: `LEAD-065_2026-09-22T0934.md` at expected coordination base
`7451465a74bd06a2676efd7a04cd0f60a86463c5`.

Collector implementation: accepted execution-binding source
`codex/bots-execution-binding-20260922@fec97738ec0e9407415f60228f7c3938613396c3`
(tree `43e80b92d8ae559db55a41ed33329695e6fd03fc`).

## Captured candidates

| ID | Public URL | Receipt | Captured UTC | Raw SHA-256 | Relevance |
|---|---|---|---|---|---|
| E1 | `https://about.fb.com/news/2026/06/reels-is-shaping-indias-video-first-future-across-gen-z-women-bharat/` | `cap-7920a4414afe4fe4` | `2026-09-22T11:28:42+00:00` | `adf1d1b5f7006431bf3806479d8a227a4152cf5472a879865f9606586bdc069d` | Current audience evidence for Reels discovery, genres, and cohort engagement. |
| E2 | `https://newsroom.tiktok.com/tiktok-and-amplify-launch-new-creator-led-content-series-for-brands?lang=en-AU` | `cap-9701ad2cb45c4b19` | `2026-09-22T11:28:42+00:00` | `72aefb0b9d06e72f08e10a12e18df6d81108ce430f0b7a5ffec941c31c410cce` | Current creator-led episodic-content evidence for sustained engagement reasoning. |

The captures are distinct both by source and bytes. E1 is Meta audience and
discovery evidence; E2 is TikTok creator-led content-format evidence.

## Frozen evidence

`social-bots/receipts/evidence/CODEX_CURRENT_CAPTURE_20260922/` contains each
candidate's raw bytes, collector receipt, and normalized signal separately, plus
`CAPTURE_INDEX.json`. Both receipts report `status: ok`,
`provenance: live-capture`, `transport_trusted: true`, and HTTP 200. Recomputed
raw SHA-256 values match receipt content hashes. Receipt-file SHA-256 values are
recorded in the capture index.

The capture-only driver invoked exactly two `divergence_freeze.capture_source`
calls through the accepted `UrllibFetcher` collector path. It imported neither
matrix preparation nor provider/dispatch code. The evidence directory contains
no prepared matrix, prompts directory, or execution manifest.

## Boundary and requested disposition

No model/provider call, public post, account action, spend, scheduler action,
or final five-call execution manifest was made. This is **READY_FOR_LEAD
SUITABILITY_REVIEW**, not model authorization or acceptance. The lead must decide
whether these exact bytes/receipts/signals are suitable as final V0.4 divergence
inputs before any matrix rebuild or owner-call request.
