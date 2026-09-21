#!/usr/bin/env python3
"""SB-CTL-012 — Artifact Graph Validator and Readiness Reporter.

Makes artifact-first project management mechanically auditable instead of relying
on a human/agent to notice registry or manifest drift. stdlib-only; reads only
local files; performs NO network, NO GitHub mutation, NO deployment, NO external
effect, and NEVER mutates canonical artifact status.

What it validates (SB-CTL-012 scope):
  1.  ARTIFACT_INDEX.json parses.
  2.  Artifact ids are unique.
  3.  Every status is in the allowed lifecycle vocabulary.
  4.  Every ``depends_on`` reference exists.
  5.  The dependency graph is acyclic.
  6.  Referenced artifact packets (canonical_ref into artifact-packets/) exist.
  7.  Artifact ids referenced by MILESTONE_MANIFEST.md exist in the index.
  8.  A milestone is only "ready" when its required dependencies are ACCEPTED.
  9.  Obviously contradictory registry states are flagged (e.g. ACCEPTED with an
      evidence note saying unresolved/changes-required; ACCEPTED depending on a
      non-ACCEPTED artifact).
  10. Missing canonical refs under social-bots/ are reported where verifiable.
  11. A deterministic readiness report per version/milestone.
  12. V2.0 ENGINEERING READINESS (SB-V20-099) is kept DISTINCT from V2.0
      OPERATIONAL PROMOTION (SB-V20-004); the two are never collapsed.

Usage:
    python3 social-bots/bin/validate_artifacts.py [--repo-root DIR] [--json]
Exit code 0 iff there are no validation errors (warnings do not fail).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ID token as used across the registry/manifest, e.g. SB-V20-099, SB-CTL-012,
# SB-V07-WIN-001, SB-EVD-001.
_ID_RE = re.compile(r"SB-[A-Z0-9]+(?:-[A-Z0-9]+)+")
_VERSION_RE = re.compile(r"\bV\d+\.\d+\b")

DEFAULT_STATUS_VALUES = (
    "PLANNED", "READY", "IN_PROGRESS", "SUBMITTED", "CHANGES_REQUIRED",
    "ACCEPTED", "BLOCKED", "SUPERSEDED", "WITHHELD",
)
ACCEPTED = "ACCEPTED"

# Evidence-note phrases that contradict an ACCEPTED status (check 9). Kept
# specific to avoid false positives on benign text (e.g. "fails closed").
_CONTRADICTION_MARKERS = (
    "unresolved", "changes-required", "changes_required", "changes required",
    "not accepted", "rejected", "blocked pending acceptance",
)


# --------------------------------------------------------------------------- #
# Result container
# --------------------------------------------------------------------------- #
@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    readiness: dict = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.errors

    def error(self, code: str, msg: str) -> None:
        self.errors.append(f"[{code}] {msg}")

    def warn(self, code: str, msg: str) -> None:
        self.warnings.append(f"[{code}] {msg}")

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
            "readiness": self.readiness,
        }


# --------------------------------------------------------------------------- #
# Index-level checks (pure; operate on already-parsed data)
# --------------------------------------------------------------------------- #
def check_unique_ids(artifacts: list[dict], rep: Report) -> None:
    seen: dict[str, int] = {}
    for a in artifacts:
        aid = a.get("id")
        if not aid:
            rep.error("MISSING_ID", f"artifact without an id: {a.get('name')!r}")
            continue
        seen[aid] = seen.get(aid, 0) + 1
    for aid, n in sorted(seen.items()):
        if n > 1:
            rep.error("DUPLICATE_ID", f"artifact id {aid!r} appears {n} times")


def check_statuses(artifacts: list[dict], allowed: set[str], rep: Report) -> None:
    for a in artifacts:
        st = a.get("status")
        if st not in allowed:
            rep.error("INVALID_STATUS",
                      f"{a.get('id')}: status {st!r} not in allowed vocabulary "
                      f"{sorted(allowed)}")


def check_dependencies_exist(artifacts: list[dict], rep: Report) -> None:
    ids = {a.get("id") for a in artifacts}
    for a in artifacts:
        for dep in a.get("depends_on") or []:
            if dep not in ids:
                rep.error("MISSING_DEPENDENCY",
                          f"{a.get('id')}: depends_on {dep!r} which is not in the index")


def find_cycles(artifacts: list[dict]) -> list[list[str]]:
    """Return dependency cycles (each as an ordered id list). Deterministic."""
    graph = {a.get("id"): [d for d in (a.get("depends_on") or [])] for a in artifacts}
    WHITE, GREY, BLACK = 0, 1, 2
    color = {n: WHITE for n in graph}
    cycles: list[list[str]] = []
    stack: list[str] = []

    def dfs(node: str) -> None:
        color[node] = GREY
        stack.append(node)
        for dep in graph.get(node, []):
            if dep not in color:  # missing dep handled elsewhere
                continue
            if color[dep] == GREY:
                # cycle: slice the stack from the first occurrence of dep
                i = stack.index(dep)
                cycles.append(stack[i:] + [dep])
            elif color[dep] == WHITE:
                dfs(dep)
        stack.pop()
        color[node] = BLACK

    for n in sorted(graph):
        if color[n] == WHITE:
            dfs(n)
    # De-duplicate cycles by their normalized node set, keep deterministic order.
    uniq: dict[frozenset, list[str]] = {}
    for c in cycles:
        key = frozenset(c)
        if key not in uniq:
            uniq[key] = c
    return [uniq[k] for k in sorted(uniq, key=lambda s: sorted(s))]


def check_acyclic(artifacts: list[dict], rep: Report) -> None:
    for cyc in find_cycles(artifacts):
        rep.error("DEPENDENCY_CYCLE", "dependency cycle: " + " -> ".join(cyc))


def check_refs_exist(artifacts: list[dict], repo_root: Path | None, rep: Report) -> None:
    """Check 6 + 10: canonical_ref files that live in the repo exist.

    A missing artifact PACKET (canonical_ref under artifact-packets/) is an ERROR
    (check 6). Any other missing canonical_ref under social-bots/ is reported as a
    WARNING (check 10 — report where locally verifiable). Refs are only checked
    when a repo_root is provided (so pure in-memory validation stays possible).
    """
    if repo_root is None:
        return
    for a in artifacts:
        ref = a.get("canonical_ref")
        if not isinstance(ref, str) or not ref:
            continue
        # Only repo-relative refs under social-bots/ are locally verifiable.
        if not ref.startswith("social-bots/"):
            continue
        exists = (repo_root / ref).exists()
        if exists:
            continue
        if "/artifact-packets/" in ref:
            rep.error("MISSING_PACKET",
                      f"{a.get('id')}: referenced packet {ref!r} does not exist")
        else:
            rep.warn("MISSING_CANONICAL_REF",
                     f"{a.get('id')}: canonical_ref {ref!r} does not exist")


def check_contradictions(artifacts: list[dict], rep: Report) -> None:
    """Check 9: obviously contradictory registry states.

    Severity: WARNING. These are inconsistencies the lead should reconcile, but
    they can be legitimately transient during an audit (e.g. a dependency briefly
    re-opened to CHANGES_REQUIRED after its dependents were accepted), so they
    surface loudly without hard-failing CI.
    """
    status = {a.get("id"): a.get("status") for a in artifacts}
    for a in artifacts:
        aid, st = a.get("id"), a.get("status")
        if st != ACCEPTED:
            continue
        # (a) ACCEPTED but an evidence note says unresolved/changes-required.
        for note in a.get("evidence") or []:
            low = str(note).lower()
            hit = next((m for m in _CONTRADICTION_MARKERS if m in low), None)
            if hit:
                rep.warn("CONTRADICTORY_STATE",
                         f"{aid}: status ACCEPTED but evidence note signals "
                         f"{hit!r}: {note!r}")
        # (b) ACCEPTED while a dependency is not ACCEPTED.
        for dep in a.get("depends_on") or []:
            if dep in status and status[dep] != ACCEPTED:
                rep.warn("CONTRADICTORY_STATE",
                         f"{aid}: status ACCEPTED but dependency {dep} is "
                         f"{status[dep]!r} (not ACCEPTED)")


# --------------------------------------------------------------------------- #
# Milestone manifest parsing + readiness (checks 7, 8, 11, 12)
# --------------------------------------------------------------------------- #
@dataclass
class Milestone:
    version: str
    title: str
    engineering_required: list[str] = field(default_factory=list)
    operational_required: list[str] = field(default_factory=list)
    prereq_versions: list[str] = field(default_factory=list)

    @property
    def all_ids(self) -> list[str]:
        out: list[str] = []
        for x in self.engineering_required + self.operational_required:
            if x not in out:
                out.append(x)
        return out


def parse_manifest(text: str) -> list[Milestone]:
    """Parse MILESTONE_MANIFEST.md into ordered milestones.

    Distinguishes the two V2-style buckets by sub-headers within a section:
    a line mentioning 'operational promotion' switches following bullets to the
    operational bucket; 'engineering-readiness' switches them to engineering.
    Absent those, all ids in the section are engineering (default) required.
    """
    milestones: list[Milestone] = []
    cur: Milestone | None = None
    mode = "engineering"
    for raw in text.splitlines():
        line = raw.rstrip()
        m = re.match(r"^##\s+(V\d+\.\d+)\s*[—-]?\s*(.*)$", line)
        if m:
            cur = Milestone(version=m.group(1), title=m.group(2).strip())
            milestones.append(cur)
            mode = "engineering"
            continue
        if cur is None:
            continue
        low = line.lower()
        if "operational promotion" in low or "operational acceptance" in low:
            mode = "operational"
        elif "engineering-readiness" in low or "engineering readiness" in low:
            mode = "engineering"
        # Prerequisite prior-milestone references ("accepted V1.7 checkpoint").
        if "accepted v" in low:
            for v in _VERSION_RE.findall(line):
                if v != cur.version and v not in cur.prereq_versions:
                    cur.prereq_versions.append(v)
        # Collect artifact ids from any content line.
        for aid in _ID_RE.findall(line):
            bucket = (cur.operational_required if mode == "operational"
                      else cur.engineering_required)
            if aid not in bucket:
                bucket.append(aid)
    return milestones


def manifest_referenced_ids(milestones: list[Milestone]) -> list[str]:
    out: list[str] = []
    for ms in milestones:
        for aid in ms.all_ids:
            if aid not in out:
                out.append(aid)
    return out


def check_manifest_refs(milestones: list[Milestone], artifacts: list[dict],
                        rep: Report) -> None:
    # Severity: WARNING, not ERROR. The manifest is a forward-looking roadmap
    # covering versions whose artifacts are registered incrementally, so a
    # not-yet-registered id is expected drift to surface for the lead — not a
    # structural break. (The detection itself is what the SB-CTL-012 acceptance
    # regression asserts.)
    ids = {a.get("id") for a in artifacts}
    for aid in manifest_referenced_ids(milestones):
        if aid not in ids:
            rep.warn("MANIFEST_UNKNOWN_ARTIFACT",
                     f"MILESTONE_MANIFEST references {aid!r} which is not in "
                     f"ARTIFACT_INDEX.json")


def compute_readiness(milestones: list[Milestone], status_by_id: dict[str, str],
                      rep: Report) -> dict:
    """Deterministic per-version readiness (checks 8, 11, 12).

    ENGINEERING readiness and OPERATIONAL promotion are reported as SEPARATE
    booleans and are never collapsed. A required id that is unknown or not
    ACCEPTED is a blocker. Operational readiness additionally requires the
    section's prerequisite milestones to be fully accepted.
    """
    def accepted(aid: str) -> bool:
        return status_by_id.get(aid) == ACCEPTED

    def blockers(ids: list[str]) -> list[dict]:
        return [{"id": i, "status": status_by_id.get(i, "MISSING")}
                for i in ids if not accepted(i)]

    # First pass: engineering/operational self-readiness per version.
    by_version: dict[str, Milestone] = {m.version: m for m in milestones}
    self_ready: dict[str, dict] = {}
    for ms in milestones:
        eng_block = blockers(ms.engineering_required)
        op_block = blockers(ms.operational_required)
        self_ready[ms.version] = {
            "engineering_required": list(ms.engineering_required),
            "operational_required": list(ms.operational_required),
            "engineering_ready_self": bool(ms.engineering_required) and not eng_block,
            "operational_ready_self": bool(ms.operational_required) and not op_block,
            "engineering_blockers": eng_block,
            "operational_blockers": op_block,
            "prereq_versions": list(ms.prereq_versions),
        }

    def all_accepted(version: str) -> bool:
        ms = by_version.get(version)
        if not ms:
            return False
        return all(accepted(i) for i in ms.all_ids) if ms.all_ids else False

    report: dict = {}
    for ms in milestones:
        base = self_ready[ms.version]
        prereqs = ms.prereq_versions
        prereqs_ok = all(all_accepted(v) for v in prereqs)
        unmet_prereqs = [v for v in prereqs if not all_accepted(v)]
        # Engineering readiness is deliberately self-scoped (e.g. SB-V20-099 can
        # be engineering-ready while operational V2.0 stays blocked).
        engineering_ready = base["engineering_ready_self"]
        # Operational promotion also requires prerequisite milestones accepted.
        operational_ready = base["operational_ready_self"] and prereqs_ok
        report[ms.version] = {
            "title": ms.title,
            "engineering_required": base["engineering_required"],
            "operational_required": base["operational_required"],
            "engineering_ready": engineering_ready,
            "operational_ready": operational_ready,
            "engineering_blockers": base["engineering_blockers"],
            "operational_blockers": base["operational_blockers"],
            "prereq_versions": prereqs,
            "unmet_prereq_versions": unmet_prereqs,
        }
    return report


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #
def validate_data(index: dict, manifest_text: str | None = None,
                  repo_root: Path | None = None) -> Report:
    """Validate already-parsed index data (+ optional manifest text/root)."""
    rep = Report()
    artifacts = index.get("artifacts")
    if not isinstance(artifacts, list):
        rep.error("BAD_INDEX", "ARTIFACT_INDEX.json has no 'artifacts' list")
        return rep
    allowed = set(index.get("status_values") or DEFAULT_STATUS_VALUES)

    check_unique_ids(artifacts, rep)
    check_statuses(artifacts, allowed, rep)
    check_dependencies_exist(artifacts, rep)
    check_acyclic(artifacts, rep)
    check_refs_exist(artifacts, repo_root, rep)
    check_contradictions(artifacts, rep)

    if manifest_text is not None:
        milestones = parse_manifest(manifest_text)
        check_manifest_refs(milestones, artifacts, rep)
        status_by_id = {a.get("id"): a.get("status") for a in artifacts}
        rep.readiness = compute_readiness(milestones, status_by_id, rep)
    return rep


def validate_repo(repo_root: Path) -> Report:
    """Load the canonical files from ``repo_root`` and validate them."""
    index_path = repo_root / "social-bots" / "ARTIFACT_INDEX.json"
    manifest_path = repo_root / "social-bots" / "MILESTONE_MANIFEST.md"
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        rep = Report()
        rep.error("INDEX_NOT_FOUND", f"{index_path} not found")
        return rep
    except json.JSONDecodeError as exc:
        rep = Report()
        rep.error("INDEX_PARSE", f"ARTIFACT_INDEX.json failed to parse: {exc}")
        return rep
    manifest_text = manifest_path.read_text(encoding="utf-8") \
        if manifest_path.exists() else None
    return validate_data(index, manifest_text, repo_root)


def _default_repo_root() -> Path:
    # bin -> social-bots -> repo root
    return Path(__file__).resolve().parents[2]


def render_text(rep: Report) -> str:
    lines: list[str] = []
    lines.append("=== Artifact Graph Validation ===")
    lines.append(f"errors:   {len(rep.errors)}")
    lines.append(f"warnings: {len(rep.warnings)}")
    for e in rep.errors:
        lines.append(f"  ERROR   {e}")
    for w in rep.warnings:
        lines.append(f"  WARN    {w}")
    if rep.readiness:
        lines.append("")
        lines.append("=== Readiness by version (engineering vs operational) ===")
        for version in sorted(rep.readiness, key=_version_key):
            r = rep.readiness[version]
            lines.append(f"{version} — {r['title']}")
            lines.append(
                f"    engineering_ready = {r['engineering_ready']}"
                f"  (required: {r['engineering_required'] or '—'})")
            if r["engineering_blockers"]:
                lines.append(f"      eng blockers: {r['engineering_blockers']}")
            lines.append(
                f"    operational_ready = {r['operational_ready']}"
                f"  (required: {r['operational_required'] or '—'})")
            if r["operational_blockers"]:
                lines.append(f"      op blockers: {r['operational_blockers']}")
            if r["unmet_prereq_versions"]:
                lines.append(f"      unmet prereq versions: {r['unmet_prereq_versions']}")
    lines.append("")
    lines.append("RESULT: " + ("PASS" if rep.ok else "FAIL"))
    return "\n".join(lines)


def _version_key(v: str):
    m = re.match(r"V(\d+)\.(\d+)", v)
    return (int(m.group(1)), int(m.group(2))) if m else (999, 999)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Artifact graph validator / readiness reporter")
    ap.add_argument("--repo-root", default=None,
                    help="repository root (defaults to the repo containing this script)")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = ap.parse_args(argv)
    repo_root = Path(args.repo_root).resolve() if args.repo_root else _default_repo_root()
    rep = validate_repo(repo_root)
    if args.json:
        print(json.dumps(rep.to_dict(), indent=2, sort_keys=True))
    else:
        print(render_text(rep))
    return 0 if rep.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
