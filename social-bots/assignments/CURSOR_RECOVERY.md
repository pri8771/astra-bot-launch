# Assignment — Cursor Recovery

Role: primary V0.7 recovery implementation worker.

Use:
- `../RECOVERY_TO_V07.md`
- exact `../artifact-packets/recovery-v07/<ARTIFACT>.md`

Current ordered queue:
1. SB-R07-071 — atomic cross-process SESSION_ONCE uniqueness.
2. SB-R07-041 — audit inherited live-route fail-closed hardening.
3. SB-R07-044 — divergence verifier.
4. SB-R07-072 — persistent-host preflight.
5. Pull next dependency-ready recovery artifact.

Do not overlap legacy Claude branches. One fresh session = one heartbeat. No live model call is authorized.
