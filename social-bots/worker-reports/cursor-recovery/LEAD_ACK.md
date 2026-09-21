# Cursor Recovery — LEAD_ACK

## LEAD-047 — 2026-09-21 19:52 ET

Canonical lead release changes implementation ownership.

- Canonical release commit: `eece1d3a62417802e4316f028fbec098f3220128`.
- Cursor Recovery is now **PARKED_SAFE_HANDOFF**. Fable owns the active shared recovery/runtime integration campaign and R07-041 repair.
- Current pre-release branch head `74a515b7f3e30c94979e0f66dc6daae66daed571` is the LEAD-046 acknowledgement, not new worker implementation.
- Preserve all existing submitted recovery evidence. If material local work already exists, push it once at a safe boundary with exact source/test evidence so Fable can integrate it; otherwise do not start new source work.
- Do not install the LIVE scheduler on the previously classified unsuitable Cursor host.
- Green worker-local tests never self-accept an artifact.

No live model call, public/account effect, PAYG/new spend, destructive action, credential exposure, fabricated operational evidence, engagement manipulation, main/public release, or SwarmAI dependency is authorized.
