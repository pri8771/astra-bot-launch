"""SB-S20-001 — versioned strategy-state store.

Proves ``runtime/strategy.py``:
- versions are immutable and contiguous; HEAD/HISTORY are consistent;
- tampering with a stored version is detected (never silently repaired);
- persona scope is structural; ``admin_all_strategies`` is the only cross reader;
- unsafe ids are refused before any filesystem write;
- a lost ownership fence writes nothing;
- weight/evidence validation rejects negatives, NaN, sum != 1, bare numbers.

Evidence class: ENGINEERING (``provenance="fixture"``). No model call, no effect.
"""
import json
import os
import shutil
import sys
import tempfile
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import strategy, leasing, paths  # noqa: E402

REF = [{"kind": "metric", "id": "obs-1"}, {"evidence_id": "ev-2"}]


def v1(bot="social-a", persona="social-a", **kw):
    base = dict(platform_weights={"x": 0.6, "instagram": 0.4},
                format_weights={"short": 1.0}, priority_topics=["a"],
                evidence_refs=REF)
    base.update(kw)
    objective = base.pop("objective", "grow qualified audience")
    return strategy.new_initial(bot, persona, objective, **base)


def tree(root):
    return sorted(str(p.relative_to(root)) for p in Path(root).rglob("*"))


class StrategyStoreTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["SBOTS_HOME"] = self.tmp

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # 1. create v1 -> v2 -> active is v2; v1 untouched byte-for-byte
    def test_versions_are_immutable_and_active_pointer_advances(self):
        s1 = v1()
        p1 = strategy.save_version(s1, activate=True)
        b1 = p1.read_bytes()
        self.assertEqual(strategy.active("social-a", "social-a").version, 1)
        s2 = strategy.next_version(s1, platform_weights={"x": 0.5, "instagram": 0.5},
                                   revision={"proposal_id": "p-1"})
        self.assertEqual(s2.version, 2)
        self.assertEqual(s2.supersedes, 1)
        strategy.save_version(s2, activate=True, proposal_id="p-1", verdict_id="vd-1")
        self.assertEqual(strategy.active("social-a", "social-a").version, 2)
        self.assertEqual(p1.read_bytes(), b1)
        self.assertEqual(strategy.load_version("social-a", "social-a", 1), s1)
        self.assertEqual(strategy.versions("social-a", "social-a"), [1, 2])
        events = [(r["version"], r["event"]) for r in strategy.history("social-a", "social-a")]
        self.assertEqual(events, [(1, "SAVED"), (1, "ACTIVATED"), (2, "SAVED"), (2, "ACTIVATED")])
        self.assertTrue(all(r.get("tampered") is False for r in strategy.history("social-a", "social-a")))
        self.assertEqual(strategy.history("social-a", "social-a")[2]["proposal_id"], "p-1")

    # 2. duplicate version refused; original bytes untouched
    def test_duplicate_version_is_refused(self):
        s1 = v1()
        p1 = strategy.save_version(s1)
        b1 = p1.read_bytes()
        dup = strategy.StrategyState(**dict(s1.as_dict(), objective="overwrite attempt"))
        with self.assertRaises(strategy.StrategyVersionExists):
            strategy.save_version(dup)
        self.assertEqual(p1.read_bytes(), b1)
        self.assertEqual(len(strategy.history("social-a", "social-a")), 1)

    def test_version_gap_and_unknown_supersedes_are_refused(self):
        s1 = v1()
        strategy.save_version(s1)
        s3 = strategy.StrategyState(**dict(s1.as_dict(), version=3, supersedes=1))
        with self.assertRaises(strategy.StrategyVersionGap):
            strategy.save_version(s3)
        s2 = strategy.StrategyState(**dict(s1.as_dict(), version=2, supersedes=None))
        self.assertTrue(strategy.validate_state(s2))          # v>1 must supersede
        with self.assertRaises(strategy.StrategyError):
            strategy.save_version(s2)
        # v2 that claims to supersede a version that is not stored
        s1b = v1(persona="social-b" if False else "cultural-primandir-atman")
        s2b = strategy.StrategyState(**dict(s1b.as_dict(), version=2, supersedes=1))
        with self.assertRaises(strategy.StrategyVersionGap):
            strategy.save_version(s2b)                        # v1 never stored for that persona
        with self.assertRaises(strategy.StrategyVersionGap):
            strategy.set_active("social-a", "social-a", 7)
        self.assertEqual(strategy.versions("social-a", "social-a"), [1])

    # 3. tampered v1 -> history flags it
    def test_tampering_is_detected_not_repaired(self):
        s1 = v1()
        p1 = strategy.save_version(s1, activate=True)
        data = json.loads(p1.read_text())
        data["objective"] = "quietly changed"
        p1.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
        rows = strategy.history("social-a", "social-a")
        self.assertTrue(all(r["tampered"] for r in rows))
        # Reload still returns what is on disk; the flag is the signal.
        self.assertEqual(strategy.load_version("social-a", "social-a", 1).objective, "quietly changed")
        p1.unlink()
        self.assertTrue(all(r.get("missing") for r in strategy.history("social-a", "social-a")))

    # 4. two personas on one bot never cross
    def test_persona_scope_is_structural(self):
        a1 = v1(persona="social-a")
        c1 = v1(persona="cultural-primandir-atman", objective="cultural")
        strategy.save_version(a1, activate=True)
        strategy.save_version(c1, activate=True)
        strategy.save_version(strategy.next_version(a1, priority_topics=["b"]), activate=True)
        self.assertEqual(strategy.active("social-a", "social-a").version, 2)
        self.assertEqual(strategy.active("social-a", "cultural-primandir-atman").version, 1)
        self.assertEqual(strategy.active("social-a", "cultural-primandir-atman").objective, "cultural")
        self.assertIsNone(strategy.active("social-a", "social-b"))
        self.assertEqual(strategy.versions("social-a", "cultural-primandir-atman"), [1])
        self.assertEqual(strategy.admin_all_strategies("social-a"), {
            "cultural-primandir-atman": {"active_version": 1, "versions": [1]},
            "social-a": {"active_version": 2, "versions": [1, 2]},
        })
        self.assertEqual(strategy.admin_all_strategies("social-b"), {})
        # Reads for a persona with no strategy leave no directory behind.
        self.assertFalse(strategy.strategy_dir("social-a", "social-b").exists())
        # A version file copied across personas is refused on load.
        src = strategy.version_path("social-a", "cultural-primandir-atman", 1)
        dst = strategy.strategy_dir("social-a", "social-b", create=True) / "v0001.json"
        shutil.copy(src, dst)
        with self.assertRaises(strategy.StrategyError):
            strategy.load_version("social-a", "social-b", 1)

    # 5. unsafe ids refused before any mkdir
    def test_unsafe_ids_are_refused_before_any_write(self):
        for persona in ("../x", "/abs", "A", "x", "", "a/b", "spaces here"):
            with self.assertRaises(strategy.StrategyError):
                strategy.new_initial("social-a", persona, "o")
            with self.assertRaises(strategy.StrategyError):
                strategy.active("social-a", persona)
            with self.assertRaises(strategy.StrategyError):
                strategy.history("social-a", persona)
        with self.assertRaises(strategy.StrategyError):
            strategy.new_initial("not-a-bot", "social-a", "o")
        with self.assertRaises(strategy.StrategyError):
            strategy.admin_all_strategies("not-a-bot")
        bad = strategy.StrategyState(**dict(v1().as_dict(), persona="../x",
                                             strategy_id="strat-social-a-../x"))
        with self.assertRaises(strategy.StrategyError):
            strategy.save_version(bad)
        self.assertEqual(tree(self.tmp), [])

    # 6. fence loss -> zero durable writes
    def test_lost_fence_writes_nothing(self):
        a = leasing.acquire("cycle:social-a", "A", ttl_seconds=0)   # immediately stale
        fa = leasing.Fence(a)
        leasing.acquire("cycle:social-a", "B", ttl_seconds=300)     # takeover
        with self.assertRaises(leasing.FenceLost):
            strategy.save_version(v1(), activate=True, fence=fa)
        d = strategy.strategy_dir("social-a", "social-a")
        self.assertEqual(sorted(p.name for p in d.iterdir()), [])
        self.assertIsNone(strategy.active("social-a", "social-a"))
        with self.assertRaises(leasing.FenceLost):
            strategy.set_active("social-a", "social-a", 1, fence=fa)
        # A live fence commits normally, and HEAD/HISTORY/version all land.
        b = leasing.inspect("cycle:social-a")
        lease_b = leasing.Lease(**b)
        fb = leasing.Fence(lease_b)
        strategy.save_version(v1(), activate=True, fence=fb)
        self.assertEqual(sorted(p.name for p in d.iterdir()),
                         ["HEAD.json", "HISTORY.jsonl", "v0001.json"])
        leasing.release(lease_b)

    # 7. weight / evidence / field validation
    def test_validation_rejects_bad_weights_refs_and_fields(self):
        for weights in ({"x": -0.1, "y": 1.1}, {"x": 1.5}, {"x": float("nan")},
                        {"x": 0.3, "y": 0.3}, {"x": True}, {"": 1.0}, {"x": "1"}):
            with self.assertRaises(strategy.StrategyError, msg=weights):
                v1(platform_weights=weights)
        self.assertEqual(strategy.validate_state(v1(platform_weights={})), [])
        for refs in ([1], ["ev-1"], [{"note": "no id"}], [{"kind": "metric"}], "ev"):
            with self.assertRaises(strategy.StrategyError, msg=refs):
                v1(evidence_refs=refs)
        with self.assertRaises(strategy.StrategyError):
            v1(status="LIVE")
        with self.assertRaises(strategy.StrategyError):
            v1(confidence=1.5)
        with self.assertRaises(strategy.StrategyError):
            v1(provenance="live")
        with self.assertRaises(strategy.StrategyError):
            v1(review_by="soon")
        with self.assertRaises(strategy.StrategyError):
            v1(priority_topics=["ok", 3])
        self.assertIsNone(v1(confidence=None).confidence)   # missing stays None, not 0

    def test_next_version_refuses_arbitrary_merge_and_reload_is_strict(self):
        s1 = v1()
        with self.assertRaises(strategy.StrategyError):
            strategy.next_version(s1, spend_budget=100)
        with self.assertRaises(strategy.StrategyError):
            strategy.next_version(s1, version=9)
        with self.assertRaises(strategy.StrategyError):
            strategy.next_version(s1, platform_weights={"x": 2.0})
        with self.assertRaises(FrozenInstanceError):
            s1.objective = "mutated"
        d = json.loads(json.dumps(s1.as_dict()))
        self.assertEqual(strategy.StrategyState.from_dict(d), s1)
        with self.assertRaises(strategy.StrategyError):
            strategy.StrategyState.from_dict(dict(d, can_public_post=True))
        with self.assertRaises(strategy.StrategyError):
            strategy.StrategyState.from_dict({k: v for k, v in d.items() if k != "status"})
        with self.assertRaises(strategy.StrategyError):
            strategy.StrategyState.from_dict(dict(d, strategy_id="strat-other"))

    # 8. SBOTS_HOME isolation
    def test_store_lives_under_sbots_home_only(self):
        strategy.save_version(v1(), activate=True)
        self.assertEqual(tree(self.tmp), [
            "state", "state/social-a", "state/social-a/strategy",
            "state/social-a/strategy/social-a",
            "state/social-a/strategy/social-a/HEAD.json",
            "state/social-a/strategy/social-a/HISTORY.jsonl",
            "state/social-a/strategy/social-a/v0001.json",
        ])
        self.assertEqual(strategy.latest_version("social-a", "social-a"), 1)
        self.assertEqual(strategy.latest_version("social-a", "social-b"), 0)
        other = tempfile.mkdtemp()
        try:
            os.environ["SBOTS_HOME"] = other
            self.assertIsNone(strategy.active("social-a", "social-a"))
            self.assertEqual(strategy.versions("social-a", "social-a"), [])
        finally:
            shutil.rmtree(other, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
