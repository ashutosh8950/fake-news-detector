# TruthScan Model-Release Prerequisites

Status: inference remains intentionally fail-closed. This plan records the shortest evidence-based route to a new, reviewable local Fake/Real inference bundle; it does not authorize training, artifact download, or release.

## Single most actionable next step

The owner should appoint a rights/provenance decision-maker and resolve the exact training-input decision:

1. recover an authenticated acquisition record and written rights evidence for the existing `data/Fake.csv` and `data/True.csv`, **or**
2. explicitly reject those files for release work and authorize a separately assessed replacement dataset.

The required evidence is not a filename or local hash. It must identify the upstream publisher and exact revision, acquisition date and method, source artifact digest, deterministic transformation to the two local CSV hashes, and permission covering training/evaluation and the intended downstream use. A qualified rights reviewer or authorized rights holder must confirm the relevant permissions; the project owner must record the scope decision.

This is the best next step because the current model bundle cannot be responsibly rebuilt or promoted without known, permitted inputs. It would unblock a controlled rebuild plan, not automatically authorize training or public deployment. If the existing dataset is retained, the exact local hashes to bind are recorded in `evaluation_results/new_release_candidate_2026-10-22/task27_dataset_provenance/TASK27_UNBLOCKING_CHECKLIST.md`. If a replacement is chosen, it requires a new identity and provenance record and must not be treated as historically equivalent.

## Prerequisite checklist

### Resolved or supported by current evidence

- **Fail-closed application behavior:** `app.py`, `routers/api.py`, and `predictor.py` leave the service available for diagnosis but report `503`/`not_ready` when the trusted bundle is unavailable. `/analyze` does not fabricate a prediction. This behavior is covered by `tests/test_application_e2e.py`, `tests/test_api.py`, and `tests/test_readiness_contract.py`.
- **Pre-deserialization byte checks:** `artifact_contract.py` verifies the required file set, sizes, and SHA-256 values from a manifest before `joblib.load` is reached. This is integrity checking against a supplied manifest, not independent authentication of the manifest or its key.
- **Current production bundle shape:** the source identifies five calibrated artifacts plus the vectorizer and calibration report. `MODEL_REPRODUCIBILITY_AND_RELEASE_PLAN.md` documents the expected bundle and compatibility checks.
- **Synthetic CI scope:** the exact-version `requirements-ci.lock` is used by `.github/workflows/ci.yml` for synthetic tests. Core tests pass in the existing environment, but this is not a clean-install proof.
- **No public-release authorization:** prior gate reports consistently leave real-data training, artifact distribution, and public hosting blocked. That fail-closed state is correct and must remain.

### Unresolved evidence

- **Dataset identity and rights:** `TASK27_DATASET_PROVENANCE_AND_LICENSE_REPORT.md` says the local files have consistency records, but no authenticated source-to-local mapping, acquisition receipt, source digest, license snapshot, or rights-holder permission was recovered. Local SHA-256 values alone do not establish origin or permission.
- **Underlying article rights:** the possible Hugging Face/Kaggle sources do not establish that the uploader could license all embedded news content for training, model distribution, public hosting, or raw-data redistribution.
- **Historical model authenticity:** `HISTORICAL_EVIDENCE_TRACE.md` and `HISTORICAL_RELEASE_RECOVERY_AUDIT.md` report no independently authenticated artifact manifest, signed release record, trusted publisher key, or byte-identity evidence for the historical pickles.
- **Release trust root:** `MODEL_REPRODUCIBILITY_AND_RELEASE_PLAN.md` requires an independently provisioned key or equivalent attestation, release identity binding, rotation/revocation process, and signature verification. The current same-host manifest/download path is not an independent trust root.
- **Dependency reproducibility:** `TASK55_HASH_PINNED_DEPENDENCY_REPORT.md` records 72 exact-version pins without hashes, no approved mirror or complete retained distributions, and no successful clean `--require-hashes` installation. `TASK56_SOURCE_AND_READINESS_REPORT.md` confirms public PyPI reachability is not package-source approval or reproducibility evidence.
- **Candidate-build environment:** the future build still needs a verified Linux/Python target lock, spaCy package/model version and checksum, source commit, container/OS identity, and build record. The current Windows environment is insufficient to establish the CI target environment.
- **Evaluation validity and leakage:** the historical `98.44%` figure is recorded in `evaluation_results/phase2_calibration_report.json` and the README, but it does not authenticate the model bytes or prove generalization. The newer group-aware v3 summary reports different selected-model metrics (for example, Decision Tree accuracy `0.9639` under one policy and `0.9738` under another) and documents independent partition checks. The reports also record mixed-label groups in one manifest. These results must not be silently substituted for the production five-model claim; the release candidate needs one owner-approved evaluation protocol, exact manifests, and reconciled metrics.
- **Source/report consistency:** `HISTORICAL_EVIDENCE_TRACE.md` and the reproducibility plan note that the checked-in calibration report says `production_switch: true` while the current generator writes `false`. The source revision and report origin must be reconciled before treating historical promotion metadata as evidence.

### Blocked pending owner approval or external information

