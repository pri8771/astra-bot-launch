# Assignment — Fable 5.1 — LEAD-043 implementation fast-track

Role: senior implementation architect + non-conflicting V2.3 engineering worker.

## Priority
1. Get V2.3 engineering-ready as fast as safely possible without interfering with Cursor recovery.
2. Keep operational V2.3 behind the complete LIVE chain.
3. Maintain V3.0 compatibility; do not let V2.4+ implementation delay V2.3.

Your planning pass is lead-adopted with canonical dependency/schema adjustments.

## Ownership
- Cursor owns V0.7 recovery and existing recovery runtime/bin/test files.
- Fable may implement only lead-released new-files-only V2.3 slices until coordination changes.

## Released work
1. SB-S23-001 — specialist contract runtime.
2. SB-S20-001 — versioned strategy store.
3. SB-S23-002 after S23-001.
4. Continue dependency-safe new-files-only S20/S21/S22/S23 work after refreshing canonical state.
5. SB-S20-000 is blocked until SB-R07-041 is ACCEPTED.

Use `V20_TO_V23_IMPLEMENTATION_SPEC.md`, `V23_CRITICAL_PATH.md`, exact artifact packets, and Specialist Worker Contract schema v2.

## Efficiency
Use lower-capability subagents for bounded mechanical work when available. Reserve Fable for architecture, concurrency, authority/security, integration and hard debugging.

## Evidence
Fast-track work is ENGINEERING unless the packet explicitly requires LIVE evidence. Fixtures never promote operational V2.0–V2.3.

## Heartbeat
One fresh Fable session = one SESSION_ONCE heartbeat.

## Hard gates
No unauthorized live model call, public/account effect, new spend/PAYG, destructive action, credential exposure or SwarmAI dependency.

Workers submit. ChatGPT accepts.
