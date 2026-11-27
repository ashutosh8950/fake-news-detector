# Task 22 — Isolated Group-Aware Build Harness Report

**Date:** 2026-10-22  
**Result:** **Harness safely implemented and synthetic-tested**  
**Candidate status:** No model candidate was trained; not production-ready.

## Summary

A separately testable harness was added under the new candidate namespace. It does not import the production predictor, preprocessing module, training scripts, calibration scripts, joblib, pickle, spaCy, or model artifacts.

The harness now provides:

- explicit output-root validation;
- rejection of production model paths and shared/previous evaluation paths;
- refusal to overwrite non-empty candidate directories;
- planned output-path recording before any future training;
- deterministic group-aware four-way splitting;
- group-overlap, row-count, group-count, class-count, and mixed-label reporting;
- validation of labels, group IDs, non-empty partitions, and target fractions;
- explicit configuration fields for dataset, license/provenance, source, preprocessing, grouping, estimator, vectorizer, calibration, environment, and candidate identity;
- fail-closed refusal of unresolved real-data training; and
- a refusal-default JSON configuration template.

No real-data training, calibration, model loading, artifact export, manifest creation, or production change occurred.

## Files created

- `evaluation_results/new_release_candidate_2026-10-22/harness/isolated_build_harness.py`
- `evaluation_results/new_release_candidate_2026-10-22/harness/tests/test_isolated_build_harness.py`
- `evaluation_results/new_release_candidate_2026-10-22/harness/candidate_config.template.json`
- `evaluation_results/new_release_candidate_2026-10-22/harness/TASK22_HARNESS_REPORT.md`

No existing file was modified by this task.

## Protected paths and isolation checks

The harness requires an explicit output root and an allowed new namespace. It rejects roots outside that namespace, roots under `models`, shared repository evaluation roots, and non-empty existing directories. The default namespace is:

`evaluation_results/new_release_candidate_2026-10-22/harness/`

The protected production-like paths include:

- `models/`
- `models/calibrated/`
- existing shared `evaluation_results/` reports and directories

Future candidate output is expected under a new child directory of the harness namespace. The harness records these paths before future training:

- `training_plan.json`
- `split_manifest.json`
- `validation_report.json`
- `artifacts/`

The harness does not create model artifacts itself. A future training implementation must consume the recorded plan and retain the same path checks before any export.

## Group-aware split design

`build_group_split(features, labels, group_ids, ...)` accepts equal-length feature, label, and stable-group sequences. It validates:

- non-empty, non-blank string group IDs;
- integer labels restricted to 0 and 1;
- four non-empty partitions: `train`, `selection`, `calibration`, and `test`;
- positive target fractions summing to 1;
- required class coverage by partition, when enabled; and
- no group overlap between partitions.

Groups are placed by a deterministic seed-based ordering and a greedy balance heuristic. The report records row counts, group counts, class counts, group IDs, mixed-label groups, pairwise group overlaps, seed, target fractions, and algorithm identifier. The implementation explicitly states that the heuristic is not globally optimal.

The harness does not claim that this synthetic splitter is the final production grouping policy. A later release task must approve and record the actual grouping policy, version, and dataset-specific partition manifest before real-data training.

## Configuration and training gates

`validate_build_configuration()` requires explicit non-empty values for dataset identity/version/schema, label mapping, licensing evidence, provenance evidence, source revision, preprocessing revision, grouping policy, estimator/vectorizer/calibration configuration, environment record, and candidate ID.

For real data, licensing and provenance evidence must be mappings with `status: reviewed`, a source, and a date. A manually entered approval flag is not accepted as evidence. Real-data training also requires explicit `allow_real_data_training: true`, but the harness still raises a deliberate “not implemented in the harness task” gate so this task cannot train real data.

The template defaults to:

- `allow_real_data_training: false`;
- unresolved licensing and provenance status; and
- required values marked as placeholders.

This does not resolve the previously reported dataset origin, legal, historical configuration, dependency-lock, or release-authentication blockers.

