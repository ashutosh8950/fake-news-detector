# TruthScan New Release Candidate Report

**Audit/build date:** 2026-10-22  
**Release route:** New, distinctly authorized release; not historical recovery  
**Status:** **STOPPED AT PRE-BUILD GATE**

## Executive result

No new release candidate was created and no training was started. The pre-build gate did not pass.

The existing Python 3.11 virtual environment contains the required core packages and `en_core_web_sm`, but this does not overcome the mandatory blockers:

1. Dataset origin and licensing remain unresolved from independently verifiable evidence.
2. The existing calibration script writes directly to `models/calibrated/` and `evaluation_results/`, so it cannot be used for an isolated candidate namespace without a reviewed code/configuration change.
3. The existing Phase 1/Phase 2 procedure is stratified, not group-aware. The Phase 2 script reconstructs a fixed 20,700/3,653 split and uses an inner random stratified split; it does not prove duplicate-group separation between fitting, calibration, and final evaluation.
4. The existing scripts and reports contain unresolved historical configuration context, including the `production_switch` discrepancy and the difference between the historical six-model Phase 1 workflow and the five-model calibrated workflow.

Because a mandatory gate failed, training, candidate artifact generation, candidate metrics, manifest generation, and candidate tests were not performed.

## Pre-build gate results

| Gate | Result | Evidence |
|---|---|---|
| Existing changes preserved | PASS | HEAD and status were recorded before inspection; no destructive Git command was used. |
| Production artifacts protected | PASS | No pickle/joblib/model file was opened, deserialized, overwritten, or downloaded. Artifact directory was inspected by names only. |
| Local dataset files present | PASS | `data/Fake.csv` and `data/True.csv` exist; headers are `title,text,subject,date`. Current line counts are 17,717 and 18,829 including headers. |
| File integrity record | PASS as integrity only | SHA-256 values were calculated locally: `Fake.csv` = `672ab39a75ac75fef9ecbb1a84e2936e064b44a32197a4801d9d0fb63ca9d57e`; `True.csv` = `c3105d9266fd2ad484aad43b13801930434ffcd68894cc975128e52433a0c6ad`. These do not prove authenticity or licensing. |
| Labels and schema | PARTIAL | The scripts assign label 0 to all rows from `Fake.csv` and 1 to all rows from `True.csv`; headers and sample rows were readable. A complete source-authenticated label validation was not available. |
| Dataset origin/licensing | FAIL / BLOCKED | Prior audits and public evidence identify possible Hugging Face/Kaggle sources, but do not authenticate the local bytes, acquisition record, or license terms for this copy. The unresolved licensing/origin issue is a mandatory stop condition. |
| Python environment | PASS for available environment | `.venv` reports Python 3.11.9, spaCy 3.8.16, scikit-learn, pandas, NumPy, joblib, and `en_core_web_sm` package availability. |
| Dependency reproducibility | PARTIAL / BLOCKED for release | `requirements.txt` is not a complete lockfile; most dependencies use lower bounds. No authenticated environment image or complete lock record is present. |
| Preprocessing availability | PASS for inspection only | `preprocessor.py` uses spaCy `en_core_web_sm`, disables parser/NER, triple-weights title text, removes stopwords, and lemmatizes. It loads the language model at module import. |
| Candidate artifact isolation | FAIL | `phase2_calibration.py:38`, `:195`, `:221`, and `:260` write to `models/calibrated/` and the shared `evaluation_results/` directory. Running it unchanged could modify production/shared outputs. |
| Leakage-safe partitions | FAIL | `evaluate_pipeline.py:297-302` uses stratified `train_test_split`; `phase2_calibration.py:108-114` uses another stratified split. Neither is wired to the duplicate-aware manifest for all fit/calibration/evaluation boundaries. |
| Configuration unambiguous | FAIL / BLOCKED | The existing workflow has the documented `production_switch` conflict and historical six-model versus five-model differences. A new release configuration must be explicitly approved and recorded rather than inferred from historical files. |

## Source and configuration inspection

### Training and calibration

`train.py` defines uncalibrated Logistic Regression, Decision Tree, Gradient Boosting, Random Forest, Multinomial Naive Bayes, and Linear SVC models with seed 42 and writes to `settings.models_dir` (`train.py:32-42`, `:129-158`). This workflow is not the calibrated five-model application workflow.

`phase2_calibration.py` defines five models—Logistic Regression, Decision Tree, Gradient Boosting, Naive Bayes, and Linear SVC—with seed 42 (`:29`, `:40-56`). It uses TF-IDF word unigrams/bigrams, `max_features=150000`, `sublinear_tf=True`, `min_df=2`, and `max_df=0.95` (`:59-70`). It chooses sigmoid versus isotonic calibration using a 20% inner stratified split and Brier score, with five-fold calibration CV (`:105-147`).

The script reconstructs the prior held-out file and requires exactly 20,700 training rows and 3,653 held-out rows (`:73-102`). It then fits on the reconstructed training data and evaluates on the held-out data (`:165-185`, `:209-233`). This is not a new group-aware three-way build protocol and writes directly into shared/prod-like locations (`:38`, `:194-195`, `:221-222`, `:260-262`).

### Preprocessing

`preprocessor.py:15-16` loads `en_core_web_sm` at module import. `preprocess()` combines title and text with the title repeated three times (`:42-50`), then applies the cleaning and spaCy lemmatization pipeline (`:18-40`). This is a material input to any candidate and must be captured by an isolated build record.

### Historical configuration context

