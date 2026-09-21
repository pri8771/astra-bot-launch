"""Platform selection intelligence (SB-V12-001).

Choose which platform(s) deserve an idea instead of blindly cross-posting.

Rules
-----
- A platform whose account/authority route is unavailable is **BLOCKED** and can
  never be selected for execution.
- A platform that cannot carry the content's required format is **UNSUITABLE**
  (also not selectable).
- Ranking combines persona/platform strategy, real per-platform historical
  performance *when available*, and learning value. When there is no historical
  performance the ranking is explicitly EXPLORATORY with high uncertainty —
  never an invented prior presented as evidence.
- Historical signals are treated as **per-platform** indicators (no cross-
  platform false equivalence, per SB-V13-001).
"""
from __future__ import annotations

# Selection statuses.
ELIGIBLE = "eligible"
BLOCKED = "blocked"        # account/authority unavailable
UNSUITABLE = "unsuitable"  # platform cannot carry the required format

# Per-platform capabilities (what native asset types the platform can carry).
PLATFORM_CAPS = {
    "x":         {"text", "image", "link"},
    "instagram": {"image", "video"},
    "tiktok":    {"video"},
    "reddit":    {"text", "link", "image"},
    "facebook":  {"text", "image", "video", "link"},
}

# Uncertainty levels driven by how much real evidence backs a platform.
UNC_HIGH = "high"      # no historical performance
UNC_MEDIUM = "medium"  # sparse sample
UNC_LOW = "low"        # enough real samples

_UNC_LEARNING = {UNC_HIGH: 1.0, UNC_MEDIUM: 0.5, UNC_LOW: 0.1}

# Component weights.
_W_STRATEGY = 0.4
_W_HISTORY = 0.4
_W_LEARNING = 0.2


def _uncertainty(hist_entry: dict | None) -> str:
    if not hist_entry or hist_entry.get("samples", 0) <= 0:
        return UNC_HIGH
    return UNC_MEDIUM if hist_entry["samples"] < 5 else UNC_LOW


def _score_platform(platform: str, *, strategy_weight: float,
                    hist_entry: dict | None, learning_weight: float) -> dict:
    reasons = []
    unc = _uncertainty(hist_entry)

    strat = max(0.0, min(1.0, strategy_weight))
    reasons.append(f"persona strategy weight {strat:.2f}")

    if unc == UNC_HIGH:
        hist_component = 0.0
        historical_basis = None
        reasons.append("no historical performance; EXPLORATORY ranking "
                       "(no invented prior used as evidence)")
    else:
        perf = float(hist_entry.get("performance", 0.0))
        perf = max(0.0, min(1.0, perf))
        hist_component = perf
        historical_basis = {"performance": perf, "samples": hist_entry["samples"],
                            "note": "per-platform indicator; not cross-platform equivalent"}
        reasons.append(f"per-platform historical performance {perf:.2f} "
                       f"over {hist_entry['samples']} samples")

    learning = _UNC_LEARNING[unc] * max(0.0, learning_weight)
    reasons.append(f"learning value {learning:.2f} (uncertainty={unc})")

    score = (_W_STRATEGY * strat + _W_HISTORY * hist_component
             + _W_LEARNING * min(1.0, learning))
    return {"score": round(score, 6), "reasons": reasons,
            "uncertainty": unc, "historical_basis": historical_basis}


def select_platforms(*, persona_strategy: dict, content_format: str,
                     availability: dict, history: dict | None = None,
                     learning_weight: float = 1.0) -> dict:
    """Rank platforms for a piece of content.

    - ``persona_strategy``: {platform: weight 0..1} the persona targets.
    - ``content_format``: the required native asset type (e.g. "video", "text").
    - ``availability``: {platform: {"account_available": bool, "authorized": bool,
      "reason": str}}.
    - ``history``: optional {platform: {"performance": 0..1, "samples": n}} of
      real per-platform metrics. Absent/empty => explicit uncertainty.
    """
    history = history or {}
    results = []

    for platform in sorted(set(persona_strategy) | set(availability)):
        avail = availability.get(platform, {})
        account_ok = bool(avail.get("account_available"))
        authorized = bool(avail.get("authorized"))

        # 1) Availability/authority gate first — BLOCKED can never be selected.
        if not account_ok or not authorized:
            results.append({
                "platform": platform, "status": BLOCKED, "score": None,
                "reasons": [avail.get("reason") or "account/authority route unavailable"],
                "uncertainty": None, "historical_basis": None,
                "selectable": False})
            continue

        # 2) Format suitability.
        if content_format not in PLATFORM_CAPS.get(platform, set()):
            results.append({
                "platform": platform, "status": UNSUITABLE, "score": None,
                "reasons": [f"platform cannot carry required format {content_format!r}"],
                "uncertainty": None, "historical_basis": None,
                "selectable": False})
            continue

        # 3) Eligible — score it.
        scored = _score_platform(
            platform, strategy_weight=float(persona_strategy.get(platform, 0.0)),
            hist_entry=history.get(platform), learning_weight=learning_weight)
        results.append({
            "platform": platform, "status": ELIGIBLE,
            "score": scored["score"], "reasons": scored["reasons"],
            "uncertainty": scored["uncertainty"],
            "historical_basis": scored["historical_basis"],
            "selectable": True})

    eligible = [r for r in results if r["status"] == ELIGIBLE]
    eligible.sort(key=lambda r: r["score"], reverse=True)
    ranked = eligible + [r for r in results if r["status"] != ELIGIBLE]

    return {
        "content_format": content_format,
        "ranked": ranked,
        "selectable": [r["platform"] for r in eligible],
        "blocked": [r["platform"] for r in results if r["status"] == BLOCKED],
        "unsuitable": [r["platform"] for r in results if r["status"] == UNSUITABLE],
        "any_historical_basis": any(r.get("historical_basis") for r in eligible),
    }