## Synthetic test results

Command executed:

```text
.venv\Scripts\python.exe -m pytest evaluation_results/new_release_candidate_2026-10-22/harness/tests/test_isolated_build_harness.py -q
```

Result:

```text
10 passed in 0.22s
```

The tests cover:

1. Same-group rows remain in one partition.
2. Invalid and missing group IDs fail.
3. Identical inputs and seed produce identical assignments.
4. Invalid labels and insufficient groups fail safely.
5. Production and shared evaluation paths are rejected.
6. Failed validation does not create candidate artifacts or overwrite a sentinel.
7. Real-data training refuses unresolved provenance without writing artifacts.
8. Tests use temporary namespaces and do not write existing production/evaluation paths.
9. Train, selection, calibration, and test groups are mutually disjoint.
10. Failure messages identify the unmet gate without including secret data.
11. Planned output paths are recorded before future training.
12. Invalid split target fractions fail safely.

The existing repository-wide test suites were not run because this task specifically required synthetic-only validation and broad application tests may exercise production loading paths. No test imported or deserialized a production artifact.

## Environment and reproducibility

The existing `.venv` was inspected without installation or modification:

- Python 3.11.9
- spaCy 3.8.16
- `en_core_web_sm` installed and discoverable
- scikit-learn, pandas, NumPy, and joblib import specifications present
- pytest available and used for the synthetic suite

The environment is not claimed to be locked or fully reproducible. `requirements.txt` remains incomplete as a lock record because most dependencies are lower-bounded or unpinned. A later task should create a reviewed lock from the approved environment, capture the Python and spaCy model sources/versions, verify it in a clean environment, and retain the resulting hashes. No lock was generated here and no package was installed.

## Remaining blockers

- Dataset origin, license, acquisition record, and independent provenance remain unresolved.
- The real-data grouping policy and production partition manifest remain unapproved.
- Existing training/calibration scripts still write to production/shared paths; they were not changed in this task.
- Historical `production_switch` and historical ensemble differences remain unresolved and must not be silently reused.
- A complete dependency lock and authenticated environment record remain absent.
- No signed manifest, trust root, or release authentication process exists for the new candidate yet.

## Recommended next task

After the project owner supplies a documented dataset/license decision and approves the new model configuration, implement a reviewed candidate-only runner that consumes a fixed group manifest and writes only below a unique harness candidate directory. Before running it on real data, add a dry-run path-plan check, verify the complete environment record, and obtain explicit release-validation criteria. Only after candidate validation should an organization-controlled signing and release-authentication process be designed.

The new release must remain distinct from the historical bundle. It must not be described as authenticating, replacing, reproducing, or outperforming the historical production artifacts without trusted reference evidence.

## Git status and audit integrity

Before changes:

- HEAD: `8c41ae005f4bee178a2b0104cb29049f00182081`
- Branch: `main`
- Pre-existing modified files: `README.md`, `app.py`, `download_models.py`, `frontend/style.css`, `predictor.py`, `routers/api.py`.
- Pre-existing untracked files/directories included earlier reports, tests, and project documentation.

After changes:

- HEAD remains `8c41ae005f4bee178a2b0104cb29049f00182081`.
- All pre-existing modifications and untracked paths remain present.
- The only new paths from this task are the four files listed in the “Files created” section under `evaluation_results/new_release_candidate_2026-10-22/harness/`.

No production code, application behavior, model artifact, prior audit report, Git tag, or Git history was modified.

## Safety confirmation

- No real dataset was used for training or calibration.
- No production pickle/joblib artifact was loaded or deserialized.
- No model artifact was downloaded, written, deleted, overwritten, or replaced.
- No existing evaluation directory or report was modified.
- No package or language model was installed or downloaded.
- No signing key was generated or used.
- No commit, push, deployment, tag, or history change occurred.

**Final status:** isolated harness implemented and synthetic-tested; real candidate creation remains blocked pending the documented prerequisites above.
