import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

TASK28 = Path(__file__).parents[1] / "task28_runner_preflight"
sys.path.insert(0, str(TASK28))
import candidate_runner_preflight as preflight  # noqa: E402


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sign_for_test(seed, message):
    h = hashlib.sha512(seed).digest()
    scalar = int.from_bytes(h[:32], "little")
    scalar &= (1 << 254) - 8
    scalar |= 1 << 254
    public = preflight._ed_encode(preflight._ed_mul(preflight._B, scalar))
    prefix = h[32:]
    r = int.from_bytes(hashlib.sha512(prefix + message).digest(), "little") % preflight._L
    point_r = preflight._ed_encode(preflight._ed_mul(preflight._B, r))
    challenge = int.from_bytes(hashlib.sha512(point_r + public + message).digest(), "little") % preflight._L
    s = (r + challenge * scalar) % preflight._L
    return public, point_r + s.to_bytes(32, "little")


class SecurePreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.repo = root / "repo"
        self.repo.mkdir()
        self.allowed = self.repo / "evaluation_results" / "new_release_candidate_2026-10-22" / "task30"
        self.allowed.mkdir(parents=True)
        self.evidence_root = root / "evidence"
        self.evidence_root.mkdir()
        self.seed = bytes(range(32))
        self.public, _ = sign_for_test(self.seed, b"key-check")
        self.policy_config = {"policy_id": "policy-x", "selected_key_types": ["body"]}
        self.policy_fp = hashlib.sha256(canonical(self.policy_config)).hexdigest()

    def tearDown(self):
        self.tmp.cleanup()

    def _write(self, name, value):
        path = self.evidence_root / name
        raw = value if isinstance(value, bytes) else canonical(value)
        path.write_bytes(raw)
        return path, hashlib.sha256(raw).hexdigest()

    def evidence(self):
        fake = self.repo / "data" / "Fake.csv"; true = self.repo / "data" / "True.csv"
        fake.parent.mkdir(exist_ok=True); fake.write_bytes(b"fake-synthetic"); true.write_bytes(b"true-synthetic")
        source = {"data/Fake.csv": hashlib.sha256(fake.read_bytes()).hexdigest(), "data/True.csv": hashlib.sha256(true.read_bytes()).hexdigest()}
        manifest = {
            "schema_version": "task30_partition_manifest_v1", "policy_id": "policy-x", "policy_fingerprint": self.policy_fp,
            "source_sha256": source, "expected_row_ids": ["r1", "r2", "r3", "r4"],
            "partitions": {"train": [{"row_id": "r1", "group_id": "g1"}], "selection": [{"row_id": "r2", "group_id": "g2"}], "calibration": [{"row_id": "r3", "group_id": "g3"}], "test": [{"row_id": "r4", "group_id": "g4"}]},
            "mixed_label_groups": []
        }
        _, manifest_hash = self._write("manifest.json", manifest)
        certificate = {"manifest_sha256": manifest_hash, "source_sha256": source, "policy_id": "policy-x", "policy_fingerprint": self.policy_fp}
        _, certificate_hash = self._write("certificate.json", certificate)
        _, lock_hash = self._write("lock.txt", b"synthetic-lock")
        environment = {"schema_version": "task30_environment_v1", "python": "3.12.10", "platform": "synthetic-windows-amd64", "lock_status": "complete", "lock_sha256": lock_hash, "lock_file": {"path": "lock.txt", "sha256": lock_hash, "trusted_digest_id": "lock"}}
        _, environment_hash = self._write("environment.json", environment)
        e = {
            "schema_version": "task30_evidence_v1", "candidate_id": "synthetic-candidate-001", "output_root": str(self.allowed / "candidate"),
            "dataset_identity": {"source_paths": list(source), "source_sha256": source, "approved": True},
            "provenance_licensing": {"status": "reviewed", "approved": True, "evidence_source": "synthetic-rights-record", "intended_uses": ["training", "artifact_distribution", "hosting"]},
            "grouping_policy": {"policy_id": "policy-x", "configuration_fingerprint": self.policy_fp, "approved": True},
            "partition_manifest": {"manifest_file": {"path": "manifest.json", "sha256": manifest_hash, "trusted_digest_id": "manifest"}, "certificate_file": {"path": "certificate.json", "sha256": certificate_hash, "trusted_digest_id": "certificate"}},
            "environment": {"environment_file": {"path": "environment.json", "sha256": environment_hash, "trusted_digest_id": "environment"}, "python": "3.12.10", "platform": "synthetic-windows-amd64", "lock_sha256": lock_hash, "lock_file": {"path": "lock.txt", "sha256": lock_hash, "trusted_digest_id": "lock"}, "approved": True},
            "runner_isolation": {"verified": True}
        }
        payload = {"candidate_id": e["candidate_id"], "dataset_source_sha256": source, "policy_id": "policy-x", "policy_fingerprint": self.policy_fp, "manifest_sha256": manifest_hash, "certificate_sha256": certificate_hash, "environment_sha256": environment_hash, "scope": ["training", "artifact_distribution", "hosting"], "decision": "approve_distinct_new_release_preflight"}
        _, signature = sign_for_test(self.seed, canonical(payload))
        approval = {"key_id": "test-key", "payload": payload, "signature_hex": signature.hex()}
        _, approval_hash = self._write("approval.json", approval)
        e["release_authorization"] = {"approval_file": {"path": "approval.json", "sha256": approval_hash, "trusted_digest_id": "approval"}}
        trusted = {"manifest": manifest_hash, "certificate": certificate_hash, "environment": environment_hash, "lock": lock_hash, "approval": approval_hash}
        return e, trusted, source

    def execute(self, evidence=None, trusted=None, **kwargs):
        if evidence is None:
            e, default_trusted, default_source = self.evidence()
        else:
            e, default_trusted, default_source = evidence, trusted, {key: evidence["dataset_identity"]["source_sha256"][key] for key in evidence["dataset_identity"]["source_sha256"]}
        test_only = kwargs.pop("test_only", True)
        return preflight.run_preflight_secure(e, repo_root=self.repo, allowed_output_root=self.allowed, evidence_root=self.evidence_root, trusted_file_digests=trusted or default_trusted, trusted_source_digests=default_source, trusted_public_keys={"test-key": self.public}, expected_policy_config=self.policy_config, test_only=test_only, **kwargs)

    def test_valid_synthetic_evidence_stops_before_training(self):
        result = self.execute()
        self.assertEqual(result["decision"], "PREFLIGHT_PASS_STOPPED_BEFORE_TRAINING")
        self.assertFalse(result["training_permitted"])
        self.assertFalse((self.allowed / "candidate").exists())

    def test_manifest_bytes_wrong_trusted_hash_refuse(self):
        e, trusted, _ = self.evidence(); (self.evidence_root / "manifest.json").write_bytes(b"changed")
        self.assertEqual(self.execute(e, trusted)["decision"], "REFUSED")

    def test_certificate_binding_wrong_digest_refuse(self):
        e, trusted, _ = self.evidence(); cert = json.loads((self.evidence_root / "certificate.json").read_text()); cert["manifest_sha256"] = "f" * 64; (self.evidence_root / "certificate.json").write_bytes(canonical(cert))
        self.assertEqual(self.execute(e, trusted)["decision"], "REFUSED")

    def test_unsigned_self_reported_digest_refuse(self):
        e, trusted, _ = self.evidence(); trusted.clear()
        self.assertEqual(self.execute(e, trusted)["decision"], "REFUSED")

    def test_missing_or_wrong_policy_fingerprint_refuse(self):
        e, trusted, _ = self.evidence(); e["grouping_policy"]["configuration_fingerprint"] = None
        self.assertEqual(self.execute(e, trusted)["decision"], "REFUSED")
        e, trusted, _ = self.evidence(); e["grouping_policy"]["configuration_fingerprint"] = "a" * 64
        self.assertEqual(self.execute(e, trusted)["decision"], "REFUSED")

    def test_signature_bound_to_different_dataset_refuse(self):
        e, trusted, _ = self.evidence(); e["dataset_identity"]["source_sha256"]["data/Fake.csv"] = "a" * 64
        self.assertEqual(self.execute(e, trusted)["decision"], "REFUSED")

    def test_modified_approval_signature_refuse(self):
        e, trusted, _ = self.evidence(); approval = json.loads((self.evidence_root / "approval.json").read_text()); approval["payload"]["candidate_id"] = "other"; (self.evidence_root / "approval.json").write_bytes(canonical(approval))
        self.assertEqual(self.execute(e, trusted)["decision"], "REFUSED")

    def test_embedded_or_untrusted_key_refuse(self):
        e, trusted, _ = self.evidence(); self.assertEqual(self.execute(e, trusted, revoked_key_ids={"test-key"})["decision"], "REFUSED")
        self.assertEqual(self.execute(e, trusted, test_only=False)["decision"], "REFUSED")

    def test_incomplete_overlap_and_group_split_refuse(self):
        e, trusted, _ = self.evidence(); manifest = json.loads((self.evidence_root / "manifest.json").read_text()); manifest["partitions"]["test"][0]["group_id"] = "g1"; (self.evidence_root / "manifest.json").write_bytes(canonical(manifest)); self.assertEqual(self.execute(e, trusted)["decision"], "REFUSED")

    def test_missing_membership_refuse(self):
        e, trusted, _ = self.evidence(); manifest = json.loads((self.evidence_root / "manifest.json").read_text()); del manifest["expected_row_ids"]; (self.evidence_root / "manifest.json").write_bytes(canonical(manifest)); self.assertEqual(self.execute(e, trusted)["decision"], "REFUSED")

    def test_environment_mismatch_or_malformed_refuse(self):
        e, trusted, _ = self.evidence(); e["environment"]["python"] = "3.11.9"; self.assertEqual(self.execute(e, trusted)["decision"], "REFUSED")
        e, trusted, _ = self.evidence(); (self.evidence_root / "environment.json").write_bytes(b"not-json"); self.assertEqual(self.execute(e, trusted)["decision"], "REFUSED")

    def test_path_escape_refuse(self):
        e, trusted, _ = self.evidence(); e["partition_manifest"]["manifest_file"]["path"] = "../manifest.json"; self.assertEqual(self.execute(e, trusted)["decision"], "REFUSED")

    def test_all_unsigned_records_never_enable_training(self):
        e, trusted, _ = self.evidence(); e["release_authorization"]["approval_file"]["trusted_digest_id"] = "missing"; result = self.execute(e, trusted); self.assertEqual(result["decision"], "REFUSED"); self.assertFalse(result["training_permitted"])


if __name__ == "__main__":
    unittest.main()
