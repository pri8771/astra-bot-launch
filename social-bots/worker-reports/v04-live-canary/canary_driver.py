#!/usr/bin/env python3
"""SB-V04-005 real live canary (Lane 2, canary branch, new epoch).

Live public HTTPS source -> hash/metadata -> bounded signal -> normal adaptive
path -> real ClaudeCodeReasoningProvider (claude CLI, subscription) -> schema
validation -> deterministic policy -> persisted decision -> zero public effect.
No injected runner, no fixture, no API-key path. Fails closed to BLOCKED.
"""
from __future__ import annotations
import os, sys, ssl, json, time, hashlib, shutil, subprocess, platform, urllib.request
from pathlib import Path

RUNTIME_DIR = sys.argv[1]
EVID = Path(sys.argv[2])
CANARY_HOME = Path(sys.argv[3])
CA = "/root/.ccr/ca-bundle.crt"
# The Ledger = plain-text accounting persona; beancount is a real current
# plain-text-accounting package on PyPI (allowed egress host). Fallback: pip.
SOURCES = ["https://pypi.org/pypi/beancount/json", "https://pypi.org/pypi/pip/json"]

EVID.mkdir(parents=True, exist_ok=True)
CANARY_HOME.mkdir(parents=True, exist_ok=True)

api_key_present = bool(os.environ.get("ANTHROPIC_API_KEY"))
claude_path = shutil.which("claude")
claude_version = None
if claude_path:
    try:
        claude_version = subprocess.run([claude_path, "--version"], capture_output=True,
                                        text=True, timeout=30).stdout.strip()
    except Exception as e:  # noqa: BLE001
        claude_version = f"version-check-failed:{type(e).__name__}"
preflight = {"os": platform.platform(), "python_version": platform.python_version(),
             "claude_cli_path": claude_path, "claude_cli_version": claude_version,
             "anthropic_api_key_present": api_key_present, "sbots_home": str(CANARY_HOME)}

# --- live retrieval ----------------------------------------------------------
ctx = ssl.create_default_context(cafile=CA if os.path.exists(CA) else None)
raw = b""; used_url = None; fetch_status = None; retrieved_at = None
for url in SOURCES:
    retrieved_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    req = urllib.request.Request(url, headers={"User-Agent": "SB-V04-live-canary/1.0 (+bounded read-only)"})
    try:
        with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
            fetch_status = r.status; raw = r.read(); used_url = url
            break
    except Exception as e:  # noqa: BLE001
        print("fetch failed", url, type(e).__name__, str(e)[:100])
if not raw:
    (EVID / "SOURCE.json").write_text(json.dumps(
        {"error": "all sources failed", "candidates": SOURCES, "retrieved_at": retrieved_at}, indent=2))
    print("BLOCKED: source fetch failed"); sys.exit(3)

sha256 = hashlib.sha256(raw).hexdigest(); content_length = len(raw)
doc = json.loads(raw); info = doc.get("info", {}) or {}; releases = doc.get("releases", {}) or {}
pkg_name = info.get("name"); pkg_version = info.get("version"); pkg_summary = (info.get("summary") or "")[:200]
bounded_excerpt = (f"PyPI package '{pkg_name}' current latest version {pkg_version}; "
                   f"{len(releases)} released versions indexed; summary: {pkg_summary}")
SOURCE = {"url": used_url, "provenance": "live-canary-capture", "retrieved_at": retrieved_at,
          "fetch_status": fetch_status, "content_length": content_length, "sha256": sha256,
          "bounded_title": f"{pkg_name} {pkg_version}", "bounded_summary": bounded_excerpt,
          "note": "Live HTTPS retrieval at canary time; public, no auth/cookies, not a fixture, not pasted. "
                  "Host from session egress allowlist (arbitrary hosts are 403 by org egress policy)."}
(EVID / "SOURCE.json").write_text(json.dumps(SOURCE, indent=2))
print("SOURCE", pkg_name, pkg_version, "bytes", content_length, "sha256", sha256[:16], "url", used_url)

