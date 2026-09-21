"""SB-V04-002 — real adaptive reasoning via a bounded Claude Code CLI subprocess.

This is the ADAPTIVE reasoning route (``adaptive = True``). It invokes the locally
installed, already-authenticated Claude Code CLI **non-interactively** with a
bounded reasoning prompt, NO effect tools, and structured JSON output, then parses
and returns a ``ReasoningProposal`` that the engine independently schema-validates
(``reasoning.validate_proposal``) before anything is scored or executed.

Hard boundaries (enforced here, not just documented):

* **No effect surface.** The subprocess is launched with `--print` (non-interactive),
  every tool disallowed, and permission prompts denied, so it cannot publish,
  message, spend, mutate credentials, run commands, fetch URLs or touch any social
  platform. It only emits text.
* **Billing guard.** If ``ANTHROPIC_API_KEY`` is present the provider is UNAVAILABLE
  and ``propose`` fails closed — that env var can route Claude Code to paid API
  billing, and this artifact must use the existing subscription only. The value is
  never read beyond a boolean presence check, never logged. ``--bare`` is likewise
  never used because it forces API-key/apiKeyHelper auth.
* **Fail closed on everything.** CLI missing, not authenticated, usage/quota
  exhausted, timeout, non-zero exit, empty output, invalid JSON, or a proposal
  that fails schema validation all resolve to "no usable proposal" (``None``), and
  the engine records BLOCKED_REASONING_UNAVAILABLE / _INVALID with the signal left
  pending. There is NO deterministic fake fallback pretending to be adaptive.
* **No hidden chain-of-thought stored.** The prompt asks for ONLY the strict JSON
  envelope (concise rationale, alternatives, uncertainties, evidence refs). We
  never request, parse or persist a reasoning trace.

A ``runner`` seam makes the subprocess injectable, so unit tests and CI exercise
every path (including the success mapping) WITHOUT launching a real model call or
incurring any spend.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass

from .reasoning import Candidate, ReasoningContext, ReasoningProposal, ACTION_VOCAB

DEFAULT_TIMEOUT_S = 60
# Tools explicitly denied to the reasoning subprocess (belt-and-suspenders; we
# also deny-by-default via permission mode). Any effect-capable tool is listed.
_DENIED_TOOLS = [
    "Bash", "Edit", "Write", "NotebookEdit", "WebFetch", "WebSearch",
    "Read", "Glob", "Grep", "Task", "Agent",
]


class CLIUnavailable(Exception):
    pass


@dataclass
class CLIResult:
    returncode: int
    stdout: str
    stderr: str


def _default_cli_runner(prompt: str, *, timeout_s: int, model: str | None) -> CLIResult:
    """Launch the real Claude Code CLI, non-interactive, with no effect tools.

    Uses the subscription auth (OAuth/keychain) — deliberately NOT ``--bare``,
    which would force API-key auth. Raises ``CLIUnavailable`` if the binary is
    missing; propagates ``subprocess.TimeoutExpired`` on timeout.
    """
    exe = shutil.which("claude")
    if not exe:
        raise CLIUnavailable("claude CLI not found on PATH")
    cmd = [
        exe, "--print",
        "--output-format", "json",
        "--permission-mode", "plan",     # cannot take effect actions
        "--permission-prompts", "none",  # any permission request is auto-denied
        "--disallowedTools", *_DENIED_TOOLS,
    ]
    if model:
        cmd += ["--model", model]
    # The prompt is passed on stdin so it never lands in the process table/args.
    proc = subprocess.run(
        cmd, input=prompt, capture_output=True, text=True, timeout=timeout_s,
        # Never inherit an API key into the child: the subscription route only.
        env={k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"},
    )
    return CLIResult(returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)


def _bounded_context(ctx: ReasoningContext) -> dict:
    """The ONLY facts sent to the model — bounded, inert, no secrets/effects."""
    sig = ctx.top_signal or {}
    persona = ctx.persona or {}
    return {
        "persona": {
            "id": persona.get("id"),
            "kind": persona.get("kind"),
            "display_name": persona.get("display_name"),
        },
        "objective": ctx.objective,
        "signal": {
            "id": sig.get("id"),
            "title": sig.get("title"),
            "summary": sig.get("summary"),
            "tags": sig.get("tags", []),
            "provenance": sig.get("provenance"),
            "has_source": bool(sig.get("url") or sig.get("source")),
        },
        "pending_count": ctx.pending_count,
        "is_duplicate": ctx.is_duplicate,
        "prior_hypotheses": int(ctx.state_summary.get("hypotheses", 0)),
        "allowed_actions": list(ACTION_VOCAB),
    }


_PROMPT_TEMPLATE = """\
You are a bounded reasoning function for an autonomous social-content runtime.
You DO NOT act. You only rank candidate actions for the deterministic policy layer.

