import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

TASK34 = Path(__file__).resolve().parent
TASK33 = TASK34.parent / "task33_gated_build"
REPO = TASK34.parents[2]
sys.path.insert(0, str(TASK33))
import gated_candidate_build as gated  # noqa: E402


class Task34VerificationTests(unittest.TestCase):
    def evidence(self):
        return {"schema_version": "task30_evidence_v1", "release_id": "synthetic-34"}

    def kwargs(self):
        return {
            "repo_root": REPO,
            "allowed_output_root": TASK34 / "synthetic-output",
            "evidence_root": TASK34,
            "trusted_file_digests": {"manifest": "a" * 64},
            "trusted_source_digests": {"source": "b" * 64},
            "trusted_public_keys": {"org-key": b"synthetic-not-a-production-key"},
            "expected_policy_config": {"policy_id": "synthetic"},
        }

    def call_preflight(self, evidence=None, **changes):
        args = self.kwargs(); args.update(changes)
        return gated.run_gated_preflight(evidence or self.evidence(), **args)

    def test_train_candidate_flag_refuses_before_imports(self):
        result = subprocess.run([sys.executable, str(REPO / "train.py"), "--candidate-release"], cwd=REPO, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("gated candidate-build orchestrator", result.stderr + result.stdout)

    def test_calibration_candidate_flag_refuses_before_imports(self):
        result = subprocess.run([sys.executable, str(REPO / "phase2_calibration.py"), "--release-candidate"], cwd=REPO, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("gated candidate-build orchestrator", result.stderr + result.stdout)

    def test_missing_authorization_and_roots_refuse(self):
        self.assertEqual(self.call_preflight()["decision"], "REFUSED")
        self.assertEqual(self.call_preflight(trusted_file_digests=None)["decision"], "REFUSED")
        self.assertEqual(self.call_preflight(trusted_source_digests=None)["decision"], "REFUSED")
        self.assertEqual(self.call_preflight(trusted_public_keys=None)["decision"], "REFUSED")

    def test_injected_authorization_booleans_do_not_authorize(self):
        for field in ("training_permitted", "build_authorized", "approved", "authenticated"):
            evidence = self.evidence(); evidence[field] = True
            result = self.call_preflight(evidence)
            self.assertEqual(result["decision"], "REFUSED")
            self.assertFalse(result["training_permitted"])
            self.assertFalse(result["build_authorized"])

    def test_legacy_result_and_legacy_schema_do_not_authorize(self):
        legacy = {"schema_version": "task28_evidence_v1"}
        result = self.call_preflight(legacy)
        self.assertEqual(result["decision"], "REFUSED")
        self.assertIn("legacy", result["reason"])

    def test_secure_failure_and_exception_fail_closed(self):
        with patch.object(gated, "candidate_preflight_only", return_value={"decision": "REFUSED", "reason": "synthetic gate"}):
            self.assertEqual(self.call_preflight()["decision"], "REFUSED")
        with patch.object(gated, "candidate_preflight_only", side_effect=RuntimeError("synthetic")):
            result = self.call_preflight()
        self.assertEqual(result["decision"], "REFUSED")
        self.assertIn("failed closed", result["reason"])

    def test_synthetic_key_is_not_a_production_root(self):
        result = self.call_preflight(trusted_public_keys={"test-synthetic": b"key"})
        self.assertIn("synthetic", result["reason"])

    def test_bound_input_changes_cannot_be_authorized_by_wrapper(self):
        for field in ("release_id", "dataset_digest", "policy_fingerprint", "partition_certificate_hash"):
            evidence = self.evidence(); evidence[field] = "changed"
            result = self.call_preflight(evidence)
            self.assertEqual(result["decision"], "REFUSED")

    def test_missing_real_evidence_categories_block(self):
        evidence = self.evidence()
        for field in ("provenance", "licensing", "grouping_approval", "partition_approval", "environment", "dependency_lock"):
            candidate = dict(evidence); candidate[field] = None
            self.assertEqual(self.call_preflight(candidate)["decision"], "REFUSED")

    def test_environment_and_digest_mismatch_cannot_be_accepted(self):
        result = self.call_preflight(trusted_file_digests={"manifest": "c" * 64}, expected_policy_config={"policy_id": "different"})
        self.assertEqual(result["decision"], "REFUSED")

    def test_boundary_is_the_only_secure_call_and_legacy_mains_are_not_called(self):
        with patch.object(gated, "candidate_preflight_only", return_value={"decision": "REFUSED", "reason": "synthetic"}) as boundary:
            self.call_preflight()
        boundary.assert_called_once()
        source = (TASK33 / "gated_candidate_build.py").read_text(encoding="utf-8")
        self.assertNotIn("import train", source)
        self.assertNotIn("import phase2_calibration", source)
        self.assertNotIn("train()", source)

    def test_import_has_no_training_side_effects(self):
        self.assertFalse(gated.REFUSAL["training_permitted"])
        self.assertFalse(gated.REFUSAL["build_authorized"])
        self.assertFalse(gated.REFUSAL["artifacts_created"])

    def test_dry_run_is_refusal_only_and_creates_no_artifacts(self):
        with tempfile.TemporaryDirectory(dir=TASK33) as temp:
            config = Path(temp) / "synthetic.json"
            config.write_text(json.dumps({"candidate_id": "synthetic-34"}), encoding="utf-8")
            result = gated.dry_run_config(config)
            self.assertEqual(result["decision"], "REFUSED")
            self.assertFalse((Path(temp) / "models").exists())
            self.assertFalse((Path(temp) / "release").exists())

    def test_secure_success_still_has_no_authorization(self):
        with patch.object(gated, "candidate_preflight_only", return_value={"decision": "PREFLIGHT_PASS_STOPPED_BEFORE_TRAINING"}):
            result = self.call_preflight()
        self.assertEqual(result["decision"], "REFUSED")
        self.assertFalse(result["training_permitted"])
        self.assertFalse(result["build_authorized"])
        self.assertFalse(result["artifacts_created"])

    def test_lower_level_build_is_not_present_in_orchestrator(self):
        source = (TASK33 / "gated_candidate_build.py").read_text(encoding="utf-8")
        self.assertNotIn("invoke_build(", source)
        self.assertNotIn("joblib", source)
        self.assertNotIn("pandas", source)

    def test_malformed_config_and_path_escape_refuse(self):
        with tempfile.TemporaryDirectory(dir=TASK34) as temp:
            bad = Path(temp) / "bad.json"; bad.write_text("{", encoding="utf-8")
            self.assertEqual(gated.dry_run_config(bad)["decision"], "REFUSED")
        self.assertEqual(gated.dry_run_config(REPO / "train.py")["decision"], "REFUSED")


if __name__ == "__main__":
    unittest.main()
