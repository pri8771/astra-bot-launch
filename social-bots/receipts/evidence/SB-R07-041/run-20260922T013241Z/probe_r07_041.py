#!/usr/bin/env python3
"""SB-R07-041 — reproduce the LEAD-047 P0 findings on the ACTUAL V1.7 modules.

Usage: python3 probe_r07_041.py <checkout>/social-bots

Runs the same five scenarios the lead's offline excerpt probes covered, but
against the real ``runtime.reasoning`` / ``runtime.decision`` modules of the
given checkout, in a fresh temporary SBOTS_HOME, with harmless sentinel
callables. It never contacts a model, the network or any account. Exit code 0
always; the JSON verdict on stdout says what was observed.

  P1 direct_model_callable_without_grant      sentinel registered, no manifest
  P2 false_fixture_label_authorization_exemption  adaptive=False/fixture labels
  P3 concurrent_one_slot_budget               4 threads, one-slot grant
  P4 reentrant_one_slot_budget                callable re-enters the provider
  P5 same_grant_new_wrappers                  two providers, one-slot grant

On a checkout WITHOUT runtime.model_dispatch (pre-fix) the "one-slot grant"
scenarios have no grant at all: every dispatch there is an unauthorized one.
"""
import json
import os
import sys
import tempfile
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

root = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root))
home = tempfile.mkdtemp(prefix="sbots-probe-")
os.environ["SBOTS_HOME"] = home
os.environ["SBOTS_REASONING"] = "model"
os.environ.pop("ANTHROPIC_API_KEY", None)
os.environ.pop("SBOTS_REASONING_REQUIRE_ADAPTIVE", None)

from runtime import reasoning, decision, research  # noqa: E402

try:
    from runtime import model_dispatch  # noqa: E402
    HAS_GATE = True
except ImportError:
    model_dispatch = None
    HAS_GATE = False

ART, LANE, SCOPE = "SB-PROBE", "windows-core", "probe-scope"


def iso(dt):
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_manifest(directory: Path, run_scope: str, max_calls: int) -> None:
    now = datetime.now(timezone.utc)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "probe.json").write_text(json.dumps({
        "schema_version": "v1", "manifest_id": "PROBE-FIXTURE-0001",
        "created_by": "probe-fixture-not-the-lead", "created_at": iso(now - timedelta(minutes=5)),
        "owner_authorization_ref": "engineering probe fixture; no real owner authorization",
        "artifact_scope": [ART], "run_scope": run_scope, "lane": LANE,
        "provider_mode": "claude-cli", "max_calls": max_calls,
        "expires_at": iso(now + timedelta(hours=1)),
        "retry_allowed": False, "public_effect_allowed": False, "spend_authorized": False,
        "api_key_allowed": False, "injected_runner_allowed": False,
    }), encoding="utf-8")


def ctx():
    return reasoning.ReasoningContext(
        persona={"id": "social-b", "kind": "general", "display_name": "probe"},
        objective="probe", top_signal={"id": "sig-1", "title": "t", "summary": "s",
                                       "tags": ["x"], "provenance": "fixture"},
        pending_count=1, is_duplicate=False, draft={"content_id": "c-1"})


def proposal():
    return reasoning.ReasoningProposal(
        alternatives=[reasoning.no_action("sentinel")], recommended_action="NO_ACTION",
        uncertainties=[], provider_id="sentinel", adaptive=True)


def sentinel():
    calls = []

    def fn(c):
        calls.append(1)
        return proposal()
    fn.calls = calls
    return fn


def scoped(run_scope: str, max_calls: int):
    """Install a one-manifest dispatch scope (post-fix only)."""
    if not HAS_GATE:
        return None
    mdir = Path(home) / "manifests" / run_scope
    write_manifest(mdir, run_scope, max_calls)
    model_dispatch.clear()
    return model_dispatch.configure(ART, LANE, run_scope, manifest_dir=mdir, home=home)


def ledger(run_scope: str):
    if not HAS_GATE:
        return None
    from runtime import authorization
    return authorization.CallBudget(run_scope, 5, home=home).audit()


obs = []

# P1 — direct model callable, no grant, no scope: provider path and engine path.
if HAS_GATE:
    model_dispatch.clear()