`phase2_calibration.py:204` writes `production_switch: False`, while the tracked Phase 2 report was previously found to record `true`. The current inference path does not consume this field according to the prior history trace. Commit `353c20f` removed Random Forest from the tracked report/configuration context without updating the generator at that point. This unresolved historical discrepancy does not prevent an owner-approved new configuration in principle, but it prevents silently treating the old workflow as the complete new-release specification.

## Dataset and provenance limitations

The local files are ignored by Git and were not downloaded or replaced during this task. Their local hashes match previously recorded local provenance values, which is consistency evidence only. The public source and licensing questions remain unresolved:

- No independently authenticated acquisition record for these exact CSV bytes was available.
- No complete publisher/version/checksum mapping to these local files was available.
- The local training scripts identify possible public sources but do not establish historical origin.
- The project owner has not supplied an authenticated dataset release record or license decision for the candidate build.

The candidate route therefore requires either an owner-approved, legally reviewed dataset input record or a verified replacement dataset and license record before any training begins.

## Environment findings

The existing `.venv` was inspected without installation or modification:

- Python: 3.11.9
- spaCy: 3.8.16
- `en_core_web_sm`: installed and discoverable; package path under the existing `.venv`
- scikit-learn, pandas, NumPy, and joblib: import specifications present
- `requirements.txt`: scikit-learn is pinned to 1.9.0, but most other dependencies are lower-bounded or unpinned
- `pyvenv.cfg`: environment is Python 3.11.9 and excludes system site packages

This establishes local availability, not an authenticated or reproducible release environment. No packages were installed and no language model was downloaded.

## Candidate configuration not executed

No candidate configuration was selected or trained. The following decisions remain required before a later isolated implementation task:

1. Approve the exact new model set and whether calibration is sigmoid or isotonic-selected under a new protocol.
2. Approve a group-aware split algorithm and fixed partition manifest with proper-fit, model-selection, calibration, and final-test partitions.
3. Establish dataset identity, legal use, acquisition record, and an independently retained dataset fingerprint.
4. Create or review code that writes exclusively under a new candidate namespace and never uses `models/calibrated/` or shared historical reports.
5. Record a complete dependency/environment specification, including the spaCy model version and source.
6. Define validation metrics, probability/class-order checks, and acceptance thresholds before inspecting candidate results.

The existing five-model configuration is recorded as a possible starting point only; it is not declared approved, historically equivalent, or production-ready.

## Tests

No artifact-contract, readiness, API, preprocessing, or duplicate-aware-manifest test suite was run in this task. The mandatory pre-build gate failed, and running broad tests could import application paths or touch shared artifacts without establishing candidate isolation. No candidate artifacts or validation results exist.

## Artifact inventory and manifest

No new candidate artifact inventory exists. No candidate manifest was generated. Existing names under `models/calibrated/` were listed only to confirm that the production-like directory was not used; their contents were not opened. No locally calculated hash from the existing production bundle is treated as a candidate or trusted reference.

## Required follow-up

The smallest legitimate next implementation task is to prepare and review an isolated build harness—without running it—after the owner supplies the dataset/license decision and approves the new configuration. That harness must:

- consume a fixed, recorded group-aware partition manifest;
- write only under `evaluation_results/new_release_candidate_<id>/`;
- separate fitting, model selection, calibration, and final evaluation;
- record environment, source, dataset, and configuration inputs;
- fail before touching production paths; and
- produce a manifest explicitly labeled as an unsigned integrity record until organization-controlled authentication is established.

After that review, a separate authorized task may run the build and validation. A successful new build must not be described as authenticating or reproducing the historical bundle.

## Exact commands and environment actions executed

Read-only or non-mutating actions executed:

```text
git rev-parse HEAD
git status --short
Get-ChildItem -Force
Get-ChildItem evaluation_results -Directory
rg -n ... training, calibration, preprocessing, split, artifact, and provenance references
Get-Content requirements.txt
Get-Content .venv\pyvenv.cfg
Get-ChildItem models\calibrated -Force | Select-Object Name
.venv\Scripts\python.exe -c "inspect Python/package/model availability"
Get-FileHash data\Fake.csv -Algorithm SHA256
Get-FileHash data\True.csv -Algorithm SHA256
Get-Content data\Fake.csv -TotalCount 2
Get-Content data\True.csv -TotalCount 2
Get-Content phase2_calibration.py
Get-Content evaluate_pipeline.py
Get-Content preprocessor.py
Get-Content config.py
```

No training command, model export command, download command, dependency installation, or test command was executed.

## Git status and integrity confirmation

Before inspection:

- HEAD: `8c41ae005f4bee178a2b0104cb29049f00182081`
- Branch: `main`
- Pre-existing modified files: `README.md`, `app.py`, `download_models.py`, `frontend/style.css`, `predictor.py`, `routers/api.py`.
- Pre-existing untracked files/directories included prior audit reports and project changes.

After the audit, HEAD remained `8c41ae005f4bee178a2b0104cb29049f00182081`, and all pre-existing modifications/untracked paths remained. The only path created by this task is:

`evaluation_results/new_release_candidate_2026-10-22/NEW_RELEASE_CANDIDATE_REPORT.md`

No application code, training code, calibration code, deployment code, historical audit report, production artifact, or Git metadata was modified.

## Final safety confirmation

- **Training status:** not started; stopped at pre-build gate.
- **Candidate status:** no candidate created.
- **Historical production artifacts:** not loaded, deserialized, downloaded, overwritten, replaced, or modified.
- **Production behavior:** not changed.
- **Historical provenance:** not recovered and not claimed.
- **Release authentication:** not created; no signing keys used.
- **Deployment:** not performed or approved.
