#!/usr/bin/env python3
"""SB-R07-072 — persistent-host preflight CLI.

Records OS/persistence/repo/Python/scheduler/permission/zero-spend facts and
emits a suitability verdict. Never installs a scheduler. Never claims V0.7 LIVE
acceptance. Ephemeral Cloud Agent / CCR hosts must be recorded as UNSUITABLE.

Exit codes
    0  receipt written (any verdict)
    1  unexpected failure
    2  bad usage
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import host_preflight as hp  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root", default=None)
    p.add_argument("--out", required=True, help="path to write the preflight JSON")
    p.add_argument("--owner-attested-persistent", action="store_true",
                   help="owner/lead explicitly attested this machine as persistent "
                        "(ignored if ephemeral markers are present)")
    args = p.parse_args(argv)
    try:
        receipt = hp.collect(
            repo_root=args.repo_root,
            owner_attested_persistent=args.owner_attested_persistent,
        )
        path = hp.write_receipt(receipt, args.out)
    except Exception as exc:  # noqa: BLE001
        print(f"PREFLIGHT FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({
        "written": str(path),
        "verdict": receipt.verdict,
        "suitable_for_v07_live_scheduler": receipt.suitable_for_v07_live_scheduler,
        "live_claim": receipt.live_claim,
        "blocker_count": len(receipt.blockers),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
