#!/usr/bin/env python3
"""PREPARE-ONLY V0.4 adaptive divergence matrix (SB-V04-002 / SB-V04-004).

Builds, hashes and isolation-checks the conservative five-case matrix from
``social-bots/V04_DIVERGENCE_ACCEPTANCE_PLAN.md`` WITHOUT invoking any adaptive
or model provider. No subprocess is spawned, no network is touched, nothing is
spent.

Subcommands
    prepare   build the matrix, verify isolation, write the immutable artifact
    verify    re-derive every digest in a written artifact and re-check isolation
    gate      print the live-execution authorization gate state (expected: DENIED)
    report    validate per-case receipts and report material divergence

Evidence
    ``--evidence-bundle FILE`` supplies real captured snapshots. Without it the
    command synthesizes two clearly labeled ENGINEERING FIXTURE snapshots so the
    machinery and the gate can be exercised; the resulting artifact is stamped
    ``acceptance_eligible: false``. A fixture bundle is never acceptance evidence.

    Bundle format:
        {"E1": {"signal": {...}, "raw_b64"|"raw_text": ..., "receipt": {...},
                "provenance_label": "live-capture", "captured_at": "..."},
         "E2": {...}}

Exit codes
    0  completed (including a correctly DENIED gate, which is the expected state)
    1  verification/isolation failure, or a malformed input
    2  bad usage
"""
from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import authorization, divergence_prepare as dp  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PERSONA_DIR = ROOT / "personas"

# Persona slot -> persona file. Matches the plan's matrix: three general runtimes
# plus one cultural/Primandir workspace.
PERSONA_FILES = {
    "baseline": "social-a.json",
    "variant_b": "social-b.json",
    "variant_c": "social-c.json",
    "cultural": "cultural-primandir-atman.json",
}

DEFAULT_OBJECTIVE = ("grow a durable, factually sound audience without publishing "
                     "anything unreviewed")


def load_personas(directory: Path = PERSONA_DIR) -> dict[str, dict]:
    personas: dict[str, dict] = {}
    for slot, filename in PERSONA_FILES.items():
        path = directory / filename
        if not path.exists():
            raise SystemExit(f"missing persona file {path}")
        personas[slot] = json.loads(path.read_text(encoding="utf-8"))
    return personas


def _fixture_snapshots() -> dict[str, dp.EvidenceSnapshot]:
    """Two materially different ENGINEERING FIXTURE snapshots.

    Deliberately explicit: these are not captures, are labeled as fixtures, and
    force ``acceptance_eligible: false``. They exist so the matrix, digests,
    isolation checks and the fail-closed gate can be exercised with zero spend.
    """
    e1_raw = b'{"fixture":"E1","note":"engineering fixture, not a real capture"}'
    e2_raw = b'{"fixture":"E2","note":"engineering fixture, not a real capture"}'
    e1_signal = {
        "id": "sig-fixture-e1",
        "title": "Plain-text accounting tooling adds a reconciliation report",
        "summary": "A widely used plain-text accounting library published a release "
                   "adding a reconciliation report command.",
        "source": "engineering-fixture",
        "url": "https://example.invalid/fixture/e1",
        "captured_at": "2026-09-21T00:00:00Z",
        "provenance": "fixture",
        "tags": ["accounting", "tooling", "release"],
    }
    e2_signal = {
        "id": "sig-fixture-e2",
        "title": "Municipal transit board publishes a fare-equity dataset",
        "summary": "A municipal transit board released a machine-readable dataset "
                   "describing fare-equity outcomes by route.",
        "source": "engineering-fixture",
        "url": "https://example.invalid/fixture/e2",
        "captured_at": "2026-09-21T00:00:00Z",
        "provenance": "fixture",
        "tags": ["transit", "open-data"],
    }
    return {
        "E1": dp.EvidenceSnapshot.from_bytes(
            "E1", e1_signal, e1_raw,
            {"kind": "engineering-fixture", "byte_length": len(e1_raw),
             "http_status": None, "url": e1_signal["url"]},
            provenance_label=dp.ENGINEERING_FIXTURE, captured_at="2026-09-21T00:00:00Z"),
        "E2": dp.EvidenceSnapshot.from_bytes(
            "E2", e2_signal, e2_raw,
            {"kind": "engineering-fixture", "byte_length": len(e2_raw),
             "http_status": None, "url": e2_signal["url"]},
            provenance_label=dp.ENGINEERING_FIXTURE, captured_at="2026-09-21T00:00:00Z"),
    }


def load_snapshots(path: str | None) -> dict[str, dp.EvidenceSnapshot]:
    if not path:
        return _fixture_snapshots()
    bundle = json.loads(Path(path).read_text(encoding="utf-8"))
    out: dict[str, dp.EvidenceSnapshot] = {}
    for sid in ("E1", "E2"):
        if sid not in bundle:
            raise SystemExit(f"evidence bundle is missing {sid}")
        entry = bundle[sid]
        if "raw_b64" in entry:
            raw = base64.b64decode(entry["raw_b64"])
        elif "raw_text" in entry:
            raw = entry["raw_text"].encode("utf-8")
        else:
            raise SystemExit(f"{sid}: bundle entry needs raw_b64 or raw_text")
        out[sid] = dp.EvidenceSnapshot.from_bytes(
            sid, entry["signal"], raw, entry.get("receipt", {}),
            provenance_label=entry.get("provenance_label", dp.ENGINEERING_FIXTURE),
            captured_at=entry.get("captured_at"))
    return out


