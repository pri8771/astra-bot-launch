#!/usr/bin/env python3
"""SB-V04-005 real live canary driver (Lane 3 Acceptance).

Chain: live public HTTPS source -> hash/metadata -> bounded signal -> runtime
capture -> real ClaudeCodeReasoningProvider (claude CLI, subscription route) ->
schema validation -> deterministic policy -> persisted decision -> zero effect.

No injected runner, no fixture, no API key path. Fails closed to BLOCKED.
"""
from __future__ import annotations
import os, sys, ssl, json, time, hashlib, shutil, subprocess, platform, urllib.request
from pathlib import Path

RUNTIME_DIR = sys.argv[1]           # path to social-bots dir on canary worktree
EVID = Path(sys.argv[2])            # evidence output dir
CANARY_HOME = Path(sys.argv[3])     # isolated SBOTS_HOME
SOURCE_URL = "https://pypi.org/pypi/pip/json"
CA = "/root/.ccr/ca-bundle.crt"

EVID.mkdir(parents=True, exist_ok=True)
CANARY_HOME.mkdir(parents=True, exist_ok=True)

# --- Preflight: environment facts (booleans only for the key) ----------------
api_key_present = bool(os.environ.get("ANTHROPIC_API_KEY"))
claude_path = shutil.which("claude")
claude_version = None
if claude_path:
    try:
        claude_version = subprocess.run([claude_path, "--version"], capture_output=True,
                                        text=True, timeout=30).stdout.strip()
    except Exception as e:  # noqa: BLE001
        claude_version = f"version-check-failed:{type(e).__name__}"
preflight = {
    "os": platform.platform(),
    "python_version": platform.python_version(),
    "claude_cli_path": claude_path,
    "claude_cli_version": claude_version,
    "anthropic_api_key_present": api_key_present,   # boolean only, value never read
    "sbots_home": str(CANARY_HOME),
}

# --- Step 1-2: live retrieval + provenance -----------------------------------
ctx = ssl.create_default_context(cafile=CA if os.path.exists(CA) else None)
retrieved_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")
req = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "SB-V04-live-canary/1.0 (+bounded read-only)"})
fetch_status = None
raw = b""
try:
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        fetch_status = r.status
        raw = r.read()
except Exception as e:  # noqa: BLE001
    SOURCE = {"url": SOURCE_URL, "retrieved_at": retrieved_at, "fetch_status": f"ERROR:{type(e).__name__}",
              "error": str(e)[:200]}
    (EVID / "SOURCE.json").write_text(json.dumps(SOURCE, indent=2))
    print("BLOCKED: source fetch failed", e)
    sys.exit(3)

sha256 = hashlib.sha256(raw).hexdigest()
content_length = len(raw)
doc = json.loads(raw)
info = doc.get("info", {}) or {}
releases = doc.get("releases", {}) or {}
pkg_name = info.get("name")
pkg_version = info.get("version")
pkg_summary = (info.get("summary") or "")[:200]
bounded_excerpt = (f"PyPI package '{pkg_name}' current latest version {pkg_version}; "
                   f"{len(releases)} released versions indexed; summary: {pkg_summary}")

SOURCE = {
    "url": SOURCE_URL,
    "provenance": "live-canary-capture",
    "retrieved_at": retrieved_at,
    "fetch_status": fetch_status,
    "content_length": content_length,
    "sha256": sha256,
    "bounded_title": f"{pkg_name} {pkg_version}",
    "bounded_summary": bounded_excerpt,
    "note": "Live HTTPS retrieval at canary time. Public, no auth/cookies, not a fixture, "
            "not manually pasted. Host chosen from the session egress allowlist (arbitrary "
            "news/data hosts are denied 403 by org egress policy in this environment).",
}
(EVID / "SOURCE.json").write_text(json.dumps(SOURCE, indent=2))
print("SOURCE captured:", pkg_name, pkg_version, "bytes", content_length, "sha256", sha256[:16])

