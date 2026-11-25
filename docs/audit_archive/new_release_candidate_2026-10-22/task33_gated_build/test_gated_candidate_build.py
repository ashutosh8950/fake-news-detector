import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
import gated_candidate_build as gated


class GatedCandidateBuildTests(unittest.TestCase):
    def base_evidence(self):
        return {"schema_version": "task30_evidence_v1", "release_id": "synthetic-candidate"}

    def call(self, evidence=None, **kwargs):
        defaults = dict(
            repo_root=REPO,
            allowed_output_root=HERE / "tmp-output",
            evidence_root=HERE,
            trusted_file_digests={"x": "a" * 64},
            trusted_source_digests={"x": "b" * 64},
            trusted_public_keys={"org-key": b"test"},
            expected_policy_config={"policy": "synthetic"},
        )
        defaults.update(kwargs)
        return gated.run_gated_preflight(evidence or self.base_evidence(), **defaults)

    def test_missing_roots_and_digests_refuse(self):
        self.assertEqual(self.call(trusted_file_digests=None)["decision"], "REFUSED")
        self.assertEqual(self.call(trusted_source_digests=None)["decision"], "REFUSED")
        self.assertEqual(self.call(trusted_public_keys=None)["decision"], "REFUSED")
        self.assertEqual(self.call(expected_policy_config=None)["decision"], "REFUSED")

    def test_legacy_and_injected_authorization_are_rejected(self):
        self.assertIn("legacy", self.call({"schema_version": "task28_evidence_v1"})["reason"])
        for field in ("training_permitted", "build_authorized", "authenticated", "approved"):
            evidence = self.base_evidence(); evidence[field] = True
            self.assertEqual(self.call(evidence)["decision"], "REFUSED")

    def test_test_key_and_secure_failure_refuse(self):
        result = self.call(trusted_public_keys={"test-key": b"synthetic"})
        self.assertIn("synthetic", result["reason"])
        with patch.object(gated, "candidate_preflight_only", side_effect=RuntimeError("synthetic")):
            result = self.call(trusted_public_keys={"org-key": b"synthetic"})
        self.assertIn("failed closed", result["reason"])

    def test_secure_boundary_success_still_cannot_authorize(self):
        passing = {"decision": "PREFLIGHT_PASS_STOPPED_BEFORE_TRAINING"}
        with patch.object(gated, "candidate_preflight_only", return_value=passing):
            result = self.call(trusted_public_keys={"org-key": b"synthetic"})
        self.assertFalse(result["training_permitted"])
        self.assertFalse(result["build_authorized"])
        self.assertFalse(result["artifacts_created"])

    def test_dry_run_is_blocked_without_dataset_reads_or_outputs(self):
        with tempfile.TemporaryDirectory(dir=HERE) as temp:
            config = Path(temp) / "config.json"
            config.write_text(json.dumps({"candidate_id": "synthetic"}), encoding="utf-8")
            result = gated.dry_run_config(config)
            self.assertEqual(result["decision"], "REFUSED")
            self.assertTrue(result["blockers"])
            self.assertFalse((Path(temp) / "models").exists())

    def test_dry_run_path_escape_and_malformed_config_refuse(self):
        self.assertEqual(gated.dry_run_config(REPO / "train.py")["decision"], "REFUSED")
        with tempfile.TemporaryDirectory(dir=HERE) as temp:
            bad = Path(temp) / "bad.json"; bad.write_text("{", encoding="utf-8")
            self.assertEqual(gated.dry_run_config(bad)["decision"], "REFUSED")

    def test_legacy_candidate_cli_entry_points_refuse_before_training(self):
        for script in (REPO / "train.py", REPO / "phase2_calibration.py"):
            completed = subprocess.run(
                [sys.executable, str(script), "--candidate-release"],
                cwd=REPO, capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(completed.returncode, 1)
            self.assertIn("gated candidate-build orchestrator", completed.stderr + completed.stdout)

    def test_orchestrator_does_not_import_legacy_entry_points(self):
        source = (HERE / "gated_candidate_build.py").read_text(encoding="utf-8")
        self.assertNotIn("import train", source)
        self.assertNotIn("import phase2_calibration", source)
        self.assertNotIn("train()", source)
        self.assertNotIn("from train", source)
        self.assertNotIn("from phase2_calibration", source)

    def test_import_and_dry_run_have_no_authorization(self):
        self.assertFalse(gated.REFUSAL["training_permitted"])
        self.assertFalse(gated.REFUSAL["build_authorized"])


if __name__ == "__main__":
    unittest.main()