def cmd_prepare(args) -> int:
    personas = load_personas()
    snapshots = load_snapshots(args.evidence_bundle)
    try:
        matrix = dp.build_matrix(
            personas=personas, snapshots=snapshots, objective=args.objective,
            run_scope=args.run_scope, lane=args.lane,
            pending_count=args.pending_count, is_duplicate=args.is_duplicate,
            prior_hypotheses=args.prior_hypotheses)
    except dp.MatrixError as exc:
        print(f"MATRIX ERROR: {exc}", file=sys.stderr)
        return 1

    out_dir = Path(args.out_dir)
    matrix_path = out_dir / "PREPARED_MATRIX.json"
    prompts_dir = out_dir / "prompts"
    try:
        dp.write_prepared(matrix, matrix_path)
        dp.write_prompts(matrix, prompts_dir)
    except dp.MatrixError as exc:
        print(f"WRITE REFUSED: {exc}", file=sys.stderr)
        return 1

    status = dp.prepare_only_status(matrix, lane=args.lane,
                                    manifest_dir=args.manifest_dir, home=args.home)
    status_path = out_dir / "PREPARE_STATUS.json"
    status_path.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(json.dumps({
        "prepared_matrix": str(matrix_path),
        "prompts_dir": str(prompts_dir),
        "status": str(status_path),
        "planned_call_count": status["planned_call_count"],
        "all_isolated": status["isolation"]["all_isolated"],
        "live_execution_permitted": status["live_execution_permitted"],
        "live_execution_performed": status["live_execution_performed"],
        "acceptance_eligible": status["acceptance_eligible"],
        "engineering_only_reasons": status["engineering_only_reasons"],
    }, indent=2))
    return 0


def _default_prompts_dir(matrix_path: str, explicit: str | None) -> str | None:
    """Prompts live beside the matrix unless told otherwise.

    Defaulting to None would make ``verify`` skip the prompt bytes — the layer
    that actually catches an edited prompt file — so the sibling directory is
    used automatically when it exists.
    """
    if explicit:
        return explicit
    sibling = Path(matrix_path).parent / "prompts"
    return str(sibling) if sibling.is_dir() else None


def cmd_verify(args) -> int:
    result = dp.verify_written(args.matrix,
                               _default_prompts_dir(args.matrix, args.prompts_dir))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verified"] else 1


def cmd_gate(args) -> int:
    rows = {
        artifact: authorization.gate_status(
            artifact=artifact, lane=args.lane, run_scope=args.run_scope,
            manifest_dir=args.manifest_dir)
        for artifact in dp.BATCH_ARTIFACTS
    }
    print(json.dumps({
        "manifest_dir": str(args.manifest_dir or authorization.MANIFEST_DIR),
        "manifests_present": [p.name for p in
                              authorization.find_manifests(args.manifest_dir)],
        "hard_max_calls": authorization.HARD_MAX_CALLS,
        "gates": rows,
        "live_execution_permitted": all(r["live_execution_permitted"] for r in rows.values()),
    }, indent=2, sort_keys=True))
    return 0


def cmd_report(args) -> int:
    matrix = dp.load_prepared(
        args.matrix, _default_prompts_dir(args.matrix, args.prompts_dir))
    receipts: dict[str, dict] = {}
    receipt_dir = Path(args.receipts)
    for case_id, *_ in dp.CASE_SPECS:
        path = receipt_dir / f"{case_id}.json"
        if path.exists():
            receipts[case_id] = json.loads(path.read_text(encoding="utf-8"))
    budget = (authorization.CallBudget(matrix.run_scope, len(matrix.cases),
                                       home=args.home) if args.home else None)
    report = dp.divergence_report(matrix, receipts, budget=budget)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)

    def common(sp):
        sp.add_argument("--lane", default="windows-core")
        sp.add_argument("--run-scope", default="v04-divergence-prepare")
        sp.add_argument("--manifest-dir", default=None,
                        help="override the canonical authorization manifest dir")

    prep = sub.add_parser("prepare", help="build and write the prepare-only matrix")
    common(prep)
    prep.add_argument("--out-dir", required=True)
    prep.add_argument("--evidence-bundle", default=None,
                      help="real captured E1/E2 bundle; omitted means labeled fixtures")
    prep.add_argument("--objective", default=DEFAULT_OBJECTIVE)
    prep.add_argument("--pending-count", type=int, default=0)
    prep.add_argument("--is-duplicate", action="store_true")
    prep.add_argument("--prior-hypotheses", type=int, default=0)
    prep.add_argument("--home", default=None, help="override SBOTS_HOME for the budget")
    prep.set_defaults(func=cmd_prepare)

    ver = sub.add_parser("verify", help="re-derive digests and re-check isolation")
    ver.add_argument("--matrix", required=True)
    ver.add_argument("--prompts-dir", default=None,
                     help="default: the prompts/ directory beside the matrix")
    ver.set_defaults(func=cmd_verify)

    gate = sub.add_parser("gate", help="print the fail-closed authorization gate state")
    common(gate)
    gate.set_defaults(func=cmd_gate)

    rep = sub.add_parser("report", help="validate receipts and report divergence")
    rep.add_argument("--matrix", required=True)
    rep.add_argument("--prompts-dir", default=None)
    rep.add_argument("--receipts", required=True,
                     help="directory holding <case_id>.json receipts")
    rep.add_argument("--home", default=None,
                     help="runtime data root holding the call-budget ledger; without "
                          "it acceptance eligibility cannot be established")
    rep.set_defaults(func=cmd_report)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
