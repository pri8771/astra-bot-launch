"""SB-R07-044 — independent V0.4 divergence acceptance verifier.

This module is the **comparator**, not an executor. It never constructs a
provider, never spawns a subprocess, never spends, and never self-accepts.

What it proves (when inputs are genuine)
----------------------------------------
Given a prepared matrix, per-case receipts, and a call-budget ledger, it checks:

* the required comparisons exist: P0|P1, P0|P2, P0|P3 (persona) and P0|E0
  (evidence);
* each comparison is materially divergent under ``proposal_divergence``;
* every receipt binds to its prepared case context digest;
* seam fixtures / synthetic kinds / engineering-fixture matrices are rejected
  for any acceptance-path claim;
* self-declared ``sanitized-real-canary`` labels alone are **not** provenance —
  a call-budget ledger must bind each case's context digest to a
  ``proposal_received`` slot under a named manifest.

What it deliberately does not claim
-----------------------------------
A ``ledger_bound_material`` result is necessary engineering evidence for the
lead to consider empirical acceptance. It is never ACCEPTED by this module.
LIVE acceptance remains ChatGPT lead + owner authorization territory
(SB-V04-002 / SB-V04-004 remain authorization-blocked until a real batch runs).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from . import authorization, divergence_prepare as dp
from .reasoning_receipt import REAL_CANARY_KIND, SEAM_FIXTURE_KIND

VERIFIER_ID = "SB-R07-044"
VERIFIER_SCHEMA_VERSION = 1

# Verdicts this verifier may emit. None of them is ACCEPTED.
VERDICT_REJECTED = "REJECTED"
VERDICT_INCOMPLETE = "INCOMPLETE_AWAITING_LIVE_RECEIPTS"
VERDICT_LEDGER_BOUND_MATERIAL = "LEDGER_BOUND_MATERIAL_ENGINEERING"


@dataclass
class VerifierInputs:
    matrix: dp.PreparedMatrix
    receipts: dict[str, dict]
    budget: authorization.CallBudget | None
    matrix_path: str | None = None
    receipts_dir: str | None = None
    budget_home: str | None = None


def load_receipts_dir(receipts_dir: str | Path) -> dict[str, dict]:
    """Load ``{P0,P1,P2,P3,E0}.json`` from a directory. Missing files stay missing."""
    root = Path(receipts_dir)
    out: dict[str, dict] = {}
    for case_id, *_ in dp.CASE_SPECS:
        path = root / f"{case_id}.json"
        if path.exists():
            out[case_id] = json.loads(path.read_text(encoding="utf-8"))
    return out


def load_inputs(*, matrix_path: str | Path, receipts_dir: str | Path,
                budget_home: str | Path | None = None,
                prompts_dir: str | Path | None = None) -> VerifierInputs:
    """Independently load a committed evidence bundle from disk."""
    matrix_path = Path(matrix_path)
    prompts = prompts_dir
    if prompts is None:
        sibling = matrix_path.parent / "prompts"
        prompts = sibling if sibling.is_dir() else None
    matrix = dp.load_prepared(matrix_path, prompts)
    receipts = load_receipts_dir(receipts_dir)
    budget = None
    if budget_home is not None:
        budget = authorization.CallBudget(matrix.run_scope, len(matrix.cases),
                                          home=budget_home)
    return VerifierInputs(
        matrix=matrix, receipts=receipts, budget=budget,
        matrix_path=str(matrix_path), receipts_dir=str(receipts_dir),
        budget_home=str(budget_home) if budget_home is not None else None,
    )


def _independent_rejections(matrix: dp.PreparedMatrix,
                            receipts: dict[str, dict]) -> list[str]:
    """Hard rejects that self-declared labels must never wash away."""
    rejects: list[str] = []
    if not matrix.acceptance_eligible:
        rejects.append(
            "prepared matrix is not acceptance_eligible (engineering-fixture "
            "snapshots or other prepare-time honesty flags); fixture matrices "
            "cannot back LIVE divergence acceptance")
        for reason in matrix.engineering_only_reasons:
            rejects.append(f"matrix engineering_only_reason: {reason}")

    required_ids = {c[0] for c in dp.CASE_SPECS}
    for case_id in sorted(required_ids):
        receipt = receipts.get(case_id)
        if receipt is None:
            rejects.append(f"{case_id}: receipt absent")
            continue
        kind = receipt.get("receipt_kind")
        if kind == SEAM_FIXTURE_KIND:
            rejects.append(
                f"{case_id}: receipt_kind={SEAM_FIXTURE_KIND!r} is a seam "
                f"fixture; fixtures/replay cannot prove live adaptive divergence")
        elif kind != REAL_CANARY_KIND:
            rejects.append(
                f"{case_id}: receipt_kind={kind!r} is not {REAL_CANARY_KIND!r}; "
                f"rejected for acceptance-path verification")
        provider = str(receipt.get("provider_id") or "")
        if "fixture" in provider.lower() or "synthetic" in provider.lower():
            rejects.append(
                f"{case_id}: provider_id={provider!r} looks synthetic/fixture; "
                f"rejected")
        if receipt.get("adaptive") is not True:
            rejects.append(f"{case_id}: adaptive!=true; rejected")
    return rejects


def _required_comparisons_ok(report: dict) -> tuple[bool, list[str]]:
    """The four plan comparisons must be present with the expected variables."""
    expected = {f"{a}|{b}": var for a, b, var in dp.REQUIRED_COMPARISONS}
    seen = {c["comparison"]: c.get("variable") for c in report.get("comparisons", [])}
    errs: list[str] = []
    for key, var in expected.items():
        if key not in seen:
            errs.append(f"required comparison {key} missing from report")
        elif seen[key] != var:
            errs.append(f"comparison {key} variable={seen[key]!r}, expected {var!r}")
    return (not errs), errs


def verify(matrix: dp.PreparedMatrix, receipts: dict[str, dict],
           budget: authorization.CallBudget | None = None,
           *, source: dict | None = None) -> dict:
    """Run the independent comparator. Never returns an ACCEPTED claim."""
    report = dp.divergence_report(matrix, receipts, budget=budget)
    independent = _independent_rejections(matrix, receipts)
    comps_ok, comp_errs = _required_comparisons_ok(report)
    independent.extend(comp_errs)

    label_only_real = bool(report.get("all_receipts_real_adaptive"))
    binding = report.get("call_slot_binding") or {}
    ledger_bound = bool(
        binding.get("checked")
        and not binding.get("unbound_cases")
        and budget is not None
    )
    if budget is None:
        independent.append(
            "no call-budget ledger supplied; self-declared receipt labels are "
            "not provenance")
        ledger_bound = False
    elif binding.get("unbound_cases"):
        independent.append(
            "call-budget ledger does not bind every case to a proposal_received "
            f"slot: {binding['unbound_cases']}")
        ledger_bound = False

    material = bool(report.get("all_comparisons_material"))

    hard_reject = any(
        ("seam fixture" in r)
        or ("synthetic/fixture" in r)
        or ("adaptive!=true" in r)
        or ("not acceptance_eligible" in r)
        or ("receipt_kind=" in r and "absent" not in r and REAL_CANARY_KIND not in r)
        for r in independent
    ) or any("does not bind" in e for e in report.get("errors", []))

    if hard_reject:
        verdict = VERDICT_REJECTED
    elif (
        material and ledger_bound and label_only_real and comps_ok
        and not independent and not report.get("errors")
    ):
        verdict = VERDICT_LEDGER_BOUND_MATERIAL
    else:
        verdict = VERDICT_INCOMPLETE

    # Belt: never claim lead acceptance.
    return {
        "schema_version": VERIFIER_SCHEMA_VERSION,
        "verifier_id": VERIFIER_ID,
        "source": source or {},
        "required_comparisons": [list(c) for c in dp.REQUIRED_COMPARISONS],
        "required_comparisons_present": comps_ok,
        "divergence_report": report,
        "independent_rejections": independent,
        "self_declared_real_labels_alone": label_only_real and not ledger_bound,
        "ledger_bound": ledger_bound,
        "all_comparisons_material": material,
        "verdict": verdict,
        "acceptance_claim": False,
        "acceptance_authority": "ChatGPT lead — this verifier never self-accepts",
        "live_model_call_performed": False,
        "evidence_class": "ENGINEERING",
        "note": (
            "LEDGER_BOUND_MATERIAL is necessary evidence for lead review of a "
            "completed live batch; it is not ACCEPTED and not a version promotion."
            if verdict == VERDICT_LEDGER_BOUND_MATERIAL else
            "No LIVE acceptance claim. Fixtures/replay/self-declared provenance "
            "are rejected for acceptance-path use."
        ),
    }


def verify_from_paths(*, matrix_path: str | Path, receipts_dir: str | Path,
                      budget_home: str | Path | None = None,
                      prompts_dir: str | Path | None = None) -> dict:
    """CLI/audit entry: load committed paths and verify independently."""
    inputs = load_inputs(matrix_path=matrix_path, receipts_dir=receipts_dir,
                         budget_home=budget_home, prompts_dir=prompts_dir)
    return verify(
        inputs.matrix, inputs.receipts, inputs.budget,
        source={
            "matrix_path": inputs.matrix_path,
            "receipts_dir": inputs.receipts_dir,
            "budget_home": inputs.budget_home,
        },
    )
