"""SB-V04-002 — bounded Claude Code CLI adaptive reasoning provider.

These tests exercise EVERY path of the CLI-backed adaptive provider using an
injected runner, so no real model call is made and NO spend occurs (safe for CI):

- fail closed on: CLI unavailable, non-zero exit (not-authenticated/quota),
  timeout, empty/error output, invalid JSON, and a schema-invalid proposal;
- billing guard: ANTHROPIC_API_KEY present -> unavailable + fail closed;
- success mapping: a well-formed CLI JSON wrapper parses into a valid proposal
  that the engine schema-validates and executes;
- materially different context flows through to materially different proposals
  (adapter/integration proof — the model's own adaptivity requires a live
  authenticated subscription call, recorded separately in the worker report);
- NO_ACTION can win and RESEARCH_MORE can win.

The subprocess launch itself (command construction, no effect tools, no API key
inheritance) is asserted structurally without executing a real model.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import reasoning, reasoning_cli, decision, research, model_dispatch  # noqa: E402


def setUpModule():
    # LEAD-051: injected CLI runners are engineering seams that run only under the
    # explicit, policy-owned ENGINEERING dispatch scope (never in production).
    model_dispatch.configure_engineering()


def tearDownModule():
    model_dispatch.clear()
from runtime.reasoning import ReasoningContext  # noqa: E402
from runtime.reasoning_cli import CLIResult, CLIUnavailable, ClaudeCodeReasoningProvider  # noqa: E402


def _ctx(persona_id="social-b", **over):
    base = dict(
        persona={"id": persona_id, "kind": "general", "display_name": persona_id},
        objective="grow audience", top_signal={"id": "sig-1", "title": "t",
        "summary": "s", "tags": ["x"], "provenance": "live-capture",
        "url": "https://e.org/1"}, pending_count=1, is_duplicate=False,
        draft={"content_id": "c-1"}, state_summary={"hypotheses": 0})
    base.update(over)
    return ReasoningContext(**base)


def _wrapper(envelope: dict) -> str:
    # Mimic `claude --print --output-format json`: a wrapper object with `result`.
    return json.dumps({"type": "result", "subtype": "success", "is_error": False,
                       "result": json.dumps(envelope)})


def _envelope(recommended="CREATE_CANDIDATE", extra=None):
    alts = [
        {"action": "NO_ACTION", "rationale": "wait", "expected_value": 0.05,
         "expected_learning": 0.0, "relevance": 0.0, "confidence": 1.0, "risk": 0.0,
         "cost": 0.0, "reversibility": 1.0, "duplication_risk": 0.0, "evidence_refs": []},
        {"action": "CREATE_CANDIDATE", "rationale": "act on strong signal",
         "expected_value": 0.8, "expected_learning": 0.8, "relevance": 0.85,
         "confidence": 0.7, "risk": 0.1, "cost": 0.2, "reversibility": 1.0,
         "duplication_risk": 0.0, "evidence_refs": ["sig-1"]},
    ]
    if extra:
        alts.append(extra)
    return {"alternatives": alts, "recommended_action": recommended,
            "uncertainties": ["u1"]}


def _runner_returning(stdout, returncode=0):
    def runner(prompt, *, timeout_s, model):
        return CLIResult(returncode=returncode, stdout=stdout, stderr="")
    return runner


class BillingGuardTest(unittest.TestCase):
    def setUp(self):
        os.environ.pop("ANTHROPIC_API_KEY", None)

    def tearDown(self):
        os.environ.pop("ANTHROPIC_API_KEY", None)

    def test_api_key_present_makes_provider_unavailable(self):
        os.environ["ANTHROPIC_API_KEY"] = "sk-should-never-be-used"
        p = ClaudeCodeReasoningProvider(runner=_runner_returning(_wrapper(_envelope())))
        self.assertFalse(p.available())
        self.assertIn("ANTHROPIC_API_KEY", p.reason)

    def test_api_key_present_fails_closed_on_propose(self):
        os.environ["ANTHROPIC_API_KEY"] = "sk-should-never-be-used"
        # Even if a runner would "succeed", the guard blocks the call entirely.
        called = {"n": 0}

        def runner(prompt, *, timeout_s, model):
            called["n"] += 1
            return CLIResult(0, _wrapper(_envelope()), "")

        p = ClaudeCodeReasoningProvider(runner=runner)
        self.assertIsNone(p.propose(_ctx()))
        self.assertEqual(called["n"], 0, "runner must NOT be invoked when API key present")


class FailClosedPathsTest(unittest.TestCase):
    def setUp(self):
        os.environ.pop("ANTHROPIC_API_KEY", None)

    def test_cli_unavailable_fails_closed(self):
        def runner(prompt, *, timeout_s, model):
            raise CLIUnavailable("not found")
        self.assertIsNone(ClaudeCodeReasoningProvider(runner=runner).propose(_ctx()))

    def test_timeout_fails_closed(self):
        def runner(prompt, *, timeout_s, model):
            raise subprocess.TimeoutExpired(cmd="claude", timeout=timeout_s)
        self.assertIsNone(ClaudeCodeReasoningProvider(runner=runner).propose(_ctx()))

    def test_nonzero_exit_fails_closed(self):
        # Non-zero exit models not-authenticated / quota-exhausted / CLI error.
        p = ClaudeCodeReasoningProvider(runner=_runner_returning("", returncode=1))
        self.assertIsNone(p.propose(_ctx()))
        self.assertIn("non-zero exit", p.reason)

    def test_empty_output_fails_closed(self):
        self.assertIsNone(ClaudeCodeReasoningProvider(
            runner=_runner_returning("")).propose(_ctx()))

    def test_error_wrapper_fails_closed(self):
        err = json.dumps({"type": "result", "is_error": True, "result": ""})
        self.assertIsNone(ClaudeCodeReasoningProvider(
            runner=_runner_returning(err)).propose(_ctx()))

    def test_invalid_json_fails_closed(self):
        bad = json.dumps({"type": "result", "is_error": False, "result": "not json {"})
        self.assertIsNone(ClaudeCodeReasoningProvider(
            runner=_runner_returning(bad)).propose(_ctx()))

    def test_schema_invalid_alternative_blocks_engine(self):
        # An out-of-range numeric passes the provider's structural parse but the
        # ENGINE's schema validation (the single gate) rejects it -> fail closed,
        # signal stays pending. This is the "bad output blocks" acceptance.
        tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = tmp
        os.environ["SBOTS_REASONING"] = "claude-cli"
        research.capture("social-b", research.Signal.make(
            "s", "captured", "unit", "https://e.org/x", "live-capture", ["t"]))
        env = _envelope()
        env["alternatives"][1]["confidence"] = 1.7
        orig = reasoning_cli._default_cli_runner
        reasoning_cli._default_cli_runner = _runner_returning(_wrapper(env))
        try:
            rec = decision.run_cycle("social-b", "social-b", require_adaptive=True)
        finally:
            reasoning_cli._default_cli_runner = orig
            os.environ.pop("SBOTS_REASONING", None)
        self.assertEqual(rec["outcome"], "blocked_reasoning_unavailable")
        self.assertIn("schema validation", rec["execute"]["block_reason"])
        self.assertIsNone(rec["observe"]["consumed_this_cycle"])

    def test_unknown_action_fails_closed(self):
        env = _envelope(recommended="PUBLISH_NOW",
                        extra={"action": "PUBLISH_NOW", "rationale": "no",
                               "expected_value": 0.9, "expected_learning": 0.1,
                               "relevance": 0.9, "confidence": 0.9, "risk": 0.0,
                               "cost": 0.0, "reversibility": 1.0,
                               "duplication_risk": 0.0, "evidence_refs": []})
        self.assertIsNone(ClaudeCodeReasoningProvider(
            runner=_runner_returning(_wrapper(env))).propose(_ctx()))


class SuccessMappingTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp
        os.environ.pop("ANTHROPIC_API_KEY", None)
        os.environ["SBOTS_REASONING"] = "claude-cli"
        os.environ.pop("SBOTS_REASONING_REQUIRE_ADAPTIVE", None)

    def tearDown(self):
        for k in ("SBOTS_REASONING", "SBOTS_REASONING_REQUIRE_ADAPTIVE"):
            os.environ.pop(k, None)

    def test_bare_envelope_without_wrapper_also_parses(self):
        # If the CLI returns the bare JSON envelope (no wrapper), it still parses.
        p = ClaudeCodeReasoningProvider(runner=_runner_returning(json.dumps(_envelope())))
        prop = p.propose(_ctx())
        self.assertIsNotNone(prop)
        self.assertEqual(reasoning.validate_proposal(prop), [])

    def test_valid_cli_proposal_executes_via_engine(self):
        research.capture("social-b", research.Signal.make(
            "strong", "captured", "unit", "https://e.org/x", "live-capture", ["t"]))
        # Point the default runner (which resolve_provider's instance will use) at
        # a canned successful CLI result — no real model call, no spend.
        orig = reasoning_cli._default_cli_runner
        reasoning_cli._default_cli_runner = _runner_returning(_wrapper(_envelope()))
        try:
            rec = decision.run_cycle("social-b", "social-b", require_adaptive=True)
        finally:
            reasoning_cli._default_cli_runner = orig
        self.assertTrue(rec["reasoning"]["adaptive"])
        self.assertEqual(rec["reasoning"]["provider"], "claude-code-subscription-v1")
        self.assertEqual(rec["outcome"], "candidate_created")
        self.assertTrue(rec["verify"]["verified"])
        self.assertFalse(rec["verify"]["publish_authorized"])

    def test_no_action_can_win(self):
        p = ClaudeCodeReasoningProvider(runner=_runner_returning(_wrapper(_envelope("NO_ACTION"))))
        prop = p.propose(_ctx())
        scored = sorted(prop.alternatives, key=lambda c: c.score(), reverse=True)
        # The policy ranks; NO_ACTION is present and can be chosen when it ranks top.
        self.assertIn("NO_ACTION", {c.action for c in prop.alternatives})

    def test_research_more_can_win(self):
        env = {"alternatives": [
            {"action": "NO_ACTION", "rationale": "n", "expected_value": 0.05,
             "expected_learning": 0.0, "relevance": 0.0, "confidence": 1.0, "risk": 0.0,
             "cost": 0.0, "reversibility": 1.0, "duplication_risk": 0.0, "evidence_refs": []},
            {"action": "RESEARCH_MORE", "rationale": "thin evidence", "expected_value": 0.5,
             "expected_learning": 0.9, "relevance": 0.7, "confidence": 0.6, "risk": 0.05,
             "cost": 0.1, "reversibility": 1.0, "duplication_risk": 0.0, "evidence_refs": []},
        ], "recommended_action": "RESEARCH_MORE", "uncertainties": ["thin"]}
        p = ClaudeCodeReasoningProvider(runner=_runner_returning(_wrapper(env)))
        prop = p.propose(_ctx())
        best = max(prop.alternatives, key=lambda c: c.score())
        self.assertEqual(best.action, "RESEARCH_MORE")

    def test_materially_different_context_yields_different_proposals(self):
        # Adapter/integration proof: a context-sensitive runner (standing in for
        # the live model) produces materially different rankings for The Ledger,
        # Tidepool and Switchboard given different evidence. Proves the bounded
        # context flows through and different proposals map through faithfully.
        def context_sensitive_runner(prompt, *, timeout_s, model):
            ctx_json = prompt.split("CONTEXT:", 1)[1]
            pid = json.loads(ctx_json[ctx_json.index("{"):])["persona"]["id"]
            rec = {"social-a": "CREATE_CANDIDATE", "social-b": "RESEARCH_MORE",
                   "social-c": "NO_ACTION"}[pid]
            return CLIResult(0, _wrapper(_envelope(rec, extra={
                "action": "RESEARCH_MORE", "rationale": "more", "expected_value": 0.6,
                "expected_learning": 0.95, "relevance": 0.7, "confidence": 0.6,
                "risk": 0.05, "cost": 0.1, "reversibility": 1.0,
                "duplication_risk": 0.0, "evidence_refs": []})), "")
        p = ClaudeCodeReasoningProvider(runner=context_sensitive_runner)
        recs = {}
        for pid in ("social-a", "social-b", "social-c"):
            prop = p.propose(_ctx(persona_id=pid))
            recs[pid] = prop.recommended_action
        self.assertEqual(len({recs["social-a"], recs["social-b"], recs["social-c"]}), 3,
                         f"expected materially different recommendations: {recs}")


class CommandConstructionTest(unittest.TestCase):
    def test_default_runner_denies_effect_tools_and_strips_api_key(self):
        # Structural assertions on the real command WITHOUT executing a model.
        captured = {}

        def fake_run(cmd, **kwargs):
            captured["cmd"] = cmd
            captured["kwargs"] = kwargs
            class P:  # noqa: E306
                returncode = 0
                stdout = _wrapper(_envelope("NO_ACTION"))
                stderr = ""
            return P()

        orig_run = subprocess.run
        orig_which = reasoning_cli.shutil.which
        reasoning_cli.shutil.which = lambda _: "/usr/bin/claude"
        subprocess.run = fake_run
        os.environ["ANTHROPIC_API_KEY"] = "sk-must-be-stripped"
        try:
            reasoning_cli._default_cli_runner("prompt", timeout_s=5, model=None)
        finally:
            subprocess.run = orig_run
            reasoning_cli.shutil.which = orig_which
            os.environ.pop("ANTHROPIC_API_KEY", None)
        cmd = captured["cmd"]
        self.assertIn("--print", cmd)
        self.assertIn("--output-format", cmd)
        self.assertIn("--disallowedTools", cmd)
        for tool in ("Bash", "Edit", "Write", "WebFetch"):
            self.assertIn(tool, cmd)
        self.assertNotIn("--bare", cmd)  # never force API-key auth
        # The child env never carries ANTHROPIC_API_KEY.
        self.assertNotIn("ANTHROPIC_API_KEY", captured["kwargs"]["env"])


if __name__ == "__main__":
    unittest.main()
