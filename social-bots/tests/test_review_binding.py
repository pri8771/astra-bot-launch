"""V1.7 C05/C06 — factual/voice/cultural/platform review bound to the FINAL text.

Draft review looks at hook/body; platform formatting renders the text that
would actually be published. These tests prove that nothing reaches the queue
unless every review ran over that exact final text and is bound to its hash;
that editing the candidate, re-formatting, editing the payload or a late write
to the queue invalidates the binding; that scope mismatches and a symlinked
queue are refused; and that a required cultural review must name the final
text. ENGINEERING-ONLY: temp homes, deterministic providers, no model call.
"""
import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import cultural_review as cr, decision, paths, personas, pipeline, research  # noqa: E402
from runtime.jsonstore import read_jsonl  # noqa: E402

SIGNAL = {"id": "sig-abc", "title": "Water tension demo",
          "summary": "A leaf floats because of surface tension.",
          "source": "test", "url": "https://example.org/leaf", "tags": ["nature"]}


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def seed(bot):
    research.capture(bot, research.Signal.make(
        SIGNAL["title"], SIGNAL["summary"], "unit-test", SIGNAL["url"], "fixture", ["nature"]))


class _Case(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.prior = os.environ.get("SBOTS_HOME")
        os.environ["SBOTS_HOME"] = self.tmp
        self.p = personas.load("social-a")
        self.cand = pipeline.review(self.p, pipeline.ideate(self.p, SIGNAL))
        self.payload = pipeline.format_for_platform(self.cand, "x")

    def tearDown(self):
        if self.prior is None:
            os.environ.pop("SBOTS_HOME", None)
        else:
            os.environ["SBOTS_HOME"] = self.prior

    def bind(self):
        return pipeline.final_review(self.p, self.cand, self.payload)


class FinalReviewBindingTest(_Case):
    def test_draft_review_stamps_a_binding_over_its_inputs(self):
        self.assertEqual(self.cand["review_binding"]["reviewed_sha256"],
                         pipeline.reviewed_digest(self.cand))

    def test_final_review_checks_the_rendered_text_not_the_draft(self):
        seen = {}
        real = pipeline.voice_review

        def spy(persona, candidate):
            seen["hook"], seen["body"] = candidate["hook"], candidate["body"]
            return real(persona, candidate)

        with mock.patch.object(pipeline, "voice_review", spy):
            final = self.bind()
        self.assertEqual(seen, {"hook": "", "body": self.payload["text"]})
        self.assertTrue(final["passed"], final["reasons"])
        self.assertEqual(final["final_text_sha256"], _sha(self.payload["text"]))
        self.assertEqual(set(final["checks"]), {"fact", "voice", "cultural", "platform"})
        self.assertIs(self.payload["review_binding"], final)
        self.assertEqual((final["content_id"], final["persona"], final["bot"], final["platform"]),
                         (self.cand["content_id"], "social-a", "social-a", "x"))

    def test_editing_the_candidate_after_review_invalidates_it(self):
        self.cand["body"] += " (edited after review)"
        final = self.bind()
        self.assertFalse(final["passed"])
        self.assertTrue(any("changed after" in r for r in final["reasons"]), final["reasons"])
        with self.assertRaises(pipeline.ReviewBindingError):
            pipeline.enqueue("social-a", self.cand, self.payload, "exp-1")

    def test_a_never_reviewed_candidate_cannot_be_bound(self):
        raw = pipeline.ideate(self.p, SIGNAL)
        payload = pipeline.format_for_platform(raw, "x")
        final = pipeline.final_review(self.p, raw, payload)
        self.assertFalse(final["passed"])
        with self.assertRaises(pipeline.ReviewBindingError):
            pipeline.enqueue("social-a", raw, payload, "exp-1")

    def test_reformatting_invalidates_the_binding(self):
        self.bind()
        other = pipeline.format_for_platform(self.cand, "reddit")
        with self.assertRaises(pipeline.ReviewBindingError):   # unbound rendering
            pipeline.enqueue("social-a", self.cand, other, "exp-1")
        other["review_binding"] = dict(self.payload["review_binding"])   # transplanted
        with self.assertRaises(pipeline.ReviewBindingError):
            pipeline.enqueue("social-a", self.cand, other, "exp-1")

    def test_enqueue_refuses_an_unbound_payload(self):
        with self.assertRaises(pipeline.ReviewBindingError) as ctx:
            pipeline.enqueue("social-a", self.cand, self.payload, "exp-1")
        self.assertIn("no final-content review binding", str(ctx.exception))
        self.assertEqual(pipeline.admin_publish_queue("social-a"), [])

    def test_enqueue_refuses_text_edited_after_final_review(self):
        self.bind()
        self.payload["text"] += " !"
        with self.assertRaises(pipeline.ReviewBindingError) as ctx:
            pipeline.enqueue("social-a", self.cand, self.payload, "exp-1")
        self.assertIn("differs", str(ctx.exception))

    def test_enqueue_refuses_a_failed_final_review(self):
        self.bind()
        self.payload["review_binding"]["passed"] = False
        with self.assertRaises(pipeline.ReviewBindingError) as ctx:
            pipeline.enqueue("social-a", self.cand, self.payload, "exp-1")
        self.assertIn("did not pass", str(ctx.exception))

    def test_enqueue_refuses_the_wrong_runtime_scope(self):
        self.bind()
        with self.assertRaises(pipeline.ReviewBindingError) as ctx:
            pipeline.enqueue("social-b", self.cand, self.payload, "exp-1")
        self.assertIn("runtime", str(ctx.exception))
        self.assertEqual(pipeline.admin_publish_queue("social-b"), [])

    def test_queued_entry_verifies_and_a_late_write_is_detected(self):
        self.bind()
        entry = pipeline.enqueue("social-a", self.cand, self.payload, "exp-1")
        [row] = pipeline.admin_publish_queue("social-a")
        self.assertEqual(row["final_text_sha256"], entry["final_text_sha256"])
        self.assertTrue(pipeline.verify_queued_entry("social-a", row)["verified"])
        # Late write: the queue file is rewritten with a different payload text.
        row["payload"]["text"] += " (late write)"
        (paths.content_dir("social-a") / "publish_queue.jsonl").write_text(
            json.dumps(row) + "\n", encoding="utf-8")
        [tampered] = pipeline.admin_publish_queue("social-a")
        verdict = pipeline.verify_queued_entry("social-a", tampered)
        self.assertFalse(verdict["verified"])
        self.assertTrue(any("does not match" in p for p in verdict["problems"]), verdict)

    def test_an_entry_moved_to_another_runtime_is_refused(self):
        self.bind()
        entry = pipeline.enqueue("social-a", self.cand, self.payload, "exp-1")
        moved = dict(entry, bot="social-b")
        verdict = pipeline.verify_queued_entry("social-b", moved)
        self.assertFalse(verdict["verified"])
        self.assertTrue(any("scoped" in p for p in verdict["problems"]), verdict)

    def test_a_symlinked_queue_is_refused_everywhere(self):
        self.bind()
        queue = paths.content_dir("social-a") / "publish_queue.jsonl"
        elsewhere = Path(self.tmp) / "elsewhere.jsonl"
        elsewhere.write_text("", encoding="utf-8")
        if queue.exists():
            queue.unlink()
        queue.symlink_to(elsewhere)
        with self.assertRaises(pipeline.ReviewBindingError):
            pipeline.enqueue("social-a", self.cand, self.payload, "exp-1")
        with self.assertRaises(pipeline.ReviewBindingError):
            pipeline.admin_publish_queue("social-a")
        self.assertEqual(elsewhere.read_text(encoding="utf-8"), "")   # nothing written through
        verdict = pipeline.verify_queued_entry("social-a", {"bot": "social-a"})
        self.assertFalse(verdict["verified"])
        self.assertTrue(any("symlink" in p for p in verdict["problems"]), verdict)


class CulturalFinalBindingTest(unittest.TestCase):
    """A required cultural review must name the exact final text (G-CULTURAL)."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.prior = os.environ.get("SBOTS_HOME")
        os.environ["SBOTS_HOME"] = self.tmp
        self.p = personas.load("cultural-primandir-atman")
        self.p.setdefault("source_requirements", {})["named_reviewer"] = "reviewer-fixture"

    def tearDown(self):
        if self.prior is None:
            os.environ.pop("SBOTS_HOME", None)
        else:
            os.environ["SBOTS_HOME"] = self.prior

    def _candidate(self, content_sha256=None, cand=None):
        cand = cand if cand is not None else pipeline.ideate(self.p, SIGNAL)
        cand["cultural_review_binding"] = cr.make_binding(
            candidate_id=cand["content_id"], reviewer_id="reviewer-fixture",
            reviewer_version="1", evidence_refs=cand["source_refs"], status=cr.ACCEPTED,
            rationale="fixture", content_sha256=content_sha256).as_dict()
        return pipeline.review(self.p, cand)

    def test_a_cultural_pass_without_the_final_text_hash_is_withheld_at_final_review(self):
        cand = self._candidate()
        self.assertTrue(cand["review_passed"], cand["review"])   # draft-level pass
        payload = pipeline.format_for_platform(cand, self.p["platform_strategy"]["primary"][0])
        final = pipeline.final_review(self.p, cand, payload)
        self.assertFalse(final["passed"])
        self.assertFalse(final["checks"]["cultural"]["passed"])
        self.assertIn("not bound to the final rendered text", final["checks"]["cultural"]["reason"])
        with self.assertRaises(pipeline.ReviewBindingError):
            pipeline.enqueue("social-a", cand, payload, "exp-c")

    def test_a_cultural_pass_bound_to_the_final_text_is_accepted(self):
        """The reviewer sees the rendering of THIS candidate and signs its hash."""
        platform = self.p["platform_strategy"]["primary"][0]
        cand = pipeline.ideate(self.p, SIGNAL)
        rendered = pipeline.format_for_platform(cand, platform)["text"]   # what the reviewer saw
        cand = self._candidate(content_sha256=_sha(rendered), cand=cand)
        payload = pipeline.format_for_platform(cand, platform)
        self.assertEqual(payload["text"], rendered)      # formatting is deterministic per candidate
        final = pipeline.final_review(self.p, cand, payload)
        self.assertTrue(final["checks"]["cultural"]["passed"], final["reasons"])
        self.assertEqual(final["final_text_sha256"], _sha(payload["text"]))

    def test_a_cultural_binding_for_other_text_is_refused(self):
        platform = self.p["platform_strategy"]["primary"][0]
        cand = self._candidate(content_sha256=_sha("some other rendering"))
        payload = pipeline.format_for_platform(cand, platform)
        final = pipeline.final_review(self.p, cand, payload)
        self.assertFalse(final["checks"]["cultural"]["passed"])


class DecisionBindingTest(_Case):
    def test_cycle_binds_the_review_to_the_queued_text(self):
        seed("social-a")
        rec = decision.run_cycle("social-a", "social-a")
        self.assertEqual(rec["outcome"], "candidate_created")
        [row] = pipeline.admin_publish_queue("social-a")
        digest = _sha(row["payload"]["text"])
        self.assertEqual(rec["verify"]["final_text_sha256"], digest)
        self.assertEqual(row["final_text_sha256"], digest)
        self.assertTrue(rec["verify"]["final_review_bound"])
        self.assertTrue(pipeline.verify_queued_entry("social-a", row)["verified"])
        hist = read_jsonl(paths.content_dir("social-a") / "content_history.jsonl")
        self.assertEqual(hist[-1]["final_text_sha256"], digest)

    def test_cycle_withholds_when_the_final_review_fails(self):
        seed("social-a")
        real = pipeline.final_review

        def failing(persona, candidate, payload):
            binding = real(persona, candidate, payload)
            binding["checks"]["voice"] = {"check": "voice", "passed": False,
                                          "reason": "fixture: banned move in final text"}
            binding["passed"] = False
            binding["reasons"] = ["voice: fixture: banned move in final text"]
            return binding

        with mock.patch.object(pipeline, "final_review", failing):
            rec = decision.run_cycle("social-a", "social-a")
        self.assertEqual(rec["outcome"], "withheld")
        gates = {g["gate"] for g in rec["execute"]["gate_failures"]}
        self.assertIn("final_review", gates)
        self.assertFalse(rec["verify"]["final_review_bound"])
        self.assertFalse(rec["verify"]["experiment_registered"])
        self.assertEqual(pipeline.admin_publish_queue("social-a"), [])
        self.assertEqual(list(paths.experiments_dir("social-a").glob("exp-*.json")), [])


if __name__ == "__main__":
    unittest.main()
