#!/usr/bin/env python3
"""CLI for the reusable V0.6 dry-run runner (SB-R07-061).

Runs all three general bots under the zero-public-effect authority profile and
writes immutable run manifests. No live model call. No public publication.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))


DEFAULT_FIXTURE_SIGNALS = {
    "social-a": [dict(
        title="Engineering fixture: measurement note",
        summary="A quiet note about measurement without a material numeric claim.",
        source="fixture", url="https://example.org/a", tags=["measurement"],
        provenance="fixture")],
    "social-b": [dict(
        title="Engineering fixture: wonder note",
        summary="A soft look at tide pools without inventing citations.",
        source="fixture", url="https://example.org/b", tags=["nature"],
        provenance="fixture")],
    "social-c": [dict(
        title="Engineering fixture: culture note",
        summary="A quiet note on feed texture without numeric claims.",
        source="fixture", url="https://example.org/c", tags=["culture"],
        provenance="fixture")],
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--home", type=Path, default=None,
                    help="SBOTS_HOME for this dry-run (default: temp dir)")
    ap.add_argument("--manifest-dir", type=Path, required=True,
                    help="Directory for immutable run manifests")
    ap.add_argument("--artifact-id", default="SB-R07-061")
    ap.add_argument("--source-code-ref", default="UNKNOWN")
    ap.add_argument("--keep-home", action="store_true")
    args = ap.parse_args(argv)

    home = args.home
    tmp = None
    if home is None:
        tmp = tempfile.TemporaryDirectory(prefix="sbots-dryrun-")
        home = Path(tmp.name)
    home = Path(home)
    home.mkdir(parents=True, exist_ok=True)
    os.environ["SBOTS_HOME"] = str(home)

    from runtime import dry_run_runner as drr  # noqa: E402

    results = drr.run_three_bot_dry_runs(
        artifact_id=args.artifact_id,
        source_code_ref=args.source_code_ref,
        signal_map=DEFAULT_FIXTURE_SIGNALS,
        manifest_dir=args.manifest_dir,
    )
    summary = {
        "artifact_id": args.artifact_id,
        "source_code_ref": args.source_code_ref,
        "home": str(home),
        "manifest_dir": str(args.manifest_dir),
        "all_passed": all(r.passed for r in results),
        "any_published": any(r.published for r in results),
        "any_publish_authorized": any(r.publish_authorized for r in results),
        "model_calls_used_total": sum(r.manifest["model_calls_used"] for r in results),
        "runs": [
            {"bot": r.bot, "persona": r.persona, "outcome": r.outcome,
             "passed": r.passed, "run_id": r.manifest["run_id"],
             "public_effect_budget": r.manifest["public_effect_budget"]}
            for r in results
        ],
    }
    args.manifest_dir.mkdir(parents=True, exist_ok=True)
    (args.manifest_dir / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    if tmp is not None and not args.keep_home:
        tmp.cleanup()
    return 0 if summary["all_passed"] and not summary["any_published"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
