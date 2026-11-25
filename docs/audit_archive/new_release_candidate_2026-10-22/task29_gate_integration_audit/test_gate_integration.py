import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

TASK28 = Path(__file__).parents[1] / "task28_runner_preflight"
sys.path.insert(0, str(TASK28))
from candidate_runner_preflight import run_preflight  # noqa: E402


class GateIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        self.allowed = self.repo / "evaluation_results" / "new_release_candidate_2026-10-22" / "task29"
        self.allowed.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def evidence(self):
        source = {"data/Fake.csv": "1" * 64, "data/True.csv": "2" * 64}
        return {
            "schema_version": "task28_evidence_v1",
            "output_root": str(self.allowed / "candidate"),
            "dataset_identity": {"source_paths": list(source), "source_sha256": source, "approved": True, "approval_source": "synthetic-owner-record"},
            "provenance_licensing": {"status": "reviewed", "approved": True, "evidence_source": "synthetic-rights-record", "intended_uses": ["training", "artifact_distribution", "hosting"]},
            "grouping_policy": {"policy_id": "policy-x", "configuration_fingerprint": "a" * 64, "approved": True},
            "partition_manifest": {"manifest_sha256": "3" * 64, "certificate_sha256": "4" * 64, "source_data_fingerprint": hashlib.sha256(json.dumps(source, sort_keys=True).encode()).hexdigest(), "policy_id": "policy-x", "approved": True, "certificate_status": "verified"},
            "partition_integrity": {"approved": True, "group_disjoint": True, "coverage_complete": True, "leakage_checks_passed": True},
            "environment": {"status": "reviewed", "approved": True, "lock_status": "accepted_with_limitations", "python": "3.11.9", "platform": "synthetic", "record_source": "synthetic-env"},
            "runner_isolation": {"containment_verified": True, "overwrite_protection": True, "failure_cleanup": True},
            "release_authorization": {"approved": True, "distinct_new_release": True, "authenticated": True, "evidence_source": "synthetic-auth-record"},
        }

    def execute(self, evidence=None, expected="a" * 64):
        return run_preflight(evidence or self.evidence(), repo_root=self.repo, allowed_output_root=self.allowed, expected_policy_fingerprint=expected)

    def test_manifest_source_hash_mismatch_is_refused(self):
        e = self.evidence(); e["partition_manifest"]["source_data_fingerprint"] = "9" * 64
        self.assertEqual(self.execute(e)["decision"], "REFUSED")

    def test_policy_fingerprint_mismatch_is_refused(self):
        e = self.evidence(); e["grouping_policy"]["configuration_fingerprint"] = "b" * 64
        self.assertEqual(self.execute(e)["decision"], "REFUSED")

    def test_unknown_license_is_refused(self):
        e = self.evidence(); e["provenance_licensing"]["status"] = "unknown"
        self.assertEqual(self.execute(e)["decision"], "REFUSED")

    def test_environment_without_accepted_lock_is_refused(self):
        e = self.evidence(); e["environment"]["lock_status"] = "missing"
        self.assertEqual(self.execute(e)["decision"], "REFUSED")

    def test_stale_result_after_input_change_is_refused(self):
        first = self.execute()
        e = self.evidence(); e["prior_result_fingerprint"] = first["evidence_fingerprint"]
        e["dataset_identity"]["source_sha256"]["data/Fake.csv"] = "9" * 64
        e["partition_manifest"]["source_data_fingerprint"] = hashlib.sha256(json.dumps(e["dataset_identity"]["source_sha256"], sort_keys=True).encode()).hexdigest()
        self.assertEqual(self.execute(e)["decision"], "REFUSED")

    def test_unsigned_authorization_is_refused(self):
        e = self.evidence(); e["release_authorization"]["authenticated"] = False
        self.assertEqual(self.execute(e)["decision"], "REFUSED")

    def test_valid_certificate_hash_does_not_bind_to_manifest_in_current_code(self):
        e = self.evidence()
        e["partition_manifest"]["manifest_sha256"] = "8" * 64
        e["partition_manifest"]["certificate_sha256"] = "7" * 64
        result = self.execute(e)
        self.assertEqual(result["decision"], "PREFLIGHT_PASS_STOPPED_BEFORE_TRAINING")

    def test_editable_authenticated_claim_is_not_cryptographically_verified(self):
        e = self.evidence()
        e["release_authorization"]["evidence_source"] = "local-editable-json"
        result = self.execute(e)
        self.assertEqual(result["decision"], "PREFLIGHT_PASS_STOPPED_BEFORE_TRAINING")

    def test_all_synthetic_gates_pass_but_training_never_launches(self):
        result = self.execute()
        self.assertEqual(result["decision"], "PREFLIGHT_PASS_STOPPED_BEFORE_TRAINING")
        self.assertFalse(result["training_permitted"])
        self.assertFalse((self.allowed / "candidate").exists())


if __name__ == "__main__":
    unittest.main()
