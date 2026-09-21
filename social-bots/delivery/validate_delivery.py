#!/usr/bin/env python3
"""Read-only validation of the Social Bots delivery supplement (Python 3.10+).

No task execution, Git writes, network, provider calls, state changes or acceptance.
Use --repo /path/to/checkout for additional checks against the real artifact index.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

GATES = {
    "G-LEAD", "G-HOST", "G-LEAD-LOOP", "G-MODEL-V04", "G-MODEL-RUNS",
    "G-ACCOUNTS", "G-PUBLISH", "G-MEASURE", "G-CULTURAL", "G-SPEND",
}
SCOPES = {
    "OFFLINE_FIXTURE", "LIVE_SOURCE", "REAL_PROCESS", "NATIVE_SCHEDULER",
    "LIVE_MODEL", "LIVE_ACCOUNT", "LIVE_PUBLIC_EFFECT", "LIVE_ANALYTICS",
}
VERSIONS = ([f"V0.{n}" for n in range(4, 10)]
            + [f"V1.{n}" for n in range(10)]
            + [f"V2.{n}" for n in range(10)] + ["V3.0"])
ARTIFACT_RE = re.compile(r"SB-[A-Z0-9]+(?:-[A-Z0-9]+)+\Z")
TASK_RE = re.compile(r"C\d{2}\Z")


def read_object(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot load {path.name}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return data


def graph_errors(rows: list[dict[str, Any]], dep_key: str) -> list[str]:
    errors: list[str] = []
    ids = [r.get("id") for r in rows]
    if any(not isinstance(i, str) or not i for i in ids):
        return ["graph: missing or invalid ID"]
    if len(set(ids)) != len(ids):
        errors.append("graph: duplicate IDs")
    graph: dict[str, list[str]] = {}
    for row in rows:
        deps = row.get(dep_key, [])
        if not isinstance(deps, list) or any(not isinstance(d, str) for d in deps):
            errors.append(f"{row['id']}: invalid dependency list")
            deps = []
        if len(set(deps)) != len(deps):
            errors.append(f"{row['id']}: duplicate dependency")
        graph[row["id"]] = deps
        for dep in deps:
            if dep not in ids:
                errors.append(f"{row['id']}: missing dependency {dep}")
    active: set[str] = set()
    complete: set[str] = set()

    def visit(node: str) -> None:
        if node in complete:
            return
        if node in active:
            errors.append(f"graph: dependency cycle involving {node}")
            return
        active.add(node)
        for dep in graph.get(node, []):
            if dep in graph:
                visit(dep)
        active.remove(node)
        complete.add(node)

    for node in graph:
        visit(node)
    return errors


def nonempty_strings(value: Any) -> bool:
    return (isinstance(value, list) and bool(value)
            and all(isinstance(v, str) and v.strip() for v in value))


def validate_data(tasks_doc: dict[str, Any], gates_doc: dict[str, Any],
                  corrections_doc: dict[str, Any], root: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    tasks = tasks_doc.get("tasks")
    milestones = gates_doc.get("milestones")
    corrections = corrections_doc.get("changes")
    for name, rows in (("tasks", tasks), ("milestones", milestones),
                       ("changes", corrections)):
        if not isinstance(rows, list) or not rows or any(not isinstance(r, dict) for r in rows):
            errors.append(f"{name}: expected a nonempty list of objects")
    if errors:
        return {"errors": errors, "warnings": warnings}
    assert isinstance(tasks, list) and isinstance(milestones, list) and isinstance(corrections, list)
    if corrections_doc.get("apply_automatically") is not False:
        errors.append("reconciliation must not apply automatically")
    if gates_doc.get("status") != "PROPOSED_TEST_DESIGN_NOT_AUTHORIZATION":
        errors.append("gate document must not imply authorization")
    errors += graph_errors(tasks, "build_requires")
    for row in tasks:
        label = str(row.get("id"))
        if not TASK_RE.fullmatch(label):
            errors.append(f"{label}: invalid task ID")
        if row.get("status") != "PLANNED_NEXT_ROUND":
            errors.append(f"{label}: task status must remain planning-only")
        sp = row.get("story_points")
        if type(sp) is not int or sp not in (1, 2):
            errors.append(f"{label}: split tasks larger than SP2")
        for key in ("title", "owner_role", "completion_test", "rollback"):
            if not isinstance(row.get(key), str) or not row[key].strip():
                errors.append(f"{label}: missing {key}")
        for key in ("inputs", "outputs", "proposed_code_surface", "test_cases",
                    "supports_artifacts", "contract_sections", "evidence_scopes"):
            if not nonempty_strings(row.get(key)):
                errors.append(f"{label}: missing/non-string {key}")
        if not isinstance(row.get("test_cases"), list) or len(row["test_cases"]) < 3:
            errors.append(f"{label}: at least three concrete tests required")
        for ref in row.get("supports_artifacts", []):
            if not isinstance(ref, str) or not ARTIFACT_RE.fullmatch(ref):
                errors.append(f"{label}: invalid artifact reference")
        for gate in row.get("external_gates", []):
            if gate not in GATES:
                errors.append(f"{label}: unknown external gate {gate}")
        for scope in row.get("evidence_scopes", []):
            if scope not in SCOPES:
                errors.append(f"{label}: unknown evidence scope {scope}")
        for ref in row.get("contract_sections", []):
            if not isinstance(ref, str):
                continue
            filename = ref.split("#", 1)[0]
            resolved = (root / filename).resolve()
            if not resolved.is_relative_to(root.resolve()) or not resolved.is_file():
                errors.append(f"{label}: missing/escaping contract file {filename}")
    if [row.get("version") for row in milestones] != VERSIONS:
        errors.append("milestones must cover V0.4 through V3.0 once, in order")
    previous = "V0.3"
    for row in milestones:
        version = row.get("version")
        if row.get("previous_version") != previous:
            errors.append(f"{version}: missing sequential product predecessor")
        previous = version
        for key in ("title", "scenario", "proof"):
            if not isinstance(row.get(key), str) or not row[key].strip():
                errors.append(f"{version}: missing {key}")
        if not nonempty_strings(row.get("required_artifacts")):
            errors.append(f"{version}: no product gate artifacts")
        if not nonempty_strings(row.get("live_scopes")):
            errors.append(f"{version}: no real evidence scope")
        if "OFFLINE_FIXTURE" in row.get("live_scopes", []):
            errors.append(f"{version}: fixture cannot be the operational proof")
        for scope in row.get("live_scopes", []):
            if scope not in SCOPES:
                errors.append(f"{version}: unknown evidence scope")
        for gate in row.get("external_gates", []):
            if gate not in GATES:
                errors.append(f"{version}: unknown external gate")
        if version == "V0.7" and "NATIVE_SCHEDULER" not in row.get("live_scopes", []):
            errors.append("V0.7: native scheduler evidence is required")
        if version == "V0.9" and "G-PUBLISH" not in row.get("external_gates", []):
            errors.append("V0.9: separate public authorization required")
    correction_ids = [row.get("id") for row in corrections]
    if any(not isinstance(i, str) for i in correction_ids) or len(set(correction_ids)) != len(correction_ids):
        errors.append("reconciliation: invalid/duplicate IDs")
    return {"errors": errors, "warnings": warnings,
            "task_count": len(tasks), "milestone_count": len(milestones),
            "reconciliation_count": len(corrections)}


def check_repository(repo: Path, tasks_doc: dict[str, Any], gates_doc: dict[str, Any]) -> dict[str, Any]:
    """Read actual index/state without mutating them. Never interpret this as acceptance."""
    sb = repo / "social-bots"
    index = read_object(sb / "ARTIFACT_INDEX.json")
    rows = index.get("artifacts")
    if not isinstance(rows, list) or any(not isinstance(r, dict) for r in rows):
        raise ValueError("Repository artifact index has an invalid artifacts list")
    errors = graph_errors(rows, "depends_on")
    warnings: list[str] = []
    by_id = {r["id"]: r for r in rows if isinstance(r.get("id"), str)}
    refs = {a for t in tasks_doc["tasks"] for a in t["supports_artifacts"]}
    refs.update(a for m in gates_doc["milestones"] for a in m["required_artifacts"])
    for artifact in sorted(refs):
        if artifact not in by_id:
            errors.append(f"Repository is missing referenced artifact {artifact}")
    for artifact in sorted(refs & set(by_id)):
        ref = by_id[artifact].get("canonical_ref", "")
        if isinstance(ref, str) and ref.startswith("social-bots/artifact-packets/"):
            path = (repo / ref).resolve()
            if not path.is_relative_to(repo.resolve()) or not path.is_file():
                errors.append(f"Missing/escaping packet for {artifact}: {ref}")
    readiness = by_id.get("SB-V23-099", {})
    if "SB-S20-007" in readiness.get("depends_on", []):
        warnings.append("C01: SB-V23-099 directly depends on LIVE S20-007; reconcile rehearsal evidence requirements")
    state_path = sb / "STATE.json"
    if state_path.is_file():
        state = read_object(state_path)
        review = state.get("lead_review", {})
        actual = review.get("review_ref", "")
        pointer = state.get("management_model", {}).get("lead_review_current", "")
        if actual and pointer and actual.removeprefix("social-bots/") != pointer.removeprefix("social-bots/"):
            warnings.append("C01: current lead-review pointer disagrees with STATE.lead_review.review_ref")
        for field, expected in (("submitted_recovery", "SUBMITTED"), ("changes_required", "CHANGES_REQUIRED")):
            for artifact in review.get(field, []):
                if artifact in by_id and by_id[artifact].get("status") != expected:
                    warnings.append(f"C01: {artifact} registry status differs from current lead-review {field}")
    return {"errors": errors, "warnings": warnings, "registry_artifact_count": len(rows)}


def validate_package(root: Path, repo: Path | None = None) -> dict[str, Any]:
    tasks = read_object(root / "TASKS.json")
    gates = read_object(root / "GATES.json")
    corrections = read_object(root / "RECONCILIATION.json")
    result = validate_data(tasks, gates, corrections, root)
    result.update(validation_scope="delivery_plan_only", repo_checks_run=False,
                  production_tests_run=False, live_tests_run=False,
                  artifact_acceptance_changed=False)
    if repo is not None and not result["errors"]:
        checked = check_repository(repo, tasks, gates)
        result["repo_checks_run"] = True
        result["registry_artifact_count"] = checked["registry_artifact_count"]
        result["errors"].extend(checked["errors"])
        result["warnings"].extend(checked["warnings"])
    result["passed"] = not result["errors"]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--repo", type=Path, help="Optional actual repository checkout for reference/status checks")
    parser.add_argument("--card", help="Print one task card only; does not authorize or execute it")
    parser.add_argument("--strict-warnings", action="store_true")
    args = parser.parse_args()
    try:
        if args.card:
            tasks = read_object(args.root / "TASKS.json")["tasks"]
            matches = [t for t in tasks if t.get("id") == args.card]
            if len(matches) != 1:
                raise ValueError(f"Expected one task matching {args.card!r}")
            print(json.dumps(matches[0], indent=2, ensure_ascii=False))
            return 0
        result = validate_package(args.root, args.repo)
    except (ValueError, KeyError, TypeError, RecursionError) as exc:
        print(json.dumps({"passed": False, "error": str(exc), "validation_scope": "delivery_plan_only"}))
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return int(not result["passed"] or bool(args.strict_warnings and result["warnings"]))


if __name__ == "__main__":
    raise SystemExit(main())
