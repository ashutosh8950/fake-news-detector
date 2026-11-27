"""Preflight-only gate for a future TruthScan candidate build.

This module deliberately has no training, dataset parsing, model-loading, or
artifact-generation path. It validates an explicit evidence package and
returns a machine-readable refusal/pass decision. A pass means only that the
synthetic/preflight evidence is internally complete; ``training_permitted`` is
always false in this task implementation.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Mapping


GATES = (
    "dataset_identity",
    "provenance_licensing",
    "grouping_policy",
    "partition_manifest",
    "partition_integrity",
    "environment",
    "runner_isolation",
    "release_authorization",
)
SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")
PARTITION_NAMES = ("train", "selection", "calibration", "test")


class PreflightError(ValueError):
    pass


def _fail(gates: dict[str, dict[str, Any]], gate: str, reason: str) -> None:
    gates[gate] = {"status": "BLOCKED", "reason": reason}


def _pass(gates: dict[str, dict[str, Any]], gate: str, evidence: str) -> None:
    gates[gate] = {"status": "PASS", "evidence": evidence}


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise PreflightError(f"{name} must be an object")
    return value


def _sha(value: Any, name: str) -> None:
    if not isinstance(value, str) or not SHA256.fullmatch(value):
        raise PreflightError(f"{name} must be a 64-character SHA-256 value")


def _canonical_fingerprint(evidence: Mapping[str, Any]) -> str:
    relevant = {key: evidence.get(key) for key in (
        "dataset_identity", "provenance_licensing", "grouping_policy",
        "partition_manifest", "partition_integrity", "environment",
        "runner_isolation", "release_authorization",
    )}
    encoded = json.dumps(relevant, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _validate_output_root(value: Any, repo_root: Path, allowed_root: Path) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PreflightError("output_root is required")
    root = Path(value).expanduser().resolve(strict=False)
    repo = repo_root.resolve(strict=True)
    allowed = allowed_root.resolve(strict=True)
    if not root.is_absolute() or not str(root).lower().startswith(str(allowed).lower() + os.sep.lower()):
        raise PreflightError("output_root is outside the approved candidate namespace")
    if root.exists():
        raise PreflightError("output_root already exists; overwrite is refused")
    if root == repo / "models" or str(root).lower().startswith(str((repo / "models")).lower() + os.sep.lower()):
        raise PreflightError("production model paths are forbidden")
    if str(root).lower().startswith(str((repo / "evaluation_results")).lower() + os.sep.lower()) and not str(root).lower().startswith(str(allowed).lower() + os.sep.lower()):
        raise PreflightError("shared evaluation paths are forbidden")
    return str(root)


def run_preflight(
    evidence: Mapping[str, Any],
    *,
    repo_root: os.PathLike[str] | str,
    allowed_output_root: os.PathLike[str] | str,
    expected_policy_fingerprint: str | None = None,
) -> dict[str, Any]:
    """Validate evidence without creating directories or reading dataset rows."""

    gates: dict[str, dict[str, Any]] = {}
    result: dict[str, Any] = {
        "schema_version": "task28_preflight_result_v1",
        "decision": "REFUSED",
        "training_permitted": False,
        "build_authorized": False,
        "authorization_mode": "legacy_non_authorizing",
        "gates": gates,
        "side_effects": {"directories_created": False, "artifacts_created": False},
    }
    try:
        ev = _mapping(evidence, "evidence")
        if ev.get("schema_version") != "task28_evidence_v1":
            raise PreflightError("unsupported or missing evidence schema_version")
        output_root = _validate_output_root(ev.get("output_root"), Path(repo_root), Path(allowed_output_root))
        result["output_root"] = output_root

        identity = _mapping(ev.get("dataset_identity"), "dataset_identity")
        paths = identity.get("source_paths")
        hashes = identity.get("source_sha256")
        if not isinstance(paths, list) or not paths or not isinstance(hashes, Mapping) or set(paths) != set(hashes):
            raise PreflightError("dataset identity requires matching non-empty source_paths and source_sha256")
        for path in paths:
            if not isinstance(path, str) or not path or Path(path).is_absolute() or ".." in Path(path).parts:
                raise PreflightError("dataset source paths must be repository-relative and traversal-free")
            _sha(hashes.get(path), f"dataset_identity.source_sha256[{path}]")
        if identity.get("approved") is not True or identity.get("approval_source") in (None, ""):
            raise PreflightError("dataset identity is not explicitly approved with a source")
        _pass(gates, "dataset_identity", "approved source paths and SHA-256 records are structurally valid")

        rights = _mapping(ev.get("provenance_licensing"), "provenance_licensing")
        if rights.get("status") != "reviewed" or rights.get("evidence_source") in (None, "") or rights.get("intended_uses") != ["training", "artifact_distribution", "hosting"]:
            raise PreflightError("provenance/licensing evidence is missing, unreviewed, or incomplete for intended uses")
        if rights.get("approved") is not True:
            raise PreflightError("provenance/licensing approval is not true")
        _pass(gates, "provenance_licensing", "reviewed evidence covers all declared intended uses")

        policy = _mapping(ev.get("grouping_policy"), "grouping_policy")
        if policy.get("approved") is not True or not isinstance(policy.get("policy_id"), str) or not SHA256.fullmatch(str(policy.get("configuration_fingerprint", ""))):
            raise PreflightError("grouping policy approval or configuration fingerprint is invalid")
        if expected_policy_fingerprint and policy["configuration_fingerprint"].lower() != expected_policy_fingerprint.lower():
            raise PreflightError("grouping policy fingerprint does not match expected configuration")
        _pass(gates, "grouping_policy", "approved policy identifier and fingerprint are valid")

        manifest = _mapping(ev.get("partition_manifest"), "partition_manifest")
        for field in ("manifest_sha256", "certificate_sha256", "source_data_fingerprint"):
            _sha(manifest.get(field), f"partition_manifest.{field}")
        if manifest.get("approved") is not True or manifest.get("policy_id") != policy.get("policy_id"):
            raise PreflightError("partition manifest is unapproved or names a different policy")
        if manifest.get("source_data_fingerprint") != hashlib.sha256(json.dumps(dict(hashes), sort_keys=True).encode()).hexdigest():
            raise PreflightError("partition manifest source fingerprint does not match dataset identity")
        if manifest.get("certificate_status") != "verified":
            raise PreflightError("partition certificate is missing or not verified")
        _pass(gates, "partition_manifest", "manifest, certificate, policy, and source fingerprint are consistent")

        integrity = _mapping(ev.get("partition_integrity"), "partition_integrity")
        required_integrity = ("group_disjoint", "coverage_complete", "leakage_checks_passed")
        if any(integrity.get(field) is not True for field in required_integrity) or integrity.get("approved") is not True:
            raise PreflightError("partition integrity evidence is incomplete or unapproved")
        _pass(gates, "partition_integrity", "group disjointness, coverage, and leakage checks are explicitly true")

        environment = _mapping(ev.get("environment"), "environment")
        if environment.get("status") != "reviewed" or environment.get("approved") is not True or environment.get("lock_status") not in ("complete", "accepted_with_limitations"):
            raise PreflightError("environment evidence is missing, unreviewed, or not accepted")
        if not isinstance(environment.get("python"), str) or not isinstance(environment.get("platform"), str) or not environment.get("record_source"):
            raise PreflightError("environment record lacks Python, platform, or source")
        _pass(gates, "environment", "reviewed environment record and accepted lock status are present")

        isolation = _mapping(ev.get("runner_isolation"), "runner_isolation")
        if any(isolation.get(field) is not True for field in ("containment_verified", "overwrite_protection", "failure_cleanup")):
            raise PreflightError("runner isolation evidence is incomplete")
        _pass(gates, "runner_isolation", "containment, overwrite protection, and cleanup are explicitly true")

        auth = _mapping(ev.get("release_authorization"), "release_authorization")
        if auth.get("approved") is not True or auth.get("distinct_new_release") is not True or auth.get("authenticated") is not True or not auth.get("evidence_source"):
            raise PreflightError("release authorization is missing, unsigned, or not for a distinct new release")
        _pass(gates, "release_authorization", "explicit authenticated authorization for a distinct new release is present")

        current_fingerprint = _canonical_fingerprint(ev)
        if ev.get("prior_result_fingerprint") not in (None, current_fingerprint):
            raise PreflightError("prior gate result is stale for the current evidence")
        result["evidence_fingerprint"] = current_fingerprint
        result["decision"] = "PREFLIGHT_PASS_STOPPED_BEFORE_TRAINING"
        result["training_permitted"] = False
        result["reason"] = "All synthetic preflight gates passed; this interface never launches training."
    except (PreflightError, TypeError, ValueError, KeyError) as exc:
        result["decision"] = "REFUSED"
        result["reason"] = str(exc)
    return result


def write_gate_report(
    result: Mapping[str, Any],
    path: os.PathLike[str] | str,
    *,
    approved_report_root: os.PathLike[str] | str,
) -> None:
    """Write a report only below an existing, approved report root.

    This helper does not create a candidate output root, refuses overwrite,
    and removes only its own temporary file if serialization/write fails.
    """
    destination = Path(path).expanduser().resolve(strict=False)
    report_root = Path(approved_report_root).expanduser().resolve(strict=True)
    if destination == report_root or report_root not in destination.parents:
        raise PreflightError("gate report path is outside the approved report root")
    if destination.exists():
        raise PreflightError("gate report already exists; overwrite is refused")
    temporary = destination.with_name(destination.name + ".tmp")
    try:
        temporary.write_text(json.dumps(dict(result), indent=2, sort_keys=True), encoding="utf-8")
        temporary.replace(destination)
    except Exception:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        raise


# Minimal Ed25519 verification based on RFC 8032.  It avoids adding a package
# dependency to the candidate workspace.  The trusted key mapping is supplied
# out-of-band by the caller; a key embedded in an approval record is never used
# as a trust root.
_Q = 2**255 - 19
_L = 2**252 + 27742317777372353535851937790883648493
_D = (-121665 * pow(121666, _Q - 2, _Q)) % _Q
_I = pow(2, (_Q - 1) // 4, _Q)
_BY = (4 * pow(5, _Q - 2, _Q)) % _Q
_BX = 0


def _xrecover(y: int) -> int:
    xx = (y * y - 1) * pow(_D * y * y + 1, _Q - 2, _Q) % _Q
    x = pow(xx, (_Q + 3) // 8, _Q)
    if (x * x - xx) % _Q:
        x = x * _I % _Q
    if x & 1:
        x = _Q - x
    return x


_BX = _xrecover(_BY)
_B = (_BX, _BY)


def _ed_add(p: tuple[int, int], q: tuple[int, int]) -> tuple[int, int]:
    x1, y1 = p
    x2, y2 = q
    den_x = pow(1 + _D * x1 * x2 * y1 * y2, _Q - 2, _Q)
    den_y = pow(1 - _D * x1 * x2 * y1 * y2, _Q - 2, _Q)
    return ((x1 * y2 + x2 * y1) * den_x % _Q, (y1 * y2 + x1 * x2) * den_y % _Q)


def _ed_mul(point: tuple[int, int], scalar: int) -> tuple[int, int]:
    result = (0, 1)
    addend = point
    while scalar:
        if scalar & 1:
            result = _ed_add(result, addend)
        addend = _ed_add(addend, addend)
        scalar >>= 1
    return result


def _ed_encode(point: tuple[int, int]) -> bytes:
    x, y = point
    value = y | ((x & 1) << 255)
    return value.to_bytes(32, "little")


def _ed_decode(raw: bytes) -> tuple[int, int]:
    if len(raw) != 32:
        raise ValueError("Ed25519 point must be 32 bytes")
    value = int.from_bytes(raw, "little")
    y = value & ((1 << 255) - 1)
    if y >= _Q:
        raise ValueError("invalid Ed25519 point")
    x = _xrecover(y)
    if ((x * x - (y * y - 1) * pow(_D * y * y + 1, _Q - 2, _Q)) % _Q) != 0:
        raise ValueError("invalid Ed25519 point")
    if ((x & 1) << 255) != (value & (1 << 255)):
        x = _Q - x
    return x, y


def _ed25519_verify(public_key: bytes, signature: bytes, message: bytes) -> bool:
    if len(public_key) != 32 or len(signature) != 64:
        return False
    try:
        a_point = _ed_decode(public_key)
        r_point = _ed_decode(signature[:32])
        s = int.from_bytes(signature[32:], "little")
        if s >= _L:
            return False
        challenge = int.from_bytes(hashlib.sha512(signature[:32] + public_key + message).digest(), "little") % _L
        return _ed_encode(_ed_mul(_B, s)) == _ed_encode(_ed_add(r_point, _ed_mul(a_point, challenge)))
    except (ValueError, ZeroDivisionError):
        return False


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _safe_evidence_file(root: Path, relative: Any, *, label: str) -> Path:
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise PreflightError(f"{label} must be a relative, traversal-free path")
    candidate = (root / relative).resolve(strict=True)
    root_resolved = root.resolve(strict=True)
    if root_resolved not in candidate.parents:
        raise PreflightError(f"{label} escapes the evidence root")
    current = root_resolved
    for part in Path(relative).parts:
        current = current / part
        if current.is_symlink():
            raise PreflightError(f"{label} may not use symlinks")
    if not candidate.is_file():
        raise PreflightError(f"{label} must be a regular file")
    return candidate


def _verified_file(root: Path, descriptor: Mapping[str, Any], trusted_digests: Mapping[str, str], label: str) -> tuple[Path, bytes, str]:
    path = _safe_evidence_file(root, descriptor.get("path"), label=label)
    expected = descriptor.get("sha256")
    _sha(expected, f"{label}.sha256")
    trust_id = descriptor.get("trusted_digest_id")
    if not isinstance(trust_id, str) or trusted_digests.get(trust_id, "").lower() != expected.lower():
        raise PreflightError(f"{label} digest is absent or not from the external trusted digest set")
    content = path.read_bytes()
    actual = hashlib.sha256(content).hexdigest()
    if actual.lower() != expected.lower():
        raise PreflightError(f"{label} bytes do not match the trusted digest")
    return path, content, actual


def _validate_partition_manifest(manifest: Mapping[str, Any], expected_source: Mapping[str, str], policy: Mapping[str, Any]) -> None:
    if manifest.get("schema_version") != "task30_partition_manifest_v1":
        raise PreflightError("partition manifest schema is unavailable or unsupported")
    if manifest.get("policy_id") != policy.get("policy_id") or manifest.get("policy_fingerprint") != policy.get("configuration_fingerprint"):
        raise PreflightError("partition manifest policy binding does not match approved policy")
    if manifest.get("source_sha256") != dict(expected_source):
        raise PreflightError("partition manifest source hashes do not match dataset identity")
    partitions = manifest.get("partitions")
    if not isinstance(partitions, Mapping) or set(partitions) != set(PARTITION_NAMES):
        raise PreflightError("partition manifest must contain exactly train, selection, calibration, and test")
    seen_rows: set[str] = set()
    groups: dict[str, str] = {}
    for partition in PARTITION_NAMES:
        entries = partitions[partition]
        if not isinstance(entries, list) or not entries:
            raise PreflightError(f"partition {partition} is missing or empty")
        for entry in entries:
            if not isinstance(entry, Mapping) or not isinstance(entry.get("row_id"), str) or not isinstance(entry.get("group_id"), str):
                raise PreflightError("partition membership requires row_id and group_id")
            row_id = entry["row_id"]
            if row_id in seen_rows:
                raise PreflightError("partition row identifiers overlap")
            seen_rows.add(row_id)
            group_id = entry["group_id"]
            prior = groups.setdefault(group_id, partition)
            if prior != partition:
                raise PreflightError("group identifiers cross prohibited partitions")
    expected_rows = manifest.get("expected_row_ids")
    if not isinstance(expected_rows, list) or len(expected_rows) != len(set(expected_rows)) or set(expected_rows) != seen_rows:
        raise PreflightError("partition manifest lacks complete, unique expected row coverage")
    if not isinstance(manifest.get("mixed_label_groups"), list):
        raise PreflightError("mixed-label handling is missing from partition manifest")


def _approval_payload(evidence: Mapping[str, Any], manifest_digest: str, certificate_digest: str, environment_digest: str) -> dict[str, Any]:
    identity = evidence["dataset_identity"]
    policy = evidence["grouping_policy"]
    return {
        "candidate_id": evidence.get("candidate_id"),
        "dataset_source_sha256": identity.get("source_sha256"),
        "policy_id": policy.get("policy_id"),
        "policy_fingerprint": policy.get("configuration_fingerprint"),
        "manifest_sha256": manifest_digest,
        "certificate_sha256": certificate_digest,
        "environment_sha256": environment_digest,
        "scope": ["training", "artifact_distribution", "hosting"],
        "decision": "approve_distinct_new_release_preflight",
    }


def run_preflight_secure(
    evidence: Mapping[str, Any],
    *,
    repo_root: os.PathLike[str] | str,
    allowed_output_root: os.PathLike[str] | str,
    evidence_root: os.PathLike[str] | str,
    trusted_file_digests: Mapping[str, str],
    trusted_source_digests: Mapping[str, str],
    trusted_public_keys: Mapping[str, bytes],
    expected_policy_config: Mapping[str, Any] | None,
    revoked_key_ids: set[str] | None = None,
    test_only: bool = False,
) -> dict[str, Any]:
    """Strict Task 30 preflight. It never creates output or enables training."""
    result: dict[str, Any] = {
        "schema_version": "task30_preflight_result_v1",
        "decision": "REFUSED",
        "training_permitted": False,
        "side_effects": {"directories_created": False, "artifacts_created": False},
        "gates": {},
    }
    try:
        ev = _mapping(evidence, "evidence")
        if ev.get("schema_version") != "task30_evidence_v1":
            raise PreflightError("Task 30 evidence schema is required")
        if not test_only:
            raise PreflightError("production trust-root provisioning is not configured; refusing authorization")
        if test_only is False and any(str(key).startswith("test-") for key in trusted_public_keys):
            raise PreflightError("test trust keys cannot be configured for a non-test run")
        _validate_output_root(ev.get("output_root"), Path(repo_root), Path(allowed_output_root))
        if not isinstance(ev.get("candidate_id"), str) or not ev["candidate_id"]:
            raise PreflightError("candidate_id is required")

        identity = _mapping(ev.get("dataset_identity"), "dataset_identity")
        source = identity.get("source_sha256")
        paths = identity.get("source_paths")
        if not isinstance(source, Mapping) or not isinstance(paths, list) or set(paths) != set(source) or identity.get("approved") is not True:
            raise PreflightError("dataset identity approval and source records are incomplete")
        for rel in paths:
            file_path = _safe_evidence_file(Path(repo_root), rel, label=f"dataset source {rel}")
            _sha(source[rel], f"dataset source {rel}")
            if trusted_source_digests.get(rel, "").lower() != source[rel].lower():
                raise PreflightError(f"dataset source hash for {rel} is not from the external trusted digest set")
            if hashlib.sha256(file_path.read_bytes()).hexdigest().lower() != source[rel].lower():
                raise PreflightError(f"dataset source bytes do not match expected hash for {rel}")
        result["gates"]["dataset_identity"] = "PASS"

        rights = _mapping(ev.get("provenance_licensing"), "provenance_licensing")
        if rights.get("status") != "reviewed" or rights.get("approved") is not True or rights.get("evidence_source") in (None, "") or rights.get("intended_uses") != ["training", "artifact_distribution", "hosting"]:
            raise PreflightError("provenance/licensing evidence is unresolved")
        result["gates"]["provenance_licensing"] = "PASS"

        policy = _mapping(ev.get("grouping_policy"), "grouping_policy")
        if not isinstance(expected_policy_config, Mapping):
            raise PreflightError("trusted expected policy configuration is required")
        if policy.get("approved") is not True or not isinstance(policy.get("policy_id"), str) or not SHA256.fullmatch(str(policy.get("configuration_fingerprint", ""))):
            raise PreflightError("grouping policy approval/fingerprint is invalid")
        if hashlib.sha256(_canonical(expected_policy_config)).hexdigest() != policy["configuration_fingerprint"]:
            raise PreflightError("grouping policy fingerprint does not match canonical approved configuration")
        result["gates"]["grouping_policy"] = "PASS"

        root = Path(evidence_root).resolve(strict=True)
        manifest_desc = _mapping(ev.get("partition_manifest"), "partition_manifest")
        manifest_path, manifest_bytes, manifest_digest = _verified_file(root, _mapping(manifest_desc.get("manifest_file"), "manifest_file"), trusted_file_digests, "manifest")
        cert_path, cert_bytes, certificate_digest = _verified_file(root, _mapping(manifest_desc.get("certificate_file"), "certificate_file"), trusted_file_digests, "certificate")
        manifest = _mapping(json.loads(manifest_bytes), "manifest")
        certificate = _mapping(json.loads(cert_bytes), "certificate")
        if certificate.get("manifest_sha256") != manifest_digest or certificate.get("source_sha256") != dict(source) or certificate.get("policy_id") != policy["policy_id"] or certificate.get("policy_fingerprint") != policy["configuration_fingerprint"]:
            raise PreflightError("certificate does not bind the exact manifest, source, and policy")
        _validate_partition_manifest(manifest, source, policy)
        result["gates"]["partition_manifest"] = "PASS"
        result["gates"]["partition_integrity"] = "PASS"

        environment_desc = _mapping(ev.get("environment"), "environment")
        env_path, env_bytes, environment_digest = _verified_file(root, _mapping(environment_desc.get("environment_file"), "environment_file"), trusted_file_digests, "environment")
        environment = _mapping(json.loads(env_bytes), "environment file")
        if environment.get("schema_version") != "task30_environment_v1" or environment.get("lock_status") != "complete" or environment.get("python") != environment_desc.get("python") or environment.get("platform") != environment_desc.get("platform") or environment_desc.get("approved") is not True:
            raise PreflightError("environment evidence is incomplete or does not match the selected configuration")
        lock_hash = environment.get("lock_sha256")
        _sha(lock_hash, "environment.lock_sha256")
        if environment_desc.get("lock_sha256") != lock_hash:
            raise PreflightError("environment lock hash does not match the environment record")
        lock_desc = _mapping(environment.get("lock_file"), "environment lock_file")
        _, _, actual_lock_digest = _verified_file(root, lock_desc, trusted_file_digests, "environment lock file")
        if actual_lock_digest.lower() != lock_hash.lower():
            raise PreflightError("environment lock file bytes do not match the recorded lock hash")
        result["gates"]["environment"] = "PASS"

        auth_desc = _mapping(ev.get("release_authorization"), "release_authorization")
        auth_path, auth_bytes, auth_digest = _verified_file(root, _mapping(auth_desc.get("approval_file"), "approval_file"), trusted_file_digests, "approval")
        approval = _mapping(json.loads(auth_bytes), "approval")
        key_id = approval.get("key_id")
        if not isinstance(key_id, str) or key_id in (revoked_key_ids or set()) or key_id not in trusted_public_keys:
            raise PreflightError("approval key is unknown, revoked, or not externally trusted")
        payload = approval.get("payload")
        signature_hex = approval.get("signature_hex")
        if not isinstance(payload, Mapping) or not isinstance(signature_hex, str):
            raise PreflightError("approval signature or payload is missing")
        expected_payload = _approval_payload(ev, manifest_digest, certificate_digest, environment_digest)
        if dict(payload) != expected_payload:
            raise PreflightError("approval payload does not bind the exact candidate evidence")
        try:
            signature = bytes.fromhex(signature_hex)
        except ValueError as exc:
            raise PreflightError("approval signature is malformed") from exc
        if not _ed25519_verify(trusted_public_keys[key_id], signature, _canonical(payload)):
            raise PreflightError("approval signature is invalid")
        result["gates"]["release_authorization"] = "PASS"
        result["gates"]["runner_isolation"] = "PASS" if _mapping(ev.get("runner_isolation"), "runner_isolation").get("verified") is True else "BLOCKED"
        if result["gates"]["runner_isolation"] != "PASS":
            raise PreflightError("runner isolation is not independently verified")
        result["decision"] = "PREFLIGHT_PASS_STOPPED_BEFORE_TRAINING"
        result["reason"] = "All strict synthetic gates passed; training remains disabled by design."
    except (PreflightError, TypeError, ValueError, KeyError, OSError, json.JSONDecodeError) as exc:
        result["decision"] = "REFUSED"
        result["reason"] = str(exc)
    return result
