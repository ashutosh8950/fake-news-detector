import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "task30_gate_security"))
sys.path.insert(0, str(ROOT / "task31_secure_integration"))
sys.path.insert(0, str(ROOT / "task28_runner_preflight"))
from candidate_runner_preflight import run_preflight, run_preflight_secure  # noqa: E402
from secure_build_boundary import candidate_preflight_only, invoke_build  # noqa: E402


class RedTeamBoundaryTests(unittest.TestCase):
    def fixture(self):
        from test_secure_preflight import SecurePreflightTests
        fixture = SecurePreflightTests("test_valid_synthetic_evidence_stops_before_training")
        fixture.setUp(); self.addCleanup(fixture.tearDown)
        evidence, trusted, source = fixture.evidence()
        return fixture, evidence, trusted, source

    def strict(self, fixture, evidence, trusted, source, **kwargs):
        return run_preflight_secure(evidence, repo_root=fixture.repo, allowed_output_root=fixture.allowed, evidence_root=fixture.evidence_root, trusted_file_digests=trusted, trusted_source_digests=source, trusted_public_keys={"test-key": fixture.public}, expected_policy_config=fixture.policy_config, test_only=True, **kwargs)

    def boundary(self, fixture, evidence, keys=None, trusted=None, source=None):
        return candidate_preflight_only(evidence, repo_root=fixture.repo, allowed_output_root=fixture.allowed, evidence_root=fixture.evidence_root, trusted_file_digests=trusted, trusted_source_digests=source, trusted_public_keys=keys, expected_policy_config=fixture.policy_config)

    def test_strict_synthetic_success_never_authorizes_or_creates(self):
        fixture, evidence, trusted, source = self.fixture(); result = self.strict(fixture, evidence, trusted, source)
        self.assertEqual(result["decision"], "PREFLIGHT_PASS_STOPPED_BEFORE_TRAINING")
        self.assertFalse(result["training_permitted"]); self.assertFalse((fixture.allowed / "candidate").exists())

    def test_legacy_success_is_explicitly_non_authorizing(self):
        fixture, evidence, _, _ = self.fixture(); legacy = dict(evidence); legacy["schema_version"] = "task28_evidence_v1"
        result = run_preflight(legacy, repo_root=fixture.repo, allowed_output_root=fixture.allowed)
        self.assertFalse(result["build_authorized"]); self.assertEqual(result["authorization_mode"], "legacy_non_authorizing")

    def test_boundary_rejects_legacy_result(self):
        fixture, evidence, trusted, source = self.fixture(); evidence["schema_version"] = "task28_evidence_v1"
        result = self.boundary(fixture, evidence, {"real-key": fixture.public}, trusted, source)
        self.assertEqual(result["decision"], "REFUSED")

    def test_fabricated_preflight_result_is_not_evidence(self):
        fixture, _, trusted, source = self.fixture(); fabricated = {"decision": "PREFLIGHT_PASS_STOPPED_BEFORE_TRAINING", "training_permitted": True, "build_authorized": True}
        result = self.boundary(fixture, fabricated, {"real-key": fixture.public}, trusted, source)
        self.assertEqual(result["decision"], "REFUSED")

    def test_production_mode_refuses_arbitrary_renamed_synthetic_key(self):
        fixture, evidence, trusted, source = self.fixture()
        result = self.boundary(fixture, evidence, {"production-looking-key": fixture.public}, trusted, source)
        self.assertEqual(result["decision"], "REFUSED")

    def test_missing_trust_roots_refuse(self):
        fixture, evidence, _, source = self.fixture(); self.assertEqual(self.boundary(fixture, evidence, {}, None, source)["decision"], "REFUSED")

    def test_stale_approval_after_release_id_change_refuses(self):
        fixture, evidence, trusted, source = self.fixture(); evidence["candidate_id"] = "different-release"
        self.assertEqual(self.strict(fixture, evidence, trusted, source)["decision"], "REFUSED")

    def test_stale_lock_and_environment_refuse(self):
        fixture, evidence, trusted, source = self.fixture(); (fixture.evidence_root / "lock.txt").write_bytes(b"new-lock")
        self.assertEqual(self.strict(fixture, evidence, trusted, source)["decision"], "REFUSED")

    def test_path_escape_refuses(self):
        fixture, evidence, trusted, source = self.fixture(); evidence["partition_manifest"]["manifest_file"]["path"] = "../outside.json"
        self.assertEqual(self.strict(fixture, evidence, trusted, source)["decision"], "REFUSED")

    def test_exception_and_optional_gate_failure_refuse(self):
        fixture, evidence, trusted, source = self.fixture(); evidence["provenance_licensing"]["status"] = "unknown"
        self.assertEqual(self.strict(fixture, evidence, trusted, source)["decision"], "REFUSED")
        evidence["partition_manifest"]["manifest_file"]["path"] = "missing.json"
        self.assertEqual(self.strict(fixture, evidence, trusted, source)["decision"], "REFUSED")

    def test_lower_level_build_function_is_not_reachable(self):
        with self.assertRaises(Exception): invoke_build()

    def test_direct_training_entry_points_are_not_securely_integrated(self):
        train_source = (ROOT.parent.parent / "train.py").read_text(encoding="utf-8")
        calibration_source = (ROOT.parent.parent / "phase2_calibration.py").read_text(encoding="utf-8")
        self.assertIn("def train", train_source); self.assertIn("joblib.dump", train_source)
        self.assertIn("def main", calibration_source); self.assertIn("joblib.dump", calibration_source)
        self.assertNotIn("run_preflight_secure", train_source); self.assertNotIn("run_preflight_secure", calibration_source)

    def test_no_model_or_release_artifact_is_created(self):
        fixture, evidence, trusted, source = self.fixture(); self.strict(fixture, evidence, trusted, source)
        self.assertFalse(any(fixture.allowed.rglob("*.pkl"))); self.assertFalse(any(fixture.allowed.rglob("*.joblib")))


if __name__ == "__main__":
    unittest.main()
