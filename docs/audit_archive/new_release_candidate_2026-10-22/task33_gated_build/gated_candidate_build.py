"""Single, candidate-only orchestration boundary for TruthScan.

This module is deliberately preflight-only.  It does not import the training
or calibration scripts, read dataset rows, load models, or create artifacts.
The production-style path requires independently provisioned trust roots and
delegates evidence validation to the Task 31 boundary.  Even a strict pass is
stopped before training until a separately reviewed implementation enables a
future build.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Mapping

TASK33_ROOT = Path(__file__).resolve().parent
TASK31_ROOT = TASK33_ROOT.parent / "task31_secure_integration"
if str(TASK31_ROOT) not in sys.path:
    sys.path.insert(0, str(TASK31_ROOT))

from secure_build_boundary import candidate_preflight_only  # noqa: E402


REFUSAL = {
    "decision": "REFUSED",
    "training_permitted": False,
    "build_authorized": False,
    "artifacts_created": False,
}

FORBIDDEN_AUTH_FIELDS = frozenset(
    {"training_permitted", "build_authorized", "authenticated", "approved", "allow_real_data_training"}
)


def _refuse(reason: str, **extra: Any) -> dict[str, Any]:
    result = dict(REFUSAL)
    result.update(extra)
    result["reason"] = reason
    return result


def run_gated_preflight(
    evidence: Mapping[str, Any],
    *,
    repo_root: str | Path,
    allowed_output_root: str | Path,
    evidence_root: str | Path,
    trusted_file_digests: Mapping[str, str] | None,
    trusted_source_digests: Mapping[str, str] | None,
    trusted_public_keys: Mapping[str, bytes] | None,
    expected_policy_config: Mapping[str, Any] | None,
    revoked_key_ids: set[str] | None = None,
) -> dict[str, Any]:
    """Run the only supported candidate preflight, never the build stage."""
    if not isinstance(evidence, Mapping):
        return _refuse("candidate evidence must be a mapping")
    if any(field in evidence for field in FORBIDDEN_AUTH_FIELDS):
        return _refuse("caller-supplied authorization fields cannot authorize a build")
    if evidence.get("schema_version") != "task30_evidence_v1":
        return _refuse("legacy or unknown evidence schema cannot authorize a candidate")
    if not trusted_file_digests or not trusted_source_digests:
        return _refuse("independently provisioned expected digests are required")
    if not trusted_public_keys:
        return _refuse("independently provisioned public-key trust root is required")
    if not expected_policy_config:
        return _refuse("expected grouping-policy configuration is required")
    if any(str(key).startswith("test-") for key in trusted_public_keys):
        return _refuse("synthetic test keys cannot authorize a real candidate")

    try:
        result = candidate_preflight_only(
            evidence,
            repo_root=repo_root,
            allowed_output_root=allowed_output_root,
            evidence_root=evidence_root,
            trusted_file_digests=trusted_file_digests,
            trusted_source_digests=trusted_source_digests,
            trusted_public_keys=trusted_public_keys,
            expected_policy_config=expected_policy_config,
            revoked_key_ids=revoked_key_ids,
        )
    except Exception as exc:  # the boundary must fail closed
        return _refuse(f"secure candidate preflight failed closed: {exc.__class__.__name__}")

    if result.get("decision") != "PREFLIGHT_PASS_STOPPED_BEFORE_TRAINING":
        return _refuse(result.get("reason", "secure candidate preflight refused"))
    return _refuse(
        "preflight completed, but the candidate-only orchestrator has no training or artifact stage",
        preflight=result,
        authorization_mode="candidate_preflight_only",
    )


def dry_run_config(config_path: str | Path) -> dict[str, Any]:
    """Inspect a candidate config without reading datasets or creating paths."""
    path = Path(config_path).resolve()
    try:
        path.relative_to(TASK33_ROOT)
    except ValueError:
        return _refuse("dry-run configuration must be inside the Task 33 directory")
    try:
        with path.open("r", encoding="utf-8") as handle:
            config = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        return _refuse(f"dry-run configuration is unreadable or malformed: {exc.__class__.__name__}")
    if not isinstance(config, Mapping):
        return _refuse("dry-run configuration must be a JSON object")
    blockers = [
        "production trust roots and authenticated approval are not provisioned",
        "dataset provenance/licensing is unresolved",
        "owner-approved grouping and partition evidence is unresolved",
        "complete dependency-lock evidence is unresolved",
        "real-data training is disabled in this candidate-only module",
    ]
    return _refuse("candidate remains blocked", mode="dry-run", blockers=blockers)


def main(argv: list[str] | None = None) -> int:
    """Provide a non-authorizing audit interface; no execute mode exists."""
    args = list(sys.argv[1:] if argv is None else argv)
    if args[:1] == ["--dry-run"] and len(args) == 2:
        result = dry_run_config(args[1])
    else:
        result = _refuse("only --dry-run <Task33 configuration> is supported; training is disabled")
    print(json.dumps(result, sort_keys=True))
    return 0 if result["decision"] == "REFUSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