fn = sentinel()
reasoning.ModelReasoningProvider(fn).propose(ctx())
provider_dispatches = len(fn.calls)
fn2 = sentinel()
research.capture("social-b", research.Signal.make(
    "sig", "captured", "probe", "https://example.invalid/s", "fixture", ["measurement"]))
reasoning.register_model_callable(fn2)
rec = decision.run_cycle("social-b", "social-b", require_adaptive=True)
reasoning.register_model_callable(None)
obs.append({"probe": "direct_model_callable_without_grant", "expected_safe_dispatches": 0,
            "observed_sentinel_dispatches_provider": provider_dispatches,
            "observed_sentinel_dispatches_engine": len(fn2.calls),
            "engine_outcome": rec.get("outcome"),
            "defect_reproduced": (provider_dispatches + len(fn2.calls)) > 0})

# P2 — caller-supplied labels must not exempt.
fn = sentinel()
fn.adaptive = False
fn.fixture = True
fn.engineering_only = True
fn.__sbots_injected_runner__ = True
reasoning.ModelReasoningProvider(fn).propose(ctx())
obs.append({"probe": "false_fixture_label_authorization_exemption", "expected_safe_dispatches": 0,
            "observed_sentinel_dispatches": len(fn.calls), "defect_reproduced": len(fn.calls) > 0})

# P3 — concurrency against a one-slot grant (pre-fix: no grant exists at all).
scope = scoped("probe-concurrent", 1)
fn = sentinel()
n = 4
barrier = threading.Barrier(n)
errors, refused = [], []
lock = threading.Lock()


def race():
    p = reasoning.ModelReasoningProvider(fn)
    barrier.wait(timeout=10)
    try:
        out = p.propose(ctx())
        if out is None and p.reason:
            with lock:
                refused.append(p.reason[:80])
    except Exception as exc:                          # noqa: BLE001
        with lock:
            errors.append(type(exc).__name__)


threads = [threading.Thread(target=race) for _ in range(n)]
for t in threads:
    t.start()
for t in threads:
    t.join(timeout=20)
obs.append({"probe": "concurrent_one_slot_budget", "threads": n, "expected_max_dispatches": 1,
            "grant_present": scope is not None, "observed_sentinel_dispatches": len(fn.calls),
            "refusals": len(refused), "errors": errors, "ledger": ledger("probe-concurrent"),
            "defect_reproduced": len(fn.calls) > 1})

# P4 — reentry: the callable re-enters its own provider.
scope = scoped("probe-reentrant", 5)
state = {"calls": 0}


def reenter(c):
    state["calls"] += 1
    if state["calls"] == 1:
        return holder["p"].propose(c)
    return proposal()


holder = {"p": reasoning.ModelReasoningProvider(reenter)}
holder["p"].propose(ctx())
obs.append({"probe": "reentrant_one_slot_budget", "expected_max_dispatches": 1,
            "grant_present": scope is not None, "observed_sentinel_dispatches": state["calls"],
            "ledger": ledger("probe-reentrant"), "defect_reproduced": state["calls"] > 1})

# P5 — two wrappers over the same callable, one-slot grant.
scope = scoped("probe-wrappers", 1)
fn = sentinel()
reasoning.ModelReasoningProvider(fn).propose(ctx())
reasoning.ModelReasoningProvider(fn).propose(ctx())
obs.append({"probe": "same_grant_new_wrappers", "grant_max_calls": 1 if scope else None,
            "grant_present": scope is not None, "observed_sentinel_dispatches": len(fn.calls),
            "ledger": ledger("probe-wrappers"), "defect_reproduced": len(fn.calls) > 1})

if HAS_GATE:
    model_dispatch.clear()

report = {
    "classification": "REAL_PROCESS_ACTUAL_MODULE_REPRODUCTION",
    "evidence_class": "ENGINEERING (OFFLINE_FIXTURE sentinels, REAL_PROCESS execution)",
    "checkout": str(root), "has_model_dispatch_gate": HAS_GATE,
    "sbots_home": home, "probes": obs,
    "reproduced": sum(1 for o in obs if o["defect_reproduced"]), "total": len(obs),
    "external_model_calls": 0, "network_calls": 0, "public_effects": 0,
    "runtime_acceptance_changed": False,
}
print(json.dumps(report, indent=2, sort_keys=True))
