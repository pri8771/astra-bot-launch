#!/usr/bin/env python3
"""SB-R07-044 — independently verify a V0.4 divergence evidence bundle.

Loads a prepared matrix, per-case receipts, and an optional call-budget ledger
from disk. Never spawns a provider, never spends, never self-accepts.

Exit codes
    0  verifier completed (any truthful verdict, including REJECTED/INCOMPLETE)
    1  load/verify machinery failure
    2  bad usage

A zero exit does NOT mean ACCEPTED. Read ``verdict`` and ``acceptance_claim``.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import divergence_verifier as dv  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--matrix", required=True, help="path to PREPARED_MATRIX.json")
    p.add_argument("--receipts", required=True,
                   help="directory containing P0.json .. E0.json")
    p.add_argument("--budget-home", default=None,
                   help="SBOTS_HOME-style directory holding the call-budget ledger")
    p.add_argument("--prompts-dir", default=None,
                   help="optional prompts directory (defaults to sibling prompts/)")
    p.add_argument("--out", default=None, help="optional path to write the verdict JSON")
    args = p.parse_args(argv)

    try:
        result = dv.verify_from_paths(
            matrix_path=args.matrix,
            receipts_dir=args.receipts,
            budget_home=args.budget_home,
            prompts_dir=args.prompts_dir,
        )
    except Exception as exc:  # noqa: BLE001 - surface load failures as exit 1
        print(f"VERIFY FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
