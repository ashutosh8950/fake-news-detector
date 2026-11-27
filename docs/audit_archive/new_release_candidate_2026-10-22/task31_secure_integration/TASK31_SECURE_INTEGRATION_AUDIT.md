# Task 31 — Secure Preflight Integration Audit

## Result

**PASS for the candidate-only integration boundary and tested legacy-bypass prevention.** The new `candidate_preflight_only` boundary rejects the legacy Task 28 schema, requires externally supplied digest/public-key roots, rejects caller authorization booleans and test keys, calls only `run_preflight_secure`, catches secure-preflight exceptions, and never authorizes or invokes training. A strict synthetic pass remains explicitly stopped before training.

Real-data execution remains disabled. No production trust root, real owner authorization, dataset license, complete authenticated dependency lock, or release approval exists.

## Initial and final repository state

- HEAD before and after: `8c41ae005f4bee178a2b0104cb29049f00182081`.
- Existing modified tracked files and untracked paths were preserved.
- Modified candidate-only implementation: `evaluation_results/new_release_candidate_2026-10-22/task28_runner_preflight/candidate_runner_preflight.py`.
- New Task 31 files are confined to `evaluation_results/new_release_candidate_2026-10-22/task31_secure_integration/`.
- No production file, model artifact, real dataset, existing manifest, or prior report was modified.

## Independently verified call graph

### Candidate preflight

- Legacy structural entry point: `task28_runner_preflight/candidate_runner_preflight.py:run_preflight`.
- Strict verifier: `task28_runner_preflight/candidate_runner_preflight.py:run_preflight_secure`.
- Strict integration boundary: `task31_secure_integration/secure_build_boundary.py:candidate_preflight_only` calls only `run_preflight_secure`.
- Lower-level build boundary: `secure_build_boundary.py:invoke_build` is an explicit fail-closed stub and contains no training call.
- No current real-data candidate runner was found that invokes either preflight function.

### Existing training/model paths inspected

- `train.py:train` directly fits and saves models under the production model path; it does not call candidate preflight.
- `phase2_calibration.py:main`/module execution fits calibration models and writes `models/calibrated/`; it does not call candidate preflight.
- `evaluation_results/group_aware_model_evaluation/v3/run_experiment.py` fits evaluation models and calibrators in an evaluation workflow; it does not call candidate preflight.
- `predictor.py:load_models` deserializes production artifacts; it is production inference code, not a candidate build path, and was not invoked.
- `download_models.py:download_models` downloads/stages production release artifacts under its own artifact contract; it does not call candidate preflight and was not invoked.
- `app.py` starts production inference and can trigger model loading; it was not invoked.

The source search found no alternate candidate build function that could be reached from the new Task 31 boundary. The existing direct training and production paths remain outside the candidate preflight system and are not authorized by this task; they must not be used for a new release.

## Integration protections implemented

`candidate_preflight_only` now enforces:

1. `task30_evidence_v1` is mandatory; legacy Task 28 evidence is refused.
2. Top-level caller-supplied `training_permitted`, `authenticated`, `approved`, and `allow_real_data_training` fields are refused.
3. Empty or missing trusted file digests, source digests, public keys, or expected policy configuration are refused.
4. Test-key identifiers are refused at the production boundary.
5. All calls go to `run_preflight_secure`; exceptions become refusal results.
6. A strict pass is still returned as `PREFLIGHT_PASS_STOPPED_BEFORE_TRAINING`, with `build_authorized=false`, `training_permitted=false`, and `artifacts_created=false`.
7. `invoke_build` fails closed and does not invoke a lower-level training function.

The strict Task 30 verifier itself recomputes evidence-file and source-byte hashes, validates manifest membership/group separation, binds certificates, verifies Ed25519 signatures against externally supplied keys, checks environment lock bytes, and remains preflight-only. The actual trust roots remain caller-provisioned and are absent for production.

## Adversarial integration testing

Command:

```text
python -m unittest discover -s evaluation_results/new_release_candidate_2026-10-22/task31_secure_integration -p "test_*.py" -q
```

Result: **21 passed, 0 failed**.

The suite covers all requested categories: strict synthetic pass without training, legacy success refusal, missing/exceptional secure preflight, injected booleans, missing roots, embedded/test keys, wrong dataset/policy/manifest/certificate bindings, changed signed approval, changed lock/environment, duplicate/overlapping/incomplete membership, path escape, lower-level build bypass, missing licensing, masked gate failure, and zero artifact creation.

Regression commands:

```text
python -m unittest discover -s evaluation_results/new_release_candidate_2026-10-22/task30_gate_security -p "test_*.py" -q
```

Result: **13 passed, 0 failed**.

```text
python -m unittest discover -s evaluation_results/new_release_candidate_2026-10-22/task29_gate_integration_audit -p "test_*.py" -q
```

Result: **9 passed, 0 failed**.

```text
python -m unittest discover -s evaluation_results/new_release_candidate_2026-10-22/task28_runner_preflight -p "test_*.py" -q
```

Result: **17 passed, 0 failed**.

```text
python -m pytest evaluation_results/new_release_candidate_2026-10-22/harness/tests/test_isolated_build_harness.py -q
```

Result: **17 passed, 1 skipped**. The existing privilege-dependent native symlink test remains skipped; no privilege bypass was attempted.

## Remaining risks and evidence blockers

- No organization-controlled production public key or trust-store provisioning exists. Test keys are not production trust roots.
- The approval signature verifies cryptographic binding only; it does not establish legal issuer authority.
- Existing Task 26/27 records are unsigned/unapproved and cannot authorize a real build.
- Existing production manifests do not provide the strict Task 30 membership schema and were not regenerated.
- The existing environment snapshot is not a complete authenticated dependency lock.
- Dataset provenance/licensing remains unresolved.
- Native symlink and filesystem race behavior is not fully proven in the current privilege-limited environment.
- Direct legacy production training and calibration scripts remain callable independently of this candidate boundary. They are not part of the authorized new-release path; a future real-data runner must be designed as a single gated path and must not call them directly.

## Safety confirmation

No network access, package installation, dataset-content processing, model loading, training, evaluation, deployment, signing, or release artifact creation occurred. Synthetic test keys and evidence were used only inside temporary test fixtures. Real-data training remains disabled.
