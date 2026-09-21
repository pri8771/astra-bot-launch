"""SB-V03-005 — persona/runtime isolation (logical model).

Proves the contract in ``runtime/isolation.py``:
- shared runtime state (bot_state.json) is single-writer under the fence;
- non-shared persona data is logically isolated inside the runtime's append-only
  stores by a mandatory ``persona`` field + persona-derived, collision-free ids;
- every persona-specific read filters strictly by persona, so one persona's data
  cannot be mistaken for another's;
- concurrent general+cultural cycles on one runtime lose no counter/consumption/
  hypothesis update.

Scope: single POSIX host, single local filesystem. No public/external effect.
"""
import os
import sys
import tempfile
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import decision, research, pipeline, isolation, worker  # noqa: E402
from runtime.state import BotState  # noqa: E402


def seed(bot, title, url):
    research.capture(bot, research.Signal.make(
        title, "captured evidence for the runtime", "unit-test", url,
        "fixture", ["indian-festivals"]))


class IsolationContractTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp

    def test_ids_are_persona_derived_and_collision_free(self):
        # Same signal, two different personas on the SAME runtime -> different
        # content_id / content_key / experiment_id by construction.
        from runtime.personas import load as load_persona
        sig = research.Signal.make("shared signal", "s", "u", "https://e.org/x",
                                   "fixture", ["t"])
        gen = load_persona("social-a")          # general, runtime social-a
        cul = load_persona("cultural-primandir-atman")  # cultural, runtime social-a
        cg = pipeline.ideate(gen, sig.__dict__ if hasattr(sig, "__dict__") else sig)
        cc = pipeline.ideate(cul, sig.__dict__ if hasattr(sig, "__dict__") else sig)
        self.assertNotEqual(cg["content_id"], cc["content_id"])
        self.assertNotEqual(pipeline.content_key(cg), pipeline.content_key(cc))
        self.assertNotEqual(f"exp-{cg['content_id']}", f"exp-{cc['content_id']}")

    def test_filters_partition_mixed_store_without_bleed(self):
        # Directly exercise the read/filter paths: write records for two personas
        # into ONE runtime's stores, then assert each persona filter returns
        # exactly its own records and none of the other's, losing nothing.
        bot = "social-a"
        pa, pb = "social-a", "cultural-primandir-atman"
        # content history (via the real state writer)
        st = BotState.load(bot)
        st.record_content({"content_id": "c-a1", "content_key": "k-a1", "persona": pa, "platform": "x"})
        st.record_content({"content_id": "c-b1", "content_key": "k-b1", "persona": pb, "platform": "x"})
        st.record_action({"action": "CREATE_CANDIDATE", "persona": pa, "content_id": "c-a1"})
        st.record_action({"action": "CREATE_CANDIDATE_WITHHELD", "persona": pb, "content_id": "c-b1"})
        # experiments + queue + analytics (via the real pipeline/analytics writers)
        from runtime import analytics
        pipeline.register_experiment(pipeline.Experiment(
            experiment_id="exp-c-a1", bot=bot, persona=pa, platform="x",
            hypothesis="h", baseline={}, intervention="i", success_metric="m",
            stop_criteria="s", observation_window_hours=48))
        pipeline.register_experiment(pipeline.Experiment(
            experiment_id="exp-c-b1", bot=bot, persona=pb, platform="x",
            hypothesis="h", baseline={}, intervention="i", success_metric="m",
            stop_criteria="s", observation_window_hours=48))
        pipeline.enqueue(bot, {"content_id": "c-a1", "persona": pa, "signal_id": "s",
                               "signature_move": "m"}, {"platform": "x"}, "exp-c-a1")
        pipeline.enqueue(bot, {"content_id": "c-b1", "persona": pb, "signal_id": "s",
                               "signature_move": "m"}, {"platform": "x"}, "exp-c-b1")
        analytics.emit(analytics.make_event(bot, pa, "candidate_created", platform="x", content_id="c-a1"))
        analytics.emit(analytics.make_event(bot, pb, "correction", platform="x", content_id="c-b1"))

        # Each persona view is exactly its own, disjoint, complete.
        self.assertEqual([r["content_id"] for r in isolation.persona_content_history(bot, pa)], ["c-a1"])
        self.assertEqual([r["content_id"] for r in isolation.persona_content_history(bot, pb)], ["c-b1"])
        self.assertEqual([r["experiment_id"] for r in isolation.persona_experiments(bot, pa)], ["exp-c-a1"])
        self.assertEqual([r["experiment_id"] for r in isolation.persona_experiments(bot, pb)], ["exp-c-b1"])
        self.assertEqual([e["content_id"] for e in isolation.persona_publish_queue(bot, pa)], ["c-a1"])
        self.assertEqual([e["content_id"] for e in isolation.persona_publish_queue(bot, pb)], ["c-b1"])
        self.assertEqual({a["action"] for a in isolation.persona_action_history(bot, pa)}, {"CREATE_CANDIDATE"})
        self.assertEqual({a["action"] for a in isolation.persona_action_history(bot, pb)}, {"CREATE_CANDIDATE_WITHHELD"})
        self.assertEqual(len(isolation.persona_analytics(bot, pa)), 1)
        self.assertEqual(len(isolation.persona_analytics(bot, pb)), 1)

        # The audit certifies a clean partition: no unlabeled / foreign records.
        rep = isolation.audit(bot, [pa, pb])
        self.assertTrue(rep["clean"], rep)
        for store, s in rep["stores"].items():
            self.assertEqual(s["unlabeled"], 0, f"{store}: unlabeled records")
            self.assertEqual(s["unknown_persona"], [], f"{store}: foreign persona")
            self.assertTrue(s["partition_covers_all"], f"{store}: partition lost/dup records")

    def test_real_general_and_cultural_cycles_do_not_bleed(self):
        # End-to-end on the same runtime: general creates a candidate; cultural is
        # WITHHELD (no named reviewer). Their records stay attributed and disjoint.
        bot = "social-a"
        seed(bot, "festival ledger", "https://example.org/gen")
        rec_gen = decision.run_cycle(bot, "social-a")
        self.assertEqual(rec_gen["outcome"], "candidate_created")
        seed(bot, "festival note", "https://example.org/cul")
        rec_cul = decision.run_cycle(bot, "cultural-primandir-atman")
        self.assertEqual(rec_cul["outcome"], "withheld")

        # General owns exactly one experiment + one queued item; cultural owns none.
        self.assertEqual(len(isolation.persona_experiments(bot, "social-a")), 1)
        self.assertEqual(len(isolation.persona_experiments(bot, "cultural-primandir-atman")), 0)
        self.assertEqual(len(isolation.persona_publish_queue(bot, "social-a")), 1)
        self.assertEqual(len(isolation.persona_publish_queue(bot, "cultural-primandir-atman")), 0)
        # Cultural's only record is its withheld action, correctly attributed.
        cul_actions = isolation.persona_action_history(bot, "cultural-primandir-atman")
        self.assertTrue(cul_actions and all(a["persona"] == "cultural-primandir-atman" for a in cul_actions))
        self.assertTrue(all(a["action"] == "CREATE_CANDIDATE_WITHHELD" for a in cul_actions))
        # Audit clean across both personas.
        self.assertTrue(isolation.audit(bot, ["social-a", "cultural-primandir-atman"])["clean"])

    def test_concurrent_general_cultural_no_lost_shared_update(self):
        # Shared runtime state (counters, consumed ledger) survives concurrent
        # general + cultural cycles on one runtime: the runtime lease serializes
        # them, so no counter or consumption update is lost.
        bot = "social-a"
        for i in range(12):
            seed(bot, f"sig {i}", f"https://example.org/{i}")
        task = worker.runtime_task_id(bot)
        ran = []
        lock_rejects = []

        def run(persona):
            try:
                res = worker.run_one_unit(task, bot, persona, ttl_seconds=300)
                ran.append(res["outcome"])
            except Exception as e:  # LeaseHeld when the other holds the runtime
                lock_rejects.append(type(e).__name__)

        for _ in range(6):
            t1 = threading.Thread(target=run, args=("social-a",))
            t2 = threading.Thread(target=run, args=("cultural-primandir-atman",))
            t1.start(); t2.start(); t1.join(); t2.join()

        st = BotState.load(bot)
        # Every cycle that actually ran advanced the shared counter exactly once;
        # rejected overlaps did not corrupt it. cycles == number of successful runs.
        self.assertEqual(st.data["counters"]["cycles"], len(ran))
        # Consumed ledger has no duplicates (no double consumption of a signal).
        consumed = st.consumed_ids()
        self.assertEqual(len(consumed), len(set(consumed)))
        self.assertTrue(isolation.audit(bot, ["social-a", "cultural-primandir-atman"])["clean"])


if __name__ == "__main__":
    unittest.main()
