import json
import sys
import unittest
from pathlib import Path

TASK30 = Path(__file__).parents[1] / "task30_gate_security"
TASK28 = Path(__file__).parents[1] / "task28_runner_preflight"
sys.path.insert(0, str(TASK30))
sys.path.insert(0, str(TASK28))
from candidate_runner_preflight import run_preflight_secure  # noqa: E402
from secure_build_boundary import candidate_preflight_only, invoke_build  # noqa: E402


class SecureIntegrationTests(unittest.TestCase):
    def fixture(self):
        from test_secure_preflight import SecurePreflightTests
        fixture = SecurePreflightTests("test_valid_synthetic_evidence_stops_before_training")
        fixture.setUp()
        self.addCleanup(fixture.tearDown)
        evidence, trusted, source = fixture.evidence()
        return fixture, evidence, trusted, source

    def strict(self, fixture, evidence, trusted, source, **kwargs):
        return run_preflight_secure(
            evidence,
            repo_root=fixture.repo,
            allowed_output_root=fixture.allowed,
            evidence_root=fixture.evidence_root,
            trusted_file_digests=trusted,
            trusted_source_digests=source,
            trusted_public_keys={"test-key": fixture.public},
            expected_policy_config=fixture.policy_config,
            test_only=True,
            **kwargs,
        )

    def boundary(self, fixture, evidence, trusted=None, source=None, keys=None, policy=None):
        return candidate_preflight_only(
            evidence,
            repo_root=fixture.repo,
            allowed_output_root=fixture.allowed,
            evidence_root=fixture.evidence_root,
            trusted_file_digests=trusted,
            trusted_source_digests=source,
            trusted_public_keys=keys,
            expected_policy_config=policy,
        )

    def test_secure_success_still_disables_training(self):
        fixture, evidence, trusted, source = self.fixture()
        result = self.strict(fixture, evidence, trusted, source)
        self.assertEqual(result["decision"], "PREFLIGHT_PASS_STOPPED_BEFORE_TRAINING")
        self.assertFalse(result["training_permitted"])
        self.assertFalse((fixture.allowed / "candidate").exists())

    def test_legacy_success_cannot_authorize_build(self):
        fixture, evidence, trusted, source = self.fixture()
        legacy = dict(evidence); legacy["schema_version"] = "task28_evidence_v1"
        result = self.boundary(fixture, legacy, trusted, source, {"real-key": fixture.public}, fixture.policy_config)
        self.assertEqual(result["decision"], "REFUSED")
        self.assertFalse(result["build_authorized"])

    def test_missing_secure_preflight_inputs_refuse(self):
        fixture, evidence, trusted, source = self.fixture()
        result = self.boundary(fixture, evidence, None, source, {"real-key": fixture.public}, fixture.policy_config)
        self.assertEqual(result["decision"], "REFUSED")

    def test_secure_preflight_exception_fails_closed(self):
        fixture, evidence, trusted, source = self.fixture()
        evidence["partition_manifest"]["manifest_file"]["path"] = "missing.json"
        result = self.boundary(fixture, evidence, trusted, source, {"real-key": fixture.public}, fixture.policy_config)
        self.assertEqual(result["decision"], "REFUSED")

    def test_caller_authorization_boolean_is_rejected(self):
        fixture, evidence, trusted, source = self.fixture(); evidence["training_permitted"] = True
        result = self.boundary(fixture, evidence, trusted, source, {"real-key": fixture.public}, fixture.policy_config)
        self.assertEqual(result["decision"], "REFUSED")

    def test_missing_public_key_root_refuses(self):
        fixture, evidence, trusted, source = self.fixture()
        self.assertEqual(self.boundary(fixture, evidence, trusted, source, {}, fixture.policy_config)["decision"], "REFUSED")

    def test_embedded_test_key_is_not_production_root(self):
        fixture, evidence, trusted, source = self.fixture()
        self.assertEqual(self.boundary(fixture, evidence, trusted, source, {"test-key": fixture.public}, fixture.policy_config)["decision"], "REFUSED")

    def test_valid_signature_wrong_dataset_refuses(self):
        fixture, evidence, trusted, source = self.fixture(); evidence["dataset_identity"]["source_sha256"]["data/Fake.csv"] = "a" * 64
        self.assertEqual(self.strict(fixture, evidence, trusted, source)["decision"], "REFUSED")

    def test_valid_signature_wrong_policy_refuses(self):
        fixture, evidence, trusted, source = self.fixture(); evidence["grouping_policy"]["configuration_fingerprint"] = "a" * 64
        self.assertEqual(self.strict(fixture, evidence, trusted, source)["decision"], "REFUSED")

    def test_valid_signature_wrong_manifest_or_certificate_refuses(self):
        fixture, evidence, trusted, source = self.fixture(); certificate = json.loads((fixture.evidence_root / "certificate.json").read_text()); certificate["manifest_sha256"] = "f" * 64; (fixture.evidence_root / "certificate.json").write_text(json.dumps(certificate), encoding="utf-8")
        self.assertEqual(self.strict(fixture, evidence, trusted, source)["decision"], "REFUSED")

    def test_signed_approval_mutation_refuses(self):
        fixture, evidence, trusted, source = self.fixture(); approval = json.loads((fixture.evidence_root / "approval.json").read_text()); approval["payload"]["candidate_id"] = "changed"; (fixture.evidence_root / "approval.json").write_text(json.dumps(approval), encoding="utf-8")
        self.assertEqual(self.strict(fixture, evidence, trusted, source)["decision"], "REFUSED")

    def test_lock_change_after_approval_refuses(self):
        fixture, evidence, trusted, source = self.fixture(); (fixture.evidence_root / "lock.txt").write_bytes(b"changed-lock")
        self.assertEqual(self.strict(fixture, evidence, trusted, source)["decision"], "REFUSED")

    def test_environment_mismatch_refuses(self):
        fixture, evidence, trusted, source = self.fixture(); evidence["environment"]["python"] = "3.11.9"
        self.assertEqual(self.strict(fixture, evidence, trusted, source)["decision"], "REFUSED")

    def test_duplicate_partition_membership_refuses(self):
        fixture, evidence, trusted, source = self.fixture(); manifest = json.loads((fixture.evidence_root / "manifest.json").read_text()); manifest["partitions"]["test"][0]["row_id"] = "r1"; (fixture.evidence_root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        self.assertEqual(self.strict(fixture, evidence, trusted, source)["decision"], "REFUSED")

    def test_overlapping_group_refuses(self):
        fixture, evidence, trusted, source = self.fixture(); manifest = json.loads((fixture.evidence_root / "manifest.json").read_text()); manifest["partitions"]["test"][0]["group_id"] = "g1"; (fixture.evidence_root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        self.assertEqual(self.strict(fixture, evidence, trusted, source)["decision"], "REFUSED")

    def test_incomplete_membership_refuses(self):
        fixture, evidence, trusted, source = self.fixture(); manifest = json.loads((fixture.evidence_root / "manifest.json").read_text()); manifest["expected_row_ids"].remove("r4"); (fixture.evidence_root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        self.assertEqual(self.strict(fixture, evidence, trusted, source)["decision"], "REFUSED")

    def test_path_escape_or_symlink_alias_refuses(self):
        fixture, evidence, trusted, source = self.fixture(); evidence["partition_manifest"]["manifest_file"]["path"] = "../manifest.json"
        self.assertEqual(self.strict(fixture, evidence, trusted, source)["decision"], "REFUSED")

    def test_lower_level_build_function_is_fail_closed(self):
        with self.assertRaises(Exception):
            invoke_build()

    def test_missing_provenance_blocks_even_with_other_inputs(self):
        fixture, evidence, trusted, source = self.fixture(); evidence["provenance_licensing"]["status"] = "unknown"
        self.assertEqual(self.strict(fixture, evidence, trusted, source)["decision"], "REFUSED")

    def test_one_gate_failure_cannot_be_masked(self):
        fixture, evidence, trusted, source = self.fixture(); evidence["runner_isolation"]["verified"] = False
        self.assertEqual(self.strict(fixture, evidence, trusted, source)["decision"], "REFUSED")

    def test_no_test_creates_candidate_or_release_artifact(self):
        fixture, evidence, trusted, source = self.fixture(); result = self.strict(fixture, evidence, trusted, source)
        self.assertFalse(result["training_permitted"])
        self.assertFalse((fixture.allowed / "candidate").exists())
        self.assertFalse(any(fixture.allowed.rglob("*.pkl")))


if __name__ == "__main__":
    unittest.main()
