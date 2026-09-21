"""SB-CTL-012 — regressions for the artifact graph validator / readiness reporter.

Pure, hermetic tests over synthetic registries plus a tmp-dir repo for file-ref
checks. Also a meta-test that the validator PASSES (no hard errors) on the real
canonical registry, so structural regressions are caught but expected roadmap
drift stays a warning.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

_SB = Path(__file__).resolve().parent.parent          # social-bots/
sys.path.insert(0, str(_SB / "bin"))
import validate_artifacts as V  # noqa: E402


def _art(aid, status="ACCEPTED", depends_on=None, canonical_ref=None, evidence=None):
    return {"id": aid, "name": aid, "type": "t", "version_gate": "V0.1",
            "owner": "x", "status": status, "canonical_ref": canonical_ref,
            "depends_on": depends_on or [], "story_points": None,
            "evidence": evidence or [], "last_verified_ref": "x"}


def _index(artifacts, status_values=None):
    return {"schema_version": 1, "status_values": list(status_values or V.DEFAULT_STATUS_VALUES),
            "artifacts": artifacts}


def _codes(entries):
    return [e.split("]")[0].lstrip("[") for e in entries]


class StructuralErrorTests(unittest.TestCase):
    def test_valid_graph_has_no_errors(self):
        idx = _index([_art("SB-A"), _art("SB-B", depends_on=["SB-A"]),
                      _art("SB-C", depends_on=["SB-A", "SB-B"])])
        rep = V.validate_data(idx)
        self.assertTrue(rep.ok, rep.errors)
        self.assertEqual(rep.errors, [])

    def test_duplicate_id_detected(self):
        idx = _index([_art("SB-A"), _art("SB-A")])
        rep = V.validate_data(idx)
        self.assertFalse(rep.ok)
        self.assertIn("DUPLICATE_ID", _codes(rep.errors))

    def test_invalid_status_detected(self):
        idx = _index([_art("SB-A", status="DEFINITELY_NOT_A_STATUS")])
        rep = V.validate_data(idx)
        self.assertIn("INVALID_STATUS", _codes(rep.errors))

    def test_missing_dependency_detected(self):
        idx = _index([_art("SB-A", depends_on=["SB-DOES-NOT-EXIST"])])
        rep = V.validate_data(idx)
        self.assertIn("MISSING_DEPENDENCY", _codes(rep.errors))

    def test_dependency_cycle_detected(self):
        idx = _index([_art("SB-A", depends_on=["SB-B"]),
                      _art("SB-B", depends_on=["SB-C"]),
                      _art("SB-C", depends_on=["SB-A"])])
        rep = V.validate_data(idx)
        self.assertIn("DEPENDENCY_CYCLE", _codes(rep.errors))

    def test_self_cycle_detected(self):
        idx = _index([_art("SB-A", depends_on=["SB-A"])])
        rep = V.validate_data(idx)
        self.assertIn("DEPENDENCY_CYCLE", _codes(rep.errors))

    def test_acyclic_diamond_is_ok(self):
        idx = _index([_art("SB-A"), _art("SB-B", depends_on=["SB-A"]),
                      _art("SB-C", depends_on=["SB-A"]),
                      _art("SB-D", depends_on=["SB-B", "SB-C"])])
        self.assertEqual(V.find_cycles(idx["artifacts"]), [])


class RefAndManifestTests(unittest.TestCase):
    def test_missing_packet_is_error(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "social-bots" / "artifact-packets").mkdir(parents=True)
            idx = _index([_art("SB-A",
                          canonical_ref="social-bots/artifact-packets/SB-A.md")])
            rep = V.validate_data(idx, repo_root=root)
            self.assertIn("MISSING_PACKET", _codes(rep.errors))

    def test_present_packet_passes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            pkt = root / "social-bots" / "artifact-packets" / "SB-A.md"
            pkt.parent.mkdir(parents=True)
            pkt.write_text("# packet")
            idx = _index([_art("SB-A",
                          canonical_ref="social-bots/artifact-packets/SB-A.md")])
            rep = V.validate_data(idx, repo_root=root)
            self.assertNotIn("MISSING_PACKET", _codes(rep.errors))

    def test_missing_canonical_ref_is_warning_not_error(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "social-bots").mkdir(parents=True)
            idx = _index([_art("SB-A", canonical_ref="social-bots/nope.md")])
            rep = V.validate_data(idx, repo_root=root)
            self.assertIn("MISSING_CANONICAL_REF", _codes(rep.warnings))
            self.assertNotIn("MISSING_CANONICAL_REF", _codes(rep.errors))

    def test_manifest_references_unknown_artifact_warns(self):
        idx = _index([_art("SB-CTL-001")])
        manifest = ("## V0.1 — x\nRequired:\n- SB-CTL-001 present.\n"
                    "- SB-V99-001 missing from index.\n")
        rep = V.validate_data(idx, manifest_text=manifest)
        self.assertIn("MANIFEST_UNKNOWN_ARTIFACT", _codes(rep.warnings))
        # It is drift, not a structural break: no hard error from it.
        self.assertNotIn("MANIFEST_UNKNOWN_ARTIFACT", _codes(rep.errors))


class ContradictionTests(unittest.TestCase):
    def test_accepted_depending_on_unaccepted_warns(self):
        idx = _index([_art("SB-DEP", status="CHANGES_REQUIRED"),
                      _art("SB-A", status="ACCEPTED", depends_on=["SB-DEP"])])
        rep = V.validate_data(idx)
        self.assertIn("CONTRADICTORY_STATE", _codes(rep.warnings))

    def test_accepted_with_unresolved_evidence_warns(self):
        idx = _index([_art("SB-A", status="ACCEPTED",
                            evidence=["reviewer note: changes-required before final"])])
        rep = V.validate_data(idx)
        self.assertIn("CONTRADICTORY_STATE", _codes(rep.warnings))

    def test_benign_evidence_does_not_false_positive(self):
        idx = _index([_art("SB-A", status="ACCEPTED",
                            evidence=["provider fails closed on timeout (correct)"])])
        rep = V.validate_data(idx)
        self.assertNotIn("CONTRADICTORY_STATE", _codes(rep.warnings))


class ReadinessTests(unittest.TestCase):
    MANIFEST = (
        "## V1.7 — checkpoint\nRequired:\n- SB-V17-001 x.\n"
        "## V2.0 — autonomous growth engine\n"
        "Required for operational promotion:\n"
        "- accepted V1.7 checkpoint;\n"
        "- SB-V20-001 strategy.\n- SB-V20-004 operational bundle.\n"
        "Engineering-readiness artifact:\n"
        "- SB-V20-099 engineering-readiness bundle.\n"
    )

    def test_engineering_and_operational_are_parsed_separately(self):
        ms = {m.version: m for m in V.parse_manifest(self.MANIFEST)}
        v20 = ms["V2.0"]
        self.assertEqual(v20.engineering_required, ["SB-V20-099"])
        self.assertEqual(sorted(v20.operational_required), ["SB-V20-001", "SB-V20-004"])
        self.assertIn("V1.7", v20.prereq_versions)

    def test_v2_engineering_ready_while_operational_blocked(self):
        # SB-V20-099 accepted (engineering ready), but operational artifacts are not.
        arts = [_art("SB-V17-001", status="ACCEPTED"),
                _art("SB-V20-099", status="ACCEPTED"),
                _art("SB-V20-001", status="PLANNED"),
                _art("SB-V20-004", status="BLOCKED")]
        rep = V.validate_data(_index(arts), manifest_text=self.MANIFEST)
        v20 = rep.readiness["V2.0"]
        self.assertTrue(v20["engineering_ready"],
                        "SB-V20-099 accepted => engineering ready")
        self.assertFalse(v20["operational_ready"],
                         "operational promotion must stay blocked")
        # The two states are distinct keys, never collapsed.
        self.assertNotEqual(v20["engineering_ready"], v20["operational_ready"])
        self.assertIn("SB-V20-004", [b["id"] for b in v20["operational_blockers"]])

    def test_operational_requires_prereq_milestone_accepted(self):
        # Even with all V2.0 operational artifacts accepted, an unmet prereq
        # milestone (V1.7 not accepted) keeps operational promotion blocked.
        arts = [_art("SB-V17-001", status="CHANGES_REQUIRED"),
                _art("SB-V20-099", status="ACCEPTED"),
                _art("SB-V20-001", status="ACCEPTED"),
                _art("SB-V20-004", status="ACCEPTED")]
        rep = V.validate_data(_index(arts), manifest_text=self.MANIFEST)
        v20 = rep.readiness["V2.0"]
        self.assertFalse(v20["operational_ready"])
        self.assertIn("V1.7", v20["unmet_prereq_versions"])


class RealRegistryMetaTest(unittest.TestCase):
    def test_validator_passes_on_canonical_registry(self):
        # Guards against a future change that would hard-fail CI on the real
        # (intentionally in-progress) registry. Drift is warnings, not errors.
        repo_root = _SB.parent
        rep = V.validate_repo(repo_root)
        self.assertTrue(rep.ok, f"unexpected hard errors: {rep.errors}")
        # And it produces a readiness report with the V2 distinction present.
        self.assertIn("V2.0", rep.readiness)
        self.assertIn("engineering_ready", rep.readiness["V2.0"])
        self.assertIn("operational_ready", rep.readiness["V2.0"])


if __name__ == "__main__":
    unittest.main()