Given the CONTEXT JSON below, return a SINGLE JSON object and NOTHING else — no
prose, no explanation, no chain-of-thought. Do not use any tools.

Output schema (all numeric fields are floats in [0,1]):
{{
  "alternatives": [
    {{"action": <one of ALLOWED_ACTIONS>, "rationale": <=200 chars,
      "expected_value": f, "expected_learning": f, "relevance": f,
      "confidence": f, "risk": f, "cost": f, "reversibility": f,
      "duplication_risk": f, "evidence_refs": [signal ids or []]}}
  ],
  "recommended_action": <must equal one alternative's action>,
  "uncertainties": [<=3 short strings]
}}

Rules:
- Consider the evidence honestly. Weak/thin/unsourced evidence should favor
  RESEARCH_MORE or NO_ACTION. A duplicate should favor NO_ACTION.
- recommended_action is advisory; include at least NO_ACTION and one other option.
- Never propose PUBLISH/SEND/SPEND/DELETE or any action outside ALLOWED_ACTIONS.
- Cite only evidence ids that appear in CONTEXT; never invent an evidence ref.

ALLOWED_ACTIONS: {allowed}

CONTEXT:
{context}
"""


def prompt_context(ctx: ReasoningContext) -> dict:
    """Public view of the EXACT bounded facts embedded in the production prompt.

    The V0.4 divergence matrix must prove isolation on what is actually sent to
    the model, not only on the coarser digest projection used for receipt
    matching (``reasoning_receipt.bounded_context``, which omits the signal
    summary). Exposing this keeps that check honest without duplicating the
    projection.
    """
    return _bounded_context(ctx)


def build_prompt(ctx: ReasoningContext) -> str:
    bounded = _bounded_context(ctx)
    return _PROMPT_TEMPLATE.format(
        allowed=", ".join(ACTION_VOCAB),
        context=json.dumps(bounded, sort_keys=True, indent=2))


def _extract_model_text(stdout: str) -> str | None:
    """Pull the model's text out of Claude Code's ``--output-format json`` wrapper.

    The wrapper is a JSON object with a ``result`` (or ``text``) field. If the
    output is already the bare JSON envelope, return it as-is. Any parse failure
    returns None (fail closed)."""
    stdout = (stdout or "").strip()
    if not stdout:
        return None
    try:
        wrapper = json.loads(stdout)
    except json.JSONDecodeError:
        return stdout  # maybe already the bare envelope; let the envelope parser try
    if isinstance(wrapper, dict):
        # If this already looks like the bare reasoning envelope, use it directly.
        if isinstance(wrapper.get("alternatives"), list):
            return stdout
        # An explicit error/refusal in the wrapper fails closed.
        if wrapper.get("is_error") or wrapper.get("subtype") in {"error", "error_max_turns"}:
            return None
        for key in ("result", "text", "content"):
            val = wrapper.get(key)
            if isinstance(val, str) and val.strip():
                return val.strip()
        # Some formats nest the text; give up rather than guess (fail closed).
        return None
    return None


def _coerce_candidate(raw: dict) -> Candidate | None:
    if not isinstance(raw, dict):
        return None
    action = raw.get("action")
    if action not in ACTION_VOCAB:
        return None
    payload: dict = {}
    # Carry only an inert signal reference for CREATE_CANDIDATE; the model may not
    # embed executable payload (schema validation independently enforces this).
    if isinstance(raw.get("evidence_refs"), list) and raw["evidence_refs"]:
        payload = {}  # evidence refs are recorded on the record, not the payload
    try:
        return Candidate(
            action=action,
            rationale=str(raw.get("rationale", ""))[:400],
            expected_value=float(raw.get("expected_value")),
            expected_learning=float(raw.get("expected_learning")),
            relevance=float(raw.get("relevance")),
            confidence=float(raw.get("confidence")),
            risk=float(raw.get("risk")),
            cost=float(raw.get("cost")),
            reversibility=float(raw.get("reversibility")),
            duplication_risk=float(raw.get("duplication_risk")),
            payload=payload,
        )
    except (TypeError, ValueError):
        return None


def parse_envelope(text: str, ctx: ReasoningContext) -> ReasoningProposal | None:
    """Parse the model's strict-JSON envelope into a ReasoningProposal.

    Returns None on any structural problem (fail closed). CREATE_CANDIDATE gets
    the real ``top_signal`` attached to its payload by the ENGINE side is not done
    here; instead we attach the bounded signal so downstream execution has the
    evidence, mirroring the deterministic providers. Schema validation is still
    performed by the engine before scoring.
    """
    if not text:
        return None
    try:
        env = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(env, dict) or not isinstance(env.get("alternatives"), list):
        return None
    alts: list[Candidate] = []
    for raw in env["alternatives"]:
        c = _coerce_candidate(raw)
        if c is None:
            return None  # any malformed alternative fails the whole proposal closed
        if c.action == "CREATE_CANDIDATE":
            # Attach the real evidence + draft so the policy can act; the model
            # never supplies executable payload of its own.
            c.payload = {"signal": ctx.top_signal, "draft": ctx.draft}
        alts.append(c)
    if not alts:
        return None
    recommended = env.get("recommended_action")
    if recommended not in ACTION_VOCAB:
        return None
    return ReasoningProposal(
        alternatives=alts,
        recommended_action=recommended,
        uncertainties=[str(u)[:200] for u in (env.get("uncertainties") or [])][:5],
        provider_id="claude-code-subscription-v1",
        adaptive=True,
    )


class ClaudeCodeReasoningProvider:
    """Adaptive provider backed by a bounded, effect-free Claude Code subprocess."""

    provider_id = "claude-code-subscription-v1"
    adaptive = True

    def __init__(self, runner=None, timeout_s: int = DEFAULT_TIMEOUT_S,
                 model: str | None = None):
        self._runner = runner or _default_cli_runner
        self._timeout_s = timeout_s
        self._model = model
        self._last_reason: str | None = None

    @property
    def reason(self) -> str | None:
        return self._last_reason

    def available(self) -> bool:
        # Billing guard: never use the API-key route for this artifact.
        if os.environ.get("ANTHROPIC_API_KEY"):
            self._last_reason = "ANTHROPIC_API_KEY present; subscription-route " \
                                "reasoning disabled to avoid paid API billing"
            return False
        if self._runner is _default_cli_runner and shutil.which("claude") is None:
            self._last_reason = "claude CLI not found on PATH"
            return False
        return True

    def propose(self, ctx: ReasoningContext) -> ReasoningProposal | None:
        # Re-check the billing guard at call time (env can change between calls).
        if os.environ.get("ANTHROPIC_API_KEY"):
            self._last_reason = "ANTHROPIC_API_KEY present; failing closed"
            return None
        prompt = build_prompt(ctx)
        try:
            result = self._runner(prompt, timeout_s=self._timeout_s, model=self._model)
        except CLIUnavailable as exc:
            self._last_reason = f"cli unavailable: {exc}"
            return None
        except subprocess.TimeoutExpired:
            self._last_reason = f"cli timeout after {self._timeout_s}s"
            return None
        except Exception as exc:  # noqa: BLE001 — any launch failure fails closed
            self._last_reason = f"cli launch error: {type(exc).__name__}"
            return None
        if result.returncode != 0:
            # Non-zero exit covers not-authenticated / quota-exhausted / errors.
            self._last_reason = f"cli non-zero exit {result.returncode}"
            return None
        text = _extract_model_text(result.stdout)
        if text is None:
            self._last_reason = "cli produced no parseable result (error/empty/refusal)"
            return None
        proposal = parse_envelope(text, ctx)
        if proposal is None:
            self._last_reason = "model output was not a valid proposal envelope"
            return None
        self._last_reason = None
        return proposal
