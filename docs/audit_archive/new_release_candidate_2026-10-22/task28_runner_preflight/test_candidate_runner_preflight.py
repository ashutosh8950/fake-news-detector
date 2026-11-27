import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from candidate_runner_preflight import PreflightError, run_preflight, write_gate_report


POLICY_FP = "a" * 64
HASH_A = "1" * 64
HASH_B = "2" * 64


class CandidateRunnerPreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        self.allowed = self.repo / "evaluation_results" / "new_release_candidate_2026-10-22" / "task28_runner_preflight"
        self.allowed.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def evidence(self):
        hashes = {"data/Fake.csv": HASH_A, "data/True.csv": HASH_B}
        source_fp = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()
        return {
            "schema_version": "task28_evidence_v1",
            "output_root": str(self.allowed / "candidate-001"),
            "dataset_identity": {
                "source_paths": list(hashes), "source_sha256": hashes,
                "approved": True, "approval_source": "synthetic-owner-record"
            },
            "provenance_licensing": {
                "status": "reviewed", "approved": True,
                "evidence_source": "synthetic-rights-record",
                "intended_uses": ["training", "artifact_distribution", "hosting"]
            },
            "grouping_policy": {"policy_id": "synthetic_policy", "configuration_fingerprint": POLICY_FP, "approved": True},
            "partition_manifest": {
                "manifest_sha256": "3" * 64, "certificate_sha256": "4" * 64,
                "source_data_fingerprint": source_fp, "policy_id": "synthetic_policy",
                "approved": True, "certificate_status": "verified"
            },
            "partition_integrity": {"approved": True, "group_disjoint": True, "coverage_complete": True, "leakage_checks_passed": True},
            "environment": {"status": "reviewed", "approved": True, "lock_status": "accepted_with_limitations", "python": "3.11.9", "platform": "synthetic-windows", "record_source": "synthetic-environment-record"},
            "runner_isolation": {"containment_verified": True, "overwrite_protection": True, "failure_cleanup": True},
            "release_authorization": {"approved": True, "distinct_new_release": True, "authenticated": True, "evidence_source": "synthetic-trust-record"}
        }

    def execute(self, evidence=None):
        return run_preflight(evidence or self.evidence(), repo_root=self.repo, allowed_output_root=self.allowed, expected_policy_fingerprint=POLICY_FP)

    def assert_refused(self, evidence, text=None, expect_absent=True):
        result = self.execute(evidence)
        self.assertEqual(result["decision"], "REFUSED")
        self.assertFalse(result["training_permitted"])
        self.assertFalse(result["side_effects"]["directories_created"])
        if expect_absent:
            self.assertFalse((self.allowed / "candidate-001").exists())
        if text:
            self.assertIn(text, result["reason"])

    def test_complete_synthetic_evidence_stops_before_training(self):
        result = self.execute()
        self.assertEqual(result["decision"], "PREFLIGHT_PASS_STOPPED_BEFORE_TRAINING")
        self.assertFalse(result["training_permitted"])
        self.assertFalse((self.allowed / "candidate-001").exists())

    def test_missing_provenance_or_license_refuses(self):
        evidence = self.evidence(); evidence["provenance_licensing"] = {}
        self.assert_refused(evidence, "provenance/licensing")

    def test_unapproved_policy_refuses(self):
        evidence = self.evidence(); evidence["grouping_policy"]["approved"] = False
        self.assert_refused(evidence, "grouping policy")

    def test_wrong_policy_fingerprint_refuses(self):
        evidence = self.evidence(); evidence["grouping_policy"]["configuration_fingerprint"] = "b" * 64
        self.assert_refused(evidence, "fingerprint")

    def test_manifest_source_mismatch_refuses(self):
        evidence = self.evidence(); evidence["partition_manifest"]["source_data_fingerprint"] = "5" * 64
        self.assert_refused(evidence, "source fingerprint")

    def test_malformed_certificate_refuses(self):
        evidence = self.evidence(); evidence["partition_manifest"]["certificate_sha256"] = "bad"
        self.assert_refused(evidence, "SHA-256")

    def test_unapproved_partition_integrity_refuses(self):
        evidence = self.evidence(); evidence["partition_integrity"]["group_disjoint"] = False
        self.assert_refused(evidence, "partition integrity")

    def test_stale_environment_refuses(self):
        evidence = self.evidence(); evidence["environment"]["lock_status"] = "missing"
        self.assert_refused(evidence, "environment")

    def test_missing_release_authorization_refuses(self):
        evidence = self.evidence(); evidence["release_authorization"] = {}
        self.assert_refused(evidence, "release authorization")

    def test_unsigned_editable_approval_refuses(self):
        evidence = self.evidence(); evidence["release_authorization"]["authenticated"] = False
        self.assert_refused(evidence, "release authorization")

    def test_invalid_output_paths_refuse(self):
        for path in (str(self.repo / "models" / "candidate"), str(self.allowed / ".." / ".." / "shared"), str(self.allowed)):
            evidence = self.evidence(); evidence["output_root"] = path
            self.assert_refused(evidence, "output_root")

    def test_existing_nonempty_output_refuses(self):
        target = self.allowed / "candidate-001"; target.mkdir(); (target / "old.txt").write_text("keep", encoding="utf-8")
        self.assert_refused(self.evidence(), "already exists", expect_absent=False)
        self.assertEqual((target / "old.txt").read_text(encoding="utf-8"), "keep")

    def test_malformed_json_equivalent_object_refuses(self):
        evidence = self.evidence(); evidence["dataset_identity"] = []
        self.assert_refused(evidence, "dataset_identity")

    def test_unexpected_type_refuses(self):
        evidence = self.evidence(); evidence["partition_integrity"]["coverage_complete"] = "true"
        self.assert_refused(evidence, "partition integrity")

    def test_stale_prior_result_refuses_after_input_change(self):
        first = self.execute()
        evidence = self.evidence(); evidence["prior_result_fingerprint"] = first["evidence_fingerprint"]
        evidence["dataset_identity"]["source_sha256"]["data/Fake.csv"] = "9" * 64
        evidence["partition_manifest"]["source_data_fingerprint"] = hashlib.sha256(json.dumps(evidence["dataset_identity"]["source_sha256"], sort_keys=True).encode()).hexdigest()
        self.assert_refused(evidence, "stale")

    def test_missing_required_dataset_fields_refuses(self):
        evidence = self.evidence(); del evidence["dataset_identity"]["source_sha256"]["data/True.csv"]
        self.assert_refused(evidence, "matching")

    def test_report_writer_rejects_outside_root_and_overwrite(self):
        report_root = self.allowed / "reports"; report_root.mkdir()
        with self.assertRaises(PreflightError):
            write_gate_report({"decision": "REFUSED"}, self.repo / "outside.json", approved_report_root=report_root)
        report = report_root / "gate.json"
        write_gate_report({"decision": "REFUSED"}, report, approved_report_root=report_root)
        with self.assertRaises(PreflightError):
            write_gate_report({"decision": "REFUSED"}, report, approved_report_root=report_root)


if __name__ == "__main__":
    unittest.main()
