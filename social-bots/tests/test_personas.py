import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import personas  # noqa: E402


class PersonaTest(unittest.TestCase):
    def test_all_personas_valid(self):
        for p in personas.load_all():
            errs = personas.validate(p)
            self.assertEqual(errs, [], f"{p['id']} invalid: {errs}")

    def test_five_personas_three_general_two_cultural(self):
        allp = personas.load_all()
        general = [p for p in allp if p["kind"] == "general"]
        cultural = [p for p in allp if p["kind"] == "cultural"]
        self.assertEqual(len(general), 3)
        self.assertEqual(len(cultural), 2)

    def test_general_personas_are_distinct(self):
        rep = personas.distinctness_report()
        self.assertFalse(rep["converged"],
                         f"personas too similar: {rep}")
        self.assertLessEqual(rep["worst_jaccard"], personas.DISTINCTNESS_MAX_JACCARD)

    def test_cultural_personas_require_review(self):
        for p in personas.load_all():
            if p["kind"] == "cultural":
                sr = p["source_requirements"]
                self.assertTrue(sr["cultural_review_required"])
                self.assertTrue(sr["named_reviewer_required"])

    def test_runtime_assignment_within_three(self):
        for p in personas.load_all():
            self.assertIn(p["runtime"], ("social-a", "social-b", "social-c"))


if __name__ == "__main__":
    unittest.main()
