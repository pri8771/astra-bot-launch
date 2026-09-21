#!/usr/bin/env python3
"""SB-R07-042 — freeze controlled V0.4 divergence inputs (no model call).

Performs two trusted live HTTPS captures (E1/E2), builds the five-case prepare
matrix, and writes an immutable freeze bundle. Never constructs an adaptive
provider.

Exit codes
    0  freeze written
    1  capture/matrix/isolation failure
    2  bad usage
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import divergence_freeze as df  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out-dir", required=True,
                   help="empty directory that will hold the immutable freeze")
    p.add_argument("--e1-url", default=df.DEFAULT_E1_URL)
    p.add_argument("--e2-url", default=df.DEFAULT_E2_URL)
    p.add_argument("--persona-dir", default=None)
    p.add_argument("--objective", default=df.DEFAULT_OBJECTIVE)
    p.add_argument("--run-scope", default="v04-divergence-freeze")
    p.add_argument("--lane", default="cursor-recovery")
    args = p.parse_args(argv)
    try:
        manifest = df.freeze_inputs(
            args.out_dir,
            e1_url=args.e1_url,
            e2_url=args.e2_url,
            persona_dir=args.persona_dir,
            objective=args.objective,
            run_scope=args.run_scope,
            lane=args.lane,
        )
    except df.FreezeError as exc:
        print(f"FREEZE FAILED: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"FREEZE FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({
        "freeze_id": manifest["freeze_id"],
        "out_dir": args.out_dir,
        "acceptance_eligible": manifest["acceptance_eligible"],
        "isolation_all_isolated": manifest["isolation_all_isolated"],
        "live_model_call_performed": manifest["live_model_call_performed"],
        "live_network_capture_performed": manifest["live_network_capture_performed"],
        "acceptance_claim": manifest["acceptance_claim"],
        "sources": manifest["sources"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
