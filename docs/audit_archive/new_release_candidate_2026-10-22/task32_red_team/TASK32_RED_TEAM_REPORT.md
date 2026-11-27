# Task 32 — Independent Red-Team Verification of the Secure Build Boundary

## Verdict

**CONDITIONAL PASS for the inspected candidate-only boundary; FAIL for repository-wide training-path integration.** The Task 31 boundary and strict Task 30 verifier behave fail-closed in the tested synthetic scope. Production-mode strict verification now refuses because no independently provisioned production trust root exists. However, direct `train.py:train` and `phase2_calibration.py:main` remain callable source-level model-building/export paths that do not call secure preflight. They were not invoked and were not modified. Therefore the repository cannot claim that every training path is gated.

## Baseline and scope

Initial and final HEAD: `8c41ae005f4bee178a2b0104cb29049f00182081`. Existing user modifications and untracked files were preserved. The only implementation change was candidate-only: `evaluation_results/new_release_candidate_2026-10-22/task28_runner_preflight/candidate_runner_preflight.py` now refuses all non-test strict calls when production trust-root provisioning is absent. New files are confined to this Task 32 directory.

No network, package installation, real dataset processing, model loading, training, evaluation, release artifact creation, deployment, or signing occurred.

## Verified call graph

The candidate path is:

`candidate_preflight_only` → `run_preflight_secure` → strict evidence/file/signature/partition/environment checks → stopped preflight result.

The boundary rejects legacy `task28_evidence_v1`, rejects caller authorization booleans, rejects synthetic test-key identifiers, requires non-empty external root mappings, catches secure exceptions, and never calls a training function. The explicit `invoke_build` function is a fail-closed stub.

The alternate repository paths are separate:

- `train.py:train` performs estimator fitting and `joblib.dump` writes.
- `phase2_calibration.py:main` performs calibration and writes calibrated artifacts.
- `download_models.py:download_models` stages production artifacts.
- `predictor.py:load_models` deserializes production artifacts.

Source inspection found no call from the first two training/export functions to `run_preflight_secure`, `candidate_preflight_only`, or the isolated harness. They were not executed. This is a confirmed source-level alternate path, not a runtime training test.

## Reproduced and tested findings

1. **Production trust-root bypass risk — fixed fail-closed.** Before the Task 32 change, `run_preflight_secure(..., test_only=False)` had no independent production trust-root provisioning check; the boundary only rejected key IDs beginning with `test-`. The strict production path now refuses unless a production trust root is configured. The red-team regression uses a renamed synthetic key and confirms refusal.
2. **Legacy preflight — contained at the candidate boundary.** The legacy function remains available for earlier synthetic compatibility, but its result now explicitly contains `build_authorized=false` and `authorization_mode=legacy_non_authorizing`; `candidate_preflight_only` rejects the legacy schema. Direct callers can still invoke the legacy function, so it must never be used as a build authorizer.
3. **Direct training/export bypass — confirmed source-level, not fixed.** `train.py:train` and `phase2_calibration.py:main` can be called without secure preflight and write model artifacts. Modifying those production paths is outside this task’s permitted scope. This remains a high-severity integration blocker for any real-data runner design.

Other red-team cases refused as expected: fabricated result objects, stale release IDs, changed signed approval payloads, changed dependency locks, mismatched environments, wrong dataset/policy/manifest/certificate bindings, missing roots, test/embedded keys, missing licensing, path escape, and lower-level build invocation.

## Tests

Task 32 command:

```text
python -m unittest discover -s evaluation_results/new_release_candidate_2026-10-22/task32_red_team -p "test_*.py" -q
```

Result: **13 passed, 0 failed**. The tests exercise actual strict validation and source-level call-path inspection; no model or dataset contents are loaded.

Task 31:

```text
python -m unittest discover -s evaluation_results/new_release_candidate_2026-10-22/task31_secure_integration -p "test_*.py" -q
```

Result: **21 passed, 0 failed**.

Task 30:

```text
python -m unittest discover -s evaluation_results/new_release_candidate_2026-10-22/task30_gate_security -p "test_*.py" -q
```

Result: **13 passed, 0 failed**.

Task 29:

```text
python -m unittest discover -s evaluation_results/new_release_candidate_2026-10-22/task29_gate_integration_audit -p "test_*.py" -q
```

Result: **9 passed, 0 failed**.

Task 28:

```text
python -m unittest discover -s evaluation_results/new_release_candidate_2026-10-22/task28_runner_preflight -p "test_*.py" -q
```

Result: **17 passed, 0 failed**.

Existing harness:

```text
python -m pytest evaluation_results/new_release_candidate_2026-10-22/harness/tests/test_isolated_build_harness.py -q
```

Result: **17 passed, 1 skipped**. The skip is the existing privilege-dependent native symlink case.

## Limitations and next action

The strict path’s cryptographic verification is real Ed25519 verification over canonical payload bytes, but a production trust root is intentionally absent. Signature validity does not establish issuer legal authority. The current tests use deterministic synthetic keys only and do not prove production key custody, revocation infrastructure, or deployment authentication. Filesystem race behavior is not eliminated by path resolution alone.

The next task should design a single candidate build entry point that invokes `candidate_preflight_only`/`run_preflight_secure` before any training or export and removes direct use of `train.py`/`phase2_calibration.py` for candidate builds, without changing production behavior until separately approved. That work must still wait for dataset/licensing evidence, owner grouping/partition approval, authenticated dependency evidence, and organization-controlled release trust roots.
