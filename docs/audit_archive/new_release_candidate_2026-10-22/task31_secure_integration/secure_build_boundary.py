"""Candidate-only integration boundary for strict preflight.

This module is intentionally not a training runner. It rejects the legacy
Task 28 evidence schema, requires externally provisioned trust roots, calls
only ``run_preflight_secure``, and keeps build authorization disabled even
after a synthetic strict preflight pass.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping

import sys

TASK28_ROOT = Path(__file__).parents[1] / "task28_runner_preflight"
if str(TASK28_ROOT) not in sys.path:
    sys.path.insert(0, str(TASK28_ROOT))
from candidate_runner_preflight import PreflightError, run_preflight_secure  # noqa: E402


FORBIDDEN_AUTH_FIELDS = frozenset({"training_permitted", "authenticated", "approved", "allow_real_data_training"})


def candidate_preflight_only(
    evidence: Mapping[str, Any],
    *,
    repo_root: os.PathLike[str] | str,
    allowed_output_root: os.PathLike[str] | str,
    evidence_root: os.PathLike[str] | str,
    trusted_file_digests: Mapping[str, str] | None,
    trusted_source_digests: Mapping[str, str] | None,
    trusted_public_keys: Mapping[str, bytes] | None,
    expected_policy_config: Mapping[str, Any] | None,
    revoked_key_ids: set[str] | None = None,
) -> dict[str, Any]:
    """Run strict preflight and return a non-authorizing result only."""

    refusal = {"decision": "REFUSED", "training_permitted": False, "build_authorized": False, "artifacts_created": False}
    if not isinstance(evidence, Mapping):
        refusal["reason"] = "evidence must be a mapping"
        return refusal
    if evidence.get("schema_version") != "task30_evidence_v1":
        refusal["reason"] = "legacy or unknown evidence schema cannot authorize a build"
        return refusal
    if any(field in evidence for field in FORBIDDEN_AUTH_FIELDS):
        refusal["reason"] = "caller-supplied authorization booleans are forbidden"
        return refusal
    if not trusted_file_digests or not trusted_source_digests or not trusted_public_keys or not expected_policy_config:
        refusal["reason"] = "independent trust roots and expected policy configuration are required"
        return refusal
    if any(str(key).startswith("test-") for key in trusted_public_keys):
        refusal["reason"] = "synthetic test keys cannot be used as production trust roots"
        return refusal
    try:
        result = run_preflight_secure(
            evidence,
            repo_root=repo_root,
            allowed_output_root=allowed_output_root,
            evidence_root=evidence_root,
            trusted_file_digests=trusted_file_digests,
            trusted_source_digests=trusted_source_digests,
            trusted_public_keys=trusted_public_keys,
            expected_policy_config=expected_policy_config,
            revoked_key_ids=revoked_key_ids,
            test_only=False,
        )
    except Exception as exc:  # fail closed at the integration boundary
        refusal["reason"] = f"secure preflight exception: {exc}"
        return refusal
    if result.get("decision") != "PREFLIGHT_PASS_STOPPED_BEFORE_TRAINING":
        return {**refusal, "reason": result.get("reason", "secure preflight refused")}
    return {
        **result,
        "build_authorized": False,
        "training_permitted": False,
        "artifacts_created": False,
        "decision": "PREFLIGHT_PASS_STOPPED_BEFORE_TRAINING",
        "reason": "Strict preflight passed, but this candidate-only boundary has no build authorization or training stage.",
    }


def invoke_build(*args: Any, **kwargs: Any) -> None:
    """Explicit fail-closed stub; no build function exists in this task."""
    raise PreflightError("real-data build execution is not implemented or authorized")
