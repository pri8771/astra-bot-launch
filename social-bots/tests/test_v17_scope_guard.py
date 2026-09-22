"""V1.7 scope guard — parked strategy/planner/specialist routes are unreachable.

V17_SCOPE.json (LEAD-048) parks V1.8+/V2.x/V3.0 work and requires "a narrow
scope guard/test if the actual dispatcher would otherwise auto-pull later
artifacts"; V17_ACCEPTANCE.md requires that unused future modules stay
unreachable from the V1.7 dispatcher and that a narrow test shows the
out-of-scope strategy/planner/specialist entrypoints are not selected. The
parked code is PRESERVED (not deleted, not finished, not claimed secure).
"""
import ast
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "bin"))

from runtime import decision, reasoning  # noqa: E402

# Parked (preserved, unreachable) modules and the prefixes that would name them.
PARKED_FILES = (
    "runtime/strategy.py", "runtime/specialist_contract.py", "runtime/specialist_sandbox.py",
    "runtime/specialist_budget.py", "runtime/specialist_research.py",
    "runtime/specialist_analysis.py", "runtime/specialist_writer.py",
    "runtime/specialist_integrator.py", "runtime/specialist_lifecycle.py",
    "bin/prove_v23_specialists.py",
)
PARKED_PREFIXES = ("runtime.strategy", "runtime.specialist_", "runtime.goal_planner",
                   "runtime.planner", "runtime.growth")
PARKED_BARE = ("strategy", "goal_planner", "planner", "growth")   # relative-import names

# The V1.7 dispatcher: the scheduled entrypoints and everything a cycle reaches.
DISPATCHER_MODULES = (
    "worker_once", "run_worker", "runtime.worker", "runtime.decision", "runtime.pipeline",
    "runtime.reasoning", "runtime.reasoning_cli", "runtime.reasoning_receipt",
    "runtime.model_dispatch", "runtime.live_route_guard", "runtime.divergence_prepare",
    "runtime.due_rotation", "runtime.direction", "runtime.invocation",
    "runtime.session_heartbeat", "runtime.leasing", "runtime.research",
    "runtime.analytics", "runtime.isolation", "runtime.state",
)
PARKED_ACTIONS = ("SPAWN_SPECIALIST", "RUN_SPECIALIST", "DELEGATE_SPECIALIST", "PLAN_GOAL",
                  "UPDATE_STRATEGY", "SELECT_STRATEGY", "REPLAN")


def _is_parked(name: str) -> bool:
    return name.startswith(PARKED_PREFIXES) or name.startswith("specialist_") \
        or name in PARKED_BARE


class ParkedCodeIsPreservedTest(unittest.TestCase):
    def test_parked_modules_still_exist(self):
        """Preserve, do not delete: the scope change is a reachability change."""
        for rel in PARKED_FILES:
            with self.subTest(file=rel):
                self.assertTrue((ROOT / rel).is_file(), rel)


class DispatcherReachabilityTest(unittest.TestCase):
    def test_dispatcher_import_closure_contains_no_parked_module(self):
        """Fresh interpreter: importing every dispatcher module loads nothing parked."""
        code = (
            "import importlib, json, sys\n"
            f"sys.path.insert(0, {str(ROOT)!r}); sys.path.insert(0, {str(ROOT / 'bin')!r})\n"
            f"for m in {DISPATCHER_MODULES!r}:\n"
            "    importlib.import_module(m)\n"
            "print(json.dumps(sorted(m for m in sys.modules "
            "if m.startswith('runtime') or m in ('worker_once', 'run_worker'))))\n")
        env = dict(os.environ, SBOTS_HOME=tempfile.mkdtemp())
        out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                             timeout=120, env=env)
        self.assertEqual(out.returncode, 0, out.stderr)
        loaded = json.loads(out.stdout)
        parked = [m for m in loaded if _is_parked(m) or _is_parked(m.split(".")[-1])]
        self.assertEqual(parked, [], f"parked modules reachable from the dispatcher: {parked}")
        for m in DISPATCHER_MODULES:
            self.assertIn(m, loaded)

    def test_dispatcher_sources_have_no_static_import_of_parked_modules(self):
        """AST-level: no `import`/`from` of a parked module in non-parked code."""
        offenders = []
        files = [p for p in (ROOT / "runtime").glob("*.py")
                 if p.relative_to(ROOT).as_posix() not in PARKED_FILES]
        files += [ROOT / "bin" / "worker_once.py", ROOT / "bin" / "run_worker.py"]
        for path in files:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        names.append(node.module)
                    if node.level and not node.module:      # from . import x
                        names.extend(a.name for a in node.names)
                for n in names:
                    if _is_parked(n) or _is_parked(n.split(".")[-1]):
                        offenders.append(f"{path.relative_to(ROOT)}:{node.lineno} {n}")
        self.assertEqual(offenders, [])


class ProviderAndActionSelectionTest(unittest.TestCase):
    def setUp(self):
        self.prior = os.environ.get("SBOTS_REASONING")
        reasoning.register_model_callable(None)

    def tearDown(self):
        if self.prior is None:
            os.environ.pop("SBOTS_REASONING", None)
        else:
            os.environ["SBOTS_REASONING"] = self.prior
        reasoning.register_model_callable(None)

    def test_no_reasoning_mode_selects_a_parked_route(self):
        """Known modes resolve to V1.7 providers; unknown/parked names fall to baseline
        (or fail closed when adaptive is required). Never a parked module."""
        for mode in ("baseline", "contextual", "model", "claude-cli", "specialist",
                     "strategy", "planner", "growth", "v23", "specialist_research", ""):
            with self.subTest(mode=mode):
                os.environ["SBOTS_REASONING"] = mode
                provider = reasoning.resolve_provider()
                self.assertFalse(_is_parked(type(provider).__module__),
                                 type(provider).__module__)
                if mode not in ("baseline", "contextual", "model", "claude-cli"):
                    self.assertEqual(provider.provider_id, "baseline-deterministic-v1")
                    strict = reasoning.resolve_provider(require_adaptive=True)
                    self.assertFalse(strict.available())
                    self.assertFalse(_is_parked(type(strict).__module__))

    def test_action_vocabulary_has_no_parked_actions(self):
        for vocab in (reasoning.ACTION_VOCAB, reasoning.EXECUTABLE_ACTIONS, decision.ACTIONS):
            self.assertTrue(set(PARKED_ACTIONS).isdisjoint(vocab), vocab)
        for action in PARKED_ACTIONS:
            with self.subTest(action=action):
                cand = reasoning.Candidate(action, "parked", 0.9, 0.9, 0.9, 0.9, 0.0, 0.0,
                                           1.0, 0.0)
                prop = reasoning.ReasoningProposal([cand], action, [], "fixture", True)
                errs = reasoning.validate_proposal(prop)
                self.assertTrue(any("unsupported action" in e for e in errs), errs)

    def test_lead_direction_consumer_reads_no_roadmap_or_artifact_index(self):
        """The scheduled worker takes work only from lead direction, never by
        scanning the artifact index, work queue or roadmaps for later artifacts."""
        for rel in ("runtime/direction.py", "bin/worker_once.py", "bin/run_worker.py",
                    "runtime/worker.py"):
            text = (ROOT / rel).read_text(encoding="utf-8")
            for marker in ("ARTIFACT_INDEX", "WORK_QUEUE", "roadmap", "ROADMAP", "V23_"):
                self.assertNotIn(marker, text, f"{rel} references {marker}")


if __name__ == "__main__":
    unittest.main()