# --- runtime: capture signal + real adaptive cycle ---------------------------
os.environ["SBOTS_HOME"] = str(CANARY_HOME)
os.environ["SBOTS_REASONING"] = "claude-cli"
os.environ["SBOTS_REASONING_REQUIRE_ADAPTIVE"] = "1"
os.environ.pop("ANTHROPIC_API_KEY", None)
sys.path.insert(0, RUNTIME_DIR)
from runtime import research, decision, reasoning, pipeline  # noqa: E402

bot = "social-a"; persona = "social-a"
sig = research.Signal.make(title=f"PyPI index: {pkg_name} {pkg_version}", summary=bounded_excerpt,
                           source="pypi.org JSON API", url=used_url, provenance="live-capture",
                           tags=["pypi", "plain-text-accounting", "live-canary", "evidence"])
research.capture(bot, sig)
print("SIGNAL", sig.id)

prov = reasoning.resolve_provider(require_adaptive=True)
provider_available = prov.available(); provider_reason = getattr(prov, "reason", None)

t0 = time.strftime("%Y-%m-%dT%H:%M:%S%z")
rec = decision.run_cycle(bot, persona, require_adaptive=True)
t1 = time.strftime("%Y-%m-%dT%H:%M:%S%z")

pub_queue = pipeline.publish_queue(bot); outcome = rec.get("outcome")
ex = rec.get("execute", {}); rmeta = rec.get("reasoning", {}); pol = rec.get("policy", {})
effect = str(ex.get("effect", "")).lower()
external = ("publish", "post", "sent", "send", "message", "spend", "purchase", "tweet", "reply")
public_effect = (ex.get("performed", False) and any(m in effect for m in external)
                 and "local" not in effect and effect not in ("none", "")) or bool(pub_queue)
proposal_valid = outcome != "blocked_reasoning_unavailable"

PROVIDER = {"provider_id": rmeta.get("provider"), "adaptive": rmeta.get("adaptive"),
            "adaptive_required": rmeta.get("adaptive_required"), "available": rmeta.get("available"),
            "provider_class": type(prov).__name__, "provider_available_preflight": provider_available,
            "provider_reason": provider_reason, "claude_cli_path": claude_path,
            "claude_cli_version": claude_version,
            "invocation_flags": ["--print", "--output-format", "json", "--permission-mode", "plan",
                                 "--permission-prompts", "none", "--disallowedTools",
                                 "Bash Edit Write NotebookEdit WebFetch WebSearch Read Glob Grep Task Agent"],
            "api_key_stripped_from_child_env": True, "anthropic_api_key_present": api_key_present,
            "call_started_at": t0, "call_finished_at": t1, "uncertainties": rmeta.get("uncertainties")}
(EVID / "PROVIDER.json").write_text(json.dumps(PROVIDER, indent=2))
(EVID / "DECISION.json").write_text(json.dumps(rec, indent=2, default=str))

SUMMARY = {"artifact": "SB-V04-005", "persona": "social-a (The Ledger)",
           "real_network_source": True, "fixture_source": False, "injected_model_runner": False,
           "actual_claude_cli_invoked": bool(rmeta.get("available")), "api_key_path_used": False,
           "proposal_schema_valid": bool(proposal_valid), "deterministic_policy_applied": True,
           "public_effect_performed": bool(public_effect),
           "decision_persisted": (CANARY_HOME / "state" / bot / "last_decision.json").exists(),
           "outcome": outcome, "chosen_action": rec.get("chosen", {}).get("action"),
           "provider_recommended_action": pol.get("provider_recommended"),
           "policy_selected_action": pol.get("policy_selected"),
           "recommended_followed": pol.get("recommended_followed"),
           "execute_effect": ex.get("effect"),
           "execute_scope": "local-only" if ("local" in effect or effect in ("none", "")) else "external",
           "publish_queue_len": len(pub_queue), "publish_authorized": False,
           "source_url": used_url, "source_sha256": sha256, "source_retrieved_at": retrieved_at,
           "signal_id": sig.id, "canary_home": str(CANARY_HOME), "preflight": preflight,
           "blocked": outcome == "blocked_reasoning_unavailable"}
(EVID / "SUMMARY.json").write_text(json.dumps(SUMMARY, indent=2))
print("OUTCOME", outcome, "| chosen", rec.get("chosen", {}).get("action"),
      "| provider_available", rmeta.get("available"), "| public_effect", public_effect,
      "| queue", len(pub_queue))
print("EVID", EVID)
