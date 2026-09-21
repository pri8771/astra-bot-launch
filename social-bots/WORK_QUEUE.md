# Work queue — LEAD-040 V0.7 recovery

Official phase remains **V0.4.x**. The owner target is V0.7 with LIVE checkpoint evidence.

Primary recovery contract: `RECOVERY_TO_V07.md`.
Primary implementation branch: `cursor/social-bots-recovery-v07-20260921`.
Base source: `claude/quirky-shannon-t1377u@918c42e2a4602589997a7c625d994e049f266d6d`.

## Current audit

The project is behind V0.7 operationally:
- V0.4 causal adaptive divergence not yet executed.
- V0.5 not closed.
- V0.6 live three-bot dry runs absent.
- V0.7 native scheduler live evidence absent.
- two-cycle autonomous lead/worker proof absent.

Engineering evidence at 918c42e is useful and should be reused, not rebuilt.

## Primary Cursor recovery queue

READY now:
1. SB-R07-071 atomic session heartbeat.
2. SB-R07-041 live-route/authorization hardening audit.
3. SB-R07-044 divergence verifier.
4. SB-R07-072 persistent-host preflight.
5. SB-R07-042 controlled input freeze.
6. SB-R07-051 operational factual-review integration.

Then pull dependency-ready SB-R07 artifacts from ARTIFACT_INDEX and RECOVERY_TO_V07.md.

## Hard gate

SB-R07-043 live five-call adaptive divergence is BLOCKED until fresh owner authorization plus matching canonical lead authorization manifest.

No public social effect is required through V0.7.

## Legacy lanes

Do not start new overlapping source work on older Core/Intelligence/Acceptance lanes while Cursor recovery is active unless ChatGPT explicitly reassigns a separate non-overlapping artifact.