- **Training on any release dataset:** blocked until the owner chooses the existing-dataset recovery path or authorizes a separately evaluated replacement, and rights evidence is reviewed.
- **Rebuilding calibrated artifacts:** blocked until the dataset identity/rights, exact source revision, approved grouping/partition manifests, and reproducible build environment are recorded.
- **Loading historical artifacts:** blocked until an independently authenticated release manifest/trust root and compatibility evidence are available. Do not bypass `artifact_contract.py`.
- **Public inference or artifact distribution:** additionally blocked until downstream-use permission, privacy/third-party-content review, deployment approval, monitoring/security evidence, and explicit release authorization are recorded.
- **Hash-pinned CI lock:** blocked until an approved package source or complete target-platform distribution set is provided. Hashes must come from the actual installable distributions, then be verified by a fresh installation, `pip check`, and the CI-equivalent suite.

## Safe dependency order to genuine local inference

1. **Owner decision:** choose existing-dataset recovery or an explicitly authorized replacement assessment; define whether the intended scope is internal academic use, public inference, commercial use, model distribution, and/or raw-data redistribution.
2. **Rights and provenance record:** authenticate the source revision, acquisition chain, transformation receipt, local digests, license/permission scope, and third-party-content restrictions. Keep the release dataset blocked if any item is missing.
3. **Technical data approval:** approve grouping policy, duplicate/leakage handling, exact outer/inner partition manifests, label semantics, and evaluation protocol for that exact dataset.
4. **Reproducible build environment:** obtain an approved Linux/Python target dependency source; create a hash-enforced lock from actual distributions; record spaCy model identity/checksum, source commit, container/OS identity, seeds, and build configuration.
5. **Controlled new build:** only after steps 1–4 are approved, run the single gated candidate-build path in `evaluation_results/new_release_candidate_2026-10-22/task33_gated_build/` into a new staging directory. Do not overwrite the current bundle. Generate a manifest containing release ID, source commit, dataset identities/digests, dependency-lock identity, configuration fingerprint, file sizes, and hashes.
6. **Independent trust and review:** sign or attest the manifest using a trust root provisioned through an owner-controlled channel separate from the artifact host. Verify key identity, scope, expiry/revocation policy, exact file set, and release identity before activation.
7. **Compatibility and release approval:** run artifact-contract checks and approved evaluation/regression checks, review limitations, then obtain explicit owner authorization for local activation. Public hosting requires a separate deployment and rights decision.

Until these steps are complete, the correct local behavior is the current one: the application may serve `/`, `/docs`, and health diagnostics, but `/analyze` must remain unavailable when trusted artifacts are not ready.

## Acceptance criteria for eventually enabling inference

- The exact dataset or approved replacement has an authenticated source/revision mapping, local digests, transformation receipt, and rights evidence covering the intended use.
- Owner-approved grouping and leakage-resistant partition manifests are bound to that dataset identity.
- The candidate build uses a reviewed source commit and a clean, hash-enforced target environment; `pip check` and the CI-equivalent suite pass from a fresh environment.
- The resulting bundle contains exactly the expected files, sizes, hashes, schema, and compatibility metadata in a signed/independently attested manifest.
- The trust root and release identity are independently provisioned and verified; same-host keys or unsigned tags are not accepted as the root of trust.
- Evaluation results are reproducible under the approved protocol, with the historical `98.44%` claim either reconciled or explicitly retired as non-release evidence.
- Explicit owner approval exists for the exact scope: local academic demonstration, model distribution, public inference, commercial use, and raw-data redistribution.
- Only after all gates pass may `predictor.load()` deserialize the bundle and `/health` report models ready.

## Files and evidence examined

- `README.md`
- `app.py`, `routers/api.py`, `predictor.py`, `artifact_contract.py`, `download_models.py`
- `.github/workflows/ci.yml`, `requirements-ci.lock`
- `evaluation_results/new_release_candidate_2026-10-22/task27_dataset_provenance/TASK27_DATASET_PROVENANCE_AND_LICENSE_REPORT.md`
- `evaluation_results/new_release_candidate_2026-10-22/task27_dataset_provenance/TASK27_UNBLOCKING_CHECKLIST.md`
- `evaluation_results/historical_evidence_trace_2026-10-21/HISTORICAL_EVIDENCE_TRACE.md`
- `evaluation_results/historical_release_recovery_2026-10-21/HISTORICAL_RELEASE_RECOVERY_AUDIT.md`
- `evaluation_results/trusted_provenance_audit_2026-10-21/TRUSTED_PROVENANCE_AUDIT.md`
- `evaluation_results/model_reproducibility_release_plan_2026-10-21/MODEL_REPRODUCIBILITY_AND_RELEASE_PLAN.md`
- `TASK54_DEPENDENCY_VALIDATION.md`, `TASK55_HASH_PINNED_DEPENDENCY_REPORT.md`, `TASK56_SOURCE_AND_READINESS_REPORT.md`
- `evaluation_results/phase2_calibration_report.json`
- `evaluation_results/group_aware_model_evaluation/v3/evaluation_summary.md`, `manifest_validation.json`, `preflight_validation.json`, and `source_provenance.json`
- `tests/test_application_e2e.py`, `tests/test_api.py`, `tests/test_readiness_contract.py`, `tests/test_artifact_contract.py`

No files other than this document were changed. No datasets, model artifacts, packages, or external resources were downloaded or loaded; no training, calibration, deployment, commit, or push was performed.

Git HEAD at inspection: `8c41ae005f4bee178a2b0104cb29049f00182081`. The pre-existing modified and untracked files were preserved.
