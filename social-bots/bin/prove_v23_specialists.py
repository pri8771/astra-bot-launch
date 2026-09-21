#!/usr/bin/env python3
"""SB-S23-008 — ENGINEERING acceptance runner for the specialist lifecycle.

Runs a researcher, then a concurrent analyst / writer / reviewer, through
``runtime.specialist_lifecycle`` on FIXTURE data inside a fresh temporary
``SBOTS_HOME`` (never the repository tree), and writes a hashed evidence bundle:

    <out>/manifest.json                 source SHA, command, classification "fixture", file hashes
    <out>/lifecycle-<worker_id>.json    one LifecycleRecord per worker
    <out>/parent_state_before.sha256    hash of the seeded parent stores before the run
    <out>/parent_state_after.sha256     ... and after (must be identical)
    <out>/leases_after.json             lease files left behind (must be [])
    <out>/scratch_after.json            scratch entries left behind (must be [])

The runner REFUSES to write a bundle when any lease is still held or any scratch
remains. Everything here is ``classification: "fixture"``; nothing in this
runner is, or can be relabeled as, LIVE evidence. No network, no model call.

Usage:
    python3 bin/prove_v23_specialists.py --bot social-a \
        --personas social-a,cultural-primandir-atman \
        --out receipts/evidence/SB-S23-008/<run-id>/
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import paths  # noqa: E402
from runtime import specialist_contract as sc  # noqa: E402
from runtime import specialist_lifecycle as sl  # noqa: E402
from runtime import specialist_research as sr  # noqa: E402
from runtime import specialist_analysis as sa  # noqa: E402
from runtime import specialist_writer as sw  # noqa: E402
from runtime.specialist_sandbox import kept_dir  # noqa: E402
from runtime.jsonstore import append_jsonl, now_iso  # noqa: E402

ARTIFACT = "SB-S23-008"
CLASSIFICATION = "fixture"
FIXTURE_SOURCES = {"https://fixture.invalid/a": "fixture source A: the sky is blue.",
                   "https://fixture.invalid/b": "fixture source B: water is wet."}
PARENT_KINDS = ("state", "content", "experiments", "memory", "analytics")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parent_state_hash(home: Path) -> str:
    h = hashlib.sha256()
    for kind in PARENT_KINDS:
        d = home / kind
        if not d.exists():
            continue
        for p in sorted(d.rglob("*")):
            rel = p.relative_to(home).as_posix()
            h.update(rel.encode())
            if p.is_file():
                h.update(sha256_file(p).encode())
    return h.hexdigest()


def seed_parent_stores(bot: str, personas: list[str]) -> None:
    """Fixture persona/runtime stores, so 'unchanged' is a meaningful claim."""
    (paths.state_dir(bot) / "bot_state.json").write_text(json.dumps(
        {"runtime": bot, "schema_version": 2, "fixture": True}, indent=2))
    for persona in personas:
        (paths.state_dir(bot) / f"persona-{persona}.json").write_text(json.dumps(
            {"runtime": bot, "persona_id": persona, "schema_version": 1, "fixture": True,
             "hypotheses": {}, "consumed_signal_ids": []}, indent=2))
        append_jsonl(paths.memory_dir(bot) / "decisions.jsonl",
                     {"persona": persona, "decision_id": f"fixture-{persona}", "fixture": True})
    (paths.content_dir(bot) / "content_history.jsonl").write_text("")
    (paths.experiments_dir(bot) / "index.jsonl").write_text("")


def _contract(bot, persona, run_id, role, schema, **kw):
    return sc.new_contract(bot=bot, persona=persona, parent_run_id=run_id, role=role,
                           objective=f"{role} fixture objective", expected_output_schema=schema,
                           time_budget_s=30, provenance="fixture", **kw)


def _kept_json(contract, rel: str) -> dict:
    return json.loads((kept_dir(contract) / rel).read_bytes().decode("utf-8"))


def run_lifecycles(bot: str, personas: list[str], run_id: str, max_workers: int = 3) -> list:
    pa = personas[0]
    pb = personas[1] if len(personas) > 1 else personas[0]

    # 1. researcher for persona A (fixture sources) -> adopted evidence
    c_r = _contract(bot, pa, run_id, "researcher", "ResearchResult/1", input_artifacts=[
        {"kind": "source_candidate", "url": u} for u in FIXTURE_SOURCES])
    rec_r = sl.run_specialist(c_r, sr.ResearchSpecialist(),
                              adapter_kwargs={"collector": sr.FixtureCollector(FIXTURE_SOURCES)})
    analyst_inputs: dict = {}
    if rec_r.decision == sl.ADOPTED:
        analyst_inputs["research_result.json"] = _kept_json(c_r, "outputs/research_result.json")
        for i in range(len(FIXTURE_SOURCES)):
            analyst_inputs[f"evidence/{i:03d}.json"] = _kept_json(c_r, f"evidence/{i:03d}.json")

    # Fixture analysis/draft bundle for the writer (persona B) and reviewer (persona A).
    ev = {"evidence_id": "ev-fixture-1", "source_id": "src-fixture-1", "url": "https://fixture.invalid/c",
          "captured_at": now_iso(), "content_hash": "f" * 64, "provenance": "fixture",
          "collector_version": "1.0.0", "status": "ok"}
    capture = {"schema": "EvidenceCapture/1", "index": 0, "evidence_ref": ev,
               "receipt": {"status": "ok", "receipt_id": "cap-fixture-1"}}
    analysis = {"schema": "AnalysisResult/1",
                "findings": [{"statement": "fixture finding", "evidence_refs": [ev]}]}
    draft = {"schema": "DraftResult/1", "candidate": {"status": "DRAFT_UNPUBLISHED", "body": "x"},
             "claims": [{"text": "fixture claim", "evidence_refs": [ev]}]}

    jobs = [
        {"contract": _contract(bot, pa, run_id, "analyst", "AnalysisResult/1"),
         "adapter": sa.AnalystSpecialist(), "inputs": analyst_inputs},
        {"contract": _contract(bot, pb, run_id, "writer", "DraftResult/1"),
         "adapter": sw.WriterSpecialist(),
         "inputs": {"evidence/000.json": capture, "analysis.json": analysis}},
        {"contract": _contract(bot, pa, run_id, "reviewer", "ReviewResult/1"),
         "adapter": sa.ReviewerSpecialist(),
         "inputs": {"evidence/000.json": capture, "analysis.json": analysis, "draft.json": draft}},
    ]
    return [rec_r] + sl.run_concurrent(jobs, max_workers=max_workers)


def build_bundle(out_dir: str | Path, *, bot: str, personas: list[str], source_sha: str,
                 command: str, max_workers: int = 3) -> dict:
    """Run the fixture lifecycles in a fresh SBOTS_HOME and write the bundle.

    Returns the manifest dict. If cleanup is incomplete, returns
    ``{"refused": True, ...}`` and writes NOTHING.
    """
    out = Path(out_dir)
    home = Path(tempfile.mkdtemp(prefix="sbots-v23-"))
    prev_home = os.environ.get("SBOTS_HOME")
    os.environ["SBOTS_HOME"] = str(home)
    run_id = f"v23-{uuid.uuid4().hex[:8]}"
    try:
        seed_parent_stores(bot, personas)
        before = parent_state_hash(home)
        records = run_lifecycles(bot, personas, run_id, max_workers=max_workers)
        after = parent_state_hash(home)
        leases_dir = home / "leases"
        leases_after = sorted(p.name for p in leases_dir.glob("*.lease.json")) if leases_dir.exists() else []
        scratch_dir = home / "scratch"
        scratch_after = sorted(p.relative_to(home).as_posix() for p in scratch_dir.rglob("*")
                               if p.is_file()) if scratch_dir.exists() else []
        unreleased = [r.worker_id for r in records if not r.lease_gone]
        if unreleased or scratch_after or leases_after:
            return {"refused": True, "artifact": ARTIFACT, "reason": "cleanup incomplete",
                    "unreleased": unreleased, "scratch_after": scratch_after,
                    "leases_after": leases_after}
        out.mkdir(parents=True, exist_ok=True)
        files: dict[str, str] = {}

        def put(name: str, data) -> None:
            p = out / name
            if isinstance(data, (dict, list)):
                p.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            else:
                p.write_text(str(data) + "\n", encoding="utf-8")
            files[name] = sha256_file(p)

        for r in records:
            put(f"lifecycle-{r.worker_id}.json", r.as_dict())
        put("parent_state_before.sha256", before)
        put("parent_state_after.sha256", after)
        put("leases_after.json", leases_after)
        put("scratch_after.json", scratch_after)
        manifest = {
            "schema": "SpecialistAcceptanceBundle/1", "artifact": ARTIFACT,
            "classification": CLASSIFICATION, "live": False,
            "note": "engineering acceptance on fixture data in a temporary SBOTS_HOME; "
                    "not LIVE evidence and cannot promote any milestone",
            "source_sha": source_sha, "command": command, "run_id": run_id,
            "generated_at": now_iso(), "bot": bot, "personas": personas,
            "max_workers": max_workers,
            "decisions": {r.worker_id: {"role": r.role, "persona": r.persona,
                                        "decision": r.decision, "cleanup": r.cleanup_status,
                                        "lease_gone": r.lease_gone} for r in records},
            "parent_state_unchanged": before == after,
            "files": files,
        }
        (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                                           encoding="utf-8")
        return manifest
    finally:
        if prev_home is None:
            os.environ.pop("SBOTS_HOME", None)
        else:
            os.environ["SBOTS_HOME"] = prev_home
        shutil.rmtree(home, ignore_errors=True)


def verify_bundle(out_dir: str | Path) -> list[str]:
    """Re-hash every file named in the manifest. Empty list means it verifies."""
    out = Path(out_dir)
    try:
        manifest = json.loads((out / "manifest.json").read_bytes())
    except (OSError, ValueError) as exc:
        return [f"manifest unreadable: {exc}"]
    errs = []
    if manifest.get("classification") != CLASSIFICATION or manifest.get("live") is not False:
        errs.append("manifest must be classification=fixture, live=false")
    for name, digest in (manifest.get("files") or {}).items():
        p = out / name
        if not p.is_file():
            errs.append(f"missing {name}")
        elif sha256_file(p) != digest:
            errs.append(f"hash mismatch {name}")
    return errs


def _git_sha() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                              timeout=10, check=True).stdout.strip()
    except Exception:                                    # noqa: BLE001 - unknown is honest
        return "unknown"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bot", default="social-a")
    ap.add_argument("--personas", default="social-a,cultural-primandir-atman")
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-workers", type=int, default=3)
    ap.add_argument("--source-sha", default=None)
    args = ap.parse_args(argv)
    personas = [p.strip() for p in args.personas.split(",") if p.strip()]
    manifest = build_bundle(args.out, bot=args.bot, personas=personas,
                            source_sha=args.source_sha or _git_sha(),
                            command=" ".join([Path(sys.argv[0]).name, *(argv or sys.argv[1:])]),
                            max_workers=args.max_workers)
    if manifest.get("refused"):
        print(json.dumps(manifest, indent=2))
        return 2
    errs = verify_bundle(args.out)
    print(json.dumps({"artifact": ARTIFACT, "classification": manifest["classification"],
                      "decisions": manifest["decisions"],
                      "parent_state_unchanged": manifest["parent_state_unchanged"],
                      "bundle": str(args.out), "verified": not errs, "errors": errs}, indent=2))
    return 0 if not errs and all(d["decision"] == "ADOPTED" for d in manifest["decisions"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