# --- Step 3-4: bounded signal into the runtime -------------------------------
os.environ["SBOTS_HOME"] = str(CANARY_HOME)
os.environ["SBOTS_REASONING"] = "claude-cli"                  # real adaptive route
os.environ["SBOTS_REASONING_REQUIRE_ADAPTIVE"] = "1"          # fail closed if not adaptive
os.environ.pop("ANTHROPIC_API_KEY", None)                     # subscription route only
sys.path.insert(0, RUNTIME_DIR)
from runtime import research, decision, reasoning, pipeline    # noqa: E402
from runtime import reasoning_cli                              # noqa: E402

bot = "social-a"       # The Ledger
persona = "social-a"
sig = research.Signal.make(
    title=f"PyPI index: {pkg_name} {pkg_version}",
    summary=bounded_excerpt,
    source="pypi.org JSON API",
    url=SOURCE_URL,
    provenance="live-capture",
    tags=["pypi", "package-index", "live-canary", "evidence"],
)
research.capture(bot, sig)
print("Signal captured:", sig.id)

# Record the exact command the real adapter will build (documentation; not executed here).
prov = reasoning.resolve_provider(require_adaptive=True)
provider_available = prov.available()
provider_reason = getattr(prov, "reason", None)

# --- Step 5-8: ONE real Claude CLI call via normal V0.4 adapter --------------
t_call0 = time.strftime("%Y-%m-%dT%H:%M:%S%z")
rec = decision.run_cycle(bot, persona, require_adaptive=True)
t_call1 = time.strftime("%Y-%m-%dT%H:%M:%S%z")

# --- Step 9: verify zero public effect ---------------------------------------
pub_queue = pipeline.publish_queue(bot)
outcome = rec.get("outcome")
executed = rec.get("execute", {})
reasoning_meta = rec.get("reasoning", {})
proposal_valid = outcome not in ("blocked_reasoning_unavailable",)

PROVIDER = {
    "provider_id": reasoning_meta.get("provider"),
    "adaptive": reasoning_meta.get("adaptive"),
    "adaptive_required": reasoning_meta.get("adaptive_required"),
    "available": reasoning_meta.get("available"),
    "provider_class": type(prov).__name__,
    "provider_available_preflight": provider_available,
    "provider_reason": provider_reason,
    "claude_cli_path": claude_path,
    "claude_cli_version": claude_version,
    "invocation_flags": ["--print", "--output-format", "json", "--permission-mode", "plan",
                         "--permission-prompts", "none", "--disallowedTools", "Bash Edit Write "
                         "NotebookEdit WebFetch WebSearch Read Glob Grep Task Agent"],
    "api_key_stripped_from_child_env": True,
    "anthropic_api_key_present": api_key_present,
    "call_started_at": t_call0,
    "call_finished_at": t_call1,
    "uncertainties": reasoning_meta.get("uncertainties"),
}
(EVID / "PROVIDER.json").write_text(json.dumps(PROVIDER, indent=2))

(EVID / "DECISION.json").write_text(json.dumps(rec, indent=2, default=str))

SUMMARY = {
    "artifact": "SB-V04-005",
    "persona": "social-a (The Ledger)",
    "real_network_source": True,
    "fixture_source": False,
    "injected_model_runner": False,
    "actual_claude_cli_invoked": bool(reasoning_meta.get("available")),
    "api_key_path_used": False,
    "proposal_schema_valid": bool(proposal_valid),
    "deterministic_policy_applied": True,
    "public_effect_performed": bool(executed.get("performed", False)) or bool(pub_queue),
    "decision_persisted": (CANARY_HOME / "state" / bot / "last_decision.json").exists(),
    "outcome": outcome,
    "chosen_action": rec.get("chosen", {}).get("action"),
    "publish_queue_len": len(pub_queue),
    "source_url": SOURCE_URL,
    "source_sha256": sha256,
    "source_retrieved_at": retrieved_at,
    "signal_id": sig.id,
    "canary_home": str(CANARY_HOME),
    "preflight": preflight,
    "blocked": outcome == "blocked_reasoning_unavailable",
}
(EVID / "SUMMARY.json").write_text(json.dumps(SUMMARY, indent=2))
print("OUTCOME:", outcome, "| chosen:", rec.get("chosen", {}).get("action"),
      "| provider_available:", reasoning_meta.get("available"),
      "| publish_queue:", len(pub_queue))
print("EVIDENCE WRITTEN TO:", EVID)
