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
from runtime.state import BotState, PersonaState  # noqa: E402


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
        # SHARED runtime state (counters) survives concurrent general + cultural
        # cycles on one runtime: the runtime lease serializes them, so no counter
        # update is lost. Consumption is PERSONA-PRIVATE (SB-V03-005), so each
        # persona keeps its own duplicate-free ledger.
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

        rt = BotState.load(bot)
        # Every cycle that actually ran advanced the shared counter exactly once;
        # rejected overlaps did not corrupt it. cycles == number of successful runs.
        self.assertEqual(rt.data["counters"]["cycles"], len(ran))
        # The shared runtime state carries NO persona-private ledger/hypotheses.
        self.assertNotIn("consumed_signal_ids", rt.data)
        self.assertNotIn("hypotheses", rt.data)
        # Each persona's private consumed ledger has no duplicates.
        for persona in ("social-a", "cultural-primandir-atman"):
            consumed = PersonaState.load(bot, persona).consumed_ids()
            self.assertEqual(len(consumed), len(set(consumed)),
                             f"{persona}: duplicate consumption")
        self.assertTrue(isolation.audit(bot, ["social-a", "cultural-primandir-atman"])["clean"])

    def test_same_signal_independently_considered_by_two_personas(self):
        # SB-V03-005 core acceptance: one shared captured signal is visible to
        # BOTH personas; the general persona consuming it does NOT hide it from
        # the cultural persona's own workspace.
        bot = "social-a"
        s = research.Signal.make("shared festival signal", "captured", "unit",
                                 "https://example.org/shared", "fixture", ["indian-festivals"])
        research.capture(bot, s)

        # Both personas see it as unconsumed initially.
        self.assertIn(s.id, [x["id"] for x in research.unconsumed_signals(
            bot, PersonaState.load(bot, "social-a").consumed_ids())])
        self.assertIn(s.id, [x["id"] for x in research.unconsumed_signals(
            bot, PersonaState.load(bot, "cultural-primandir-atman").consumed_ids())])

        # General consumes it.
        rec_gen = decision.run_cycle(bot, "social-a")
        self.assertEqual(rec_gen["observe"]["consumed_this_cycle"], s.id)

        # General now sees it consumed; the cultural persona still sees it pending.
        gen_consumed = PersonaState.load(bot, "social-a").consumed_ids()
        cul_consumed = PersonaState.load(bot, "cultural-primandir-atman").consumed_ids()
        self.assertIn(s.id, gen_consumed)
        self.assertNotIn(s.id, cul_consumed)
        self.assertIn(s.id, [x["id"] for x in research.unconsumed_signals(bot, cul_consumed)])

        # And the cultural persona can independently consider (and consume) it.
        rec_cul = decision.run_cycle(bot, "cultural-primandir-atman")
        self.assertEqual(rec_cul["observe"]["consumed_this_cycle"], s.id)
        self.assertIn(s.id, PersonaState.load(bot, "cultural-primandir-atman").consumed_ids())

    def test_one_persona_hypotheses_do_not_change_another_reasoning_context(self):
        # A persona's hypothesis count feeds ITS reasoning novelty only. Growing
        # the general persona's hypotheses must not change the cultural persona's
        # reasoning context (hypothesis_count).
        bot = "social-a"
        # Drive several general-persona candidate cycles to grow its hypotheses.
        for i in range(3):
            seed(bot, f"gen sig {i}", f"https://example.org/gen/{i}")
            decision.run_cycle(bot, "social-a")
        gen_hyp = PersonaState.load(bot, "social-a").hypothesis_count()
        cul_hyp = PersonaState.load(bot, "cultural-primandir-atman").hypothesis_count()
        self.assertGreater(gen_hyp, 0, "general persona should have learned hypotheses")
        self.assertEqual(cul_hyp, 0, "cultural persona's hypotheses must be untouched")

    def test_persona_separation_survives_restart(self):
        # Persona-private ledgers/hypotheses persist to disk per persona and
        # reload independently — no bleed across a simulated process restart.
        bot = "social-a"
        seed(bot, "gen restart sig", "https://example.org/gen-restart")
        decision.run_cycle(bot, "social-a")
        seed(bot, "cul restart sig", "https://example.org/cul-restart")
        # cultural is WITHHELD (no reviewer) but still consumes its own signal.
        decision.run_cycle(bot, "cultural-primandir-atman")

        # Fresh loads from disk (restart): each persona keeps its OWN private
        # state in its own file — the two ledgers are independent objects, and
        # each advanced by its own cycle (one consumed signal apiece).
        gen = PersonaState.load(bot, "social-a")
        cul = PersonaState.load(bot, "cultural-primandir-atman")
        self.assertEqual(gen.persona_id, "social-a")
        self.assertEqual(cul.persona_id, "cultural-primandir-atman")
        self.assertEqual(len(gen.consumed_ids()), 1)
        self.assertEqual(len(cul.consumed_ids()), 1)
        # General learned a hypothesis (candidate created); cultural did not
        # (WITHHELD, no named reviewer) — learning stays persona-private.
        self.assertGreater(gen.hypothesis_count(), 0)
        self.assertEqual(cul.hypothesis_count(), 0)
        # Shared runtime state stays shared and is not persona-scoped.
        rt = BotState.load(bot)
        self.assertNotIn("hypotheses", rt.data)
        self.assertGreaterEqual(rt.data["counters"]["cycles"], 2)


    def test_legacy_shared_state_migrates_to_default_owner_without_deletion(self):
        # Safe migration: a pre-SB-V03-005 bot_state.json carried the consumed
        # ledger + hypotheses at the runtime level. On load they are (a) archived
        # into _legacy (never silently deleted), (b) removed from the ACTIVE
        # shared keys, and (c) migrated once into the default-owner persona
        # (persona_id == bot). Other personas start clean.
        import json
        from runtime import paths
        bot = "social-a"
        legacy_state = {
            "bot": bot,
            "schema_version": 1,
            "consumed_signal_ids": ["sig-legacy-1", "sig-legacy-2"],
            "hypotheses": {"h-old": {"statement": "old", "confidence": 0.5, "evidence": []}},
            "counters": {"cycles": 7, "actions": 2, "no_action": 3},
            "recovery": {"last_clean_tick": "2026-01-01T00:00:00+00:00", "in_flight": None},
            "observation_fingerprint": "abc123",
        }
        sp = paths.state_dir(bot) / "bot_state.json"
        sp.write_text(json.dumps(legacy_state))

        # RuntimeState.load archives legacy persona-private keys, drops them from
        # active use, and preserves counters/recovery.
        rt = BotState.load(bot)
        self.assertNotIn("consumed_signal_ids", rt.data)
        self.assertNotIn("hypotheses", rt.data)
        self.assertEqual(rt.data["counters"]["cycles"], 7)  # shared facts preserved
        self.assertIn("_legacy", rt.data)
        self.assertEqual(rt.data["_legacy"]["archived_persona_private"]["consumed_signal_ids"],
                         ["sig-legacy-1", "sig-legacy-2"])

        # Default-owner persona (== bot) inherits the legacy private state once.
        gen = PersonaState.load(bot, bot)
        self.assertEqual(gen.consumed_ids(), ["sig-legacy-1", "sig-legacy-2"])
        self.assertIn("h-old", gen.data["hypotheses"])

        # A different persona on the same runtime starts CLEAN (no bleed).
        cul = PersonaState.load(bot, "cultural-primandir-atman")
        self.assertEqual(cul.consumed_ids(), [])
        self.assertEqual(cul.hypothesis_count(), 0)

        # Migration is idempotent: a second default-owner load does not double it.
        gen2 = PersonaState.load(bot, bot)
        self.assertEqual(gen2.consumed_ids(), ["sig-legacy-1", "sig-legacy-2"])

    def test_run_cycle_commits_runtime_with_final_migration_marker(self):
        # LEAD-018 migration-consistency: run_cycle loads RuntimeState, then
        # PersonaState (which migrates). The runtime the cycle COMMITS must carry
        # the final migrated marker — it must not be clobbered by the cycle's own
        # later rt.save(). Reload from disk after the cycle and check the marker.
        import json
        from runtime import paths
        bot = "social-a"
        legacy_state = {
            "bot": bot, "schema_version": 1,
            "consumed_signal_ids": ["sig-old"],
            "hypotheses": {"h-old": {"statement": "old", "confidence": 0.5, "evidence": []}},
            "counters": {"cycles": 3, "actions": 0, "no_action": 0},
            "recovery": {"last_clean_tick": None, "in_flight": None},
            "observation_fingerprint": None,
        }
        (paths.state_dir(bot) / "bot_state.json").write_text(json.dumps(legacy_state))
        seed(bot, "post-migration signal", "https://example.org/mig")
        decision.run_cycle(bot, "social-a")   # loads rt, migrates persona(runtime=rt), commits rt

        rt_disk = json.loads((paths.state_dir(bot) / "bot_state.json").read_text())
        # The committed runtime carries the final marker and NO active persona keys.
        self.assertTrue(rt_disk.get("_legacy", {}).get("migrated_to_persona"),
                        "committed runtime must carry the final migration marker")
        self.assertNotIn("consumed_signal_ids", rt_disk)
        self.assertNotIn("hypotheses", rt_disk)
        self.assertEqual(rt_disk["counters"]["cycles"], 4)  # 3 legacy + this cycle
        # The persona inherited the legacy ledger AND advanced this cycle.
        gen = PersonaState.load(bot, bot)
        self.assertIn("sig-old", gen.consumed_ids())
        self.assertIn("h-old", gen.data["hypotheses"])

    def test_migration_recovers_when_marker_set_but_persona_file_missing(self):
        # Crash-safety: if a marker was written but the persona file never became
        # durable (crash between phases), the next load STILL migrates (the
        # persona file, not the marker, is the idempotency gate) — no data loss.
        import json
        from runtime import paths
        bot = "social-a"
        state = {
            "bot": bot, "schema_version": 2,
            "counters": {"cycles": 1, "actions": 0, "no_action": 0},
            "recovery": {"last_clean_tick": None, "in_flight": None},
            "observation_fingerprint": None,
            "_legacy": {
                "archived_persona_private": {"consumed_signal_ids": ["sig-x"],
                                             "hypotheses": {}},
                "archived_at": "2026-01-01T00:00:00+00:00",
                "migrated_to_persona": True,   # marker says done...
            },
        }
        (paths.state_dir(bot) / "bot_state.json").write_text(json.dumps(state))
        # ...but the persona file is absent (the phase-1 save was lost).
        self.assertFalse((paths.state_dir(bot) / "persona-social-a.json").exists())
        gen = PersonaState.load(bot, bot)
        self.assertEqual(gen.consumed_ids(), ["sig-x"], "must recover the legacy data")
        self.assertTrue((paths.state_dir(bot) / "persona-social-a.json").exists())

    def test_mixed_persona_production_dedup_read_is_scoped_no_bleed(self):
        # Production-path regression for the persona-scoped read boundary: the
        # SAME signal+signature drives BOTH personas; one persona's content
        # history must NOT make the other's candidate look like a duplicate.
        bot = "social-a"
        from runtime import pipeline
        sig = research.Signal.make("shared dedup signal", "captured", "unit",
                                   "https://example.org/dedup", "fixture", ["t"])
        research.capture(bot, sig)
        # General creates a candidate (writes its content history).
        rec_gen = decision.run_cycle(bot, "social-a")
        self.assertEqual(rec_gen["outcome"], "candidate_created")
        # The general persona now sees ITS candidate as a duplicate...
        gen_persona = __import__("runtime.personas", fromlist=["load"]).load("social-a")
        gen_draft = pipeline.ideate(gen_persona, sig.__dict__)
        self.assertTrue(pipeline.is_duplicate(bot, gen_draft))
        # ...but the cultural persona's own candidate for the same signal is NOT a
        # duplicate: the dedup read is persona-scoped, so no cross-persona bleed.
        cul_persona = __import__("runtime.personas", fromlist=["load"]).load(
            "cultural-primandir-atman")
        cul_draft = pipeline.ideate(cul_persona, sig.__dict__)
        self.assertFalse(pipeline.is_duplicate(bot, cul_draft))
        # The scoped read API returns only each persona's own keys.
        self.assertNotEqual(pipeline.persona_content_keys(bot, "social-a"),
                            pipeline.persona_content_keys(bot, "cultural-primandir-atman"))


if __name__ == "__main__":
    unittest.main()
