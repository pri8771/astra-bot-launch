#!/usr/bin/env python3
"""Run ONE bounded work unit. This is the payload a host scheduler invokes.

Usage:
    python3 bin/run_worker.py <bot> [persona_id]

Exit codes:
    0  unit completed (any decision, including NO_ACTION)
    3  no-overlap: another live worker holds the lease (expected, benign)
    1  unexpected failure (a failure receipt was written)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import worker, leasing  # noqa: E402


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    bot = sys.argv[1]
    persona = sys.argv[2] if len(sys.argv) > 2 else bot
    task_id = f"cycle:{bot}:{persona}"
    try:
        res = worker.run_one_unit(task_id, bot, persona)
    except leasing.LeaseHeld as held:
        print(f"NO-OVERLAP: {held}")
        return 3
    print("OK:", {k: res[k] for k in ("worker_id", "chosen_action", "verified",
                                      "lease_released", "finish_receipt")})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
