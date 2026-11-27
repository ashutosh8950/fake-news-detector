# TruthScan Historical Evidence Trace

Date: 2026-10-21 (Asia/Calcutta)

## Executive verdict

**Task 17 blockers remain.** Existing Git history resolves part of the production_switch chronology but not its intended semantics or the authenticity of the model bundle.

The strongest historical evidence is:

- Commit 0ddbd3498e3c06a791efb34a3f37c9181eb6a08b introduced phase2_calibration.py and the Phase 2 report together, with both the generator and report using false.
- Commit 353c20f241d73f7e875508b1eb22eafc6943f9bb later changed only the tracked report value from false to true while removing Random Forest from the report and predictor. It did not change the calibration generator.
- Commit efb475ef5460cb720006fc8abc1dee58a041d165 subsequently removed Random Forest from the generator, but left production_switch false in the generator.
- The current predictor does not read production_switch; model membership and ensemble behavior are controlled by predictor.py.

This establishes source/report drift and a likely release-promotion edit, but not the project owner’s intended meaning. It does not resolve the configuration decision, dataset-origin, dependency-lock, trusted-reference, or release-authenticity blockers. No production artifact was loaded, rebuilt, downloaded, modified, or retrained.

## Current Git state

- HEAD verified at audit start: 8c41ae005f4bee178a2b0104cb29049f00182081.
- Branch: main.
- Existing modifications and untracked files were preserved.
- Existing audit directories and reports were not modified.

Working-tree entries present before this audit included modified README.md, app.py, download_models.py, frontend/style.css, predictor.py, and routers/api.py; untracked project documentation, artifact_contract.py, duplicate_aware_manifest.py, prior evaluation directories, prior audit reports, and tests.

## Phase A — production_switch history

### Current working tree

- evaluation_results/phase2_calibration_report.json:8 records "production_switch": true.
- The parsed type is JSON boolean, not a string.
- phase2_calibration.py:204 writes "production_switch": False, which serializes to JSON false.
- predictor.py:30-36 defines the active keys as lr, dt, gbc, nb, svc.
- predictor.py:64-106 loads the report and extracts model metadata, but has no read of production_switch.
- predictor.py:126-150 computes per-model probabilities and averages the five class-1 probabilities. The field does not affect prediction.

### Tracked occurrence inventory

Read-only git grep across all reachable commits found the field only in the Phase 2 report and generator:

- 8c41ae005f4bee178a2b0104cb29049f00182081: evaluation_results/phase2_calibration_report.json:8 is true; phase2_calibration.py:204 is False.
- 08f6c3589e72ae3d2c67cdc237c7343f2b537b24: same values.
- 14f35b271ca5a83feca845b213abff98ac2fcf7d: same values.
- efb475ef5460cb720006fc8abc1dee58a041d165: same values.
- cf1c859d5dfa73b8262a2f1c92c85d0a0cfa7ff: report true; generator false at line 208 in that revision.
- 353c20f241d73f7e875508b1eb22eafc6943f9bb: report true; generator false at line 208.
- 2c9974f6e2732398364786d70e0669239aca1941: report false; generator false at line 208.
- 01e57f8a4fb8047a2ab55602d292a53df28b9657: report false; generator false at line 208.
- 0ddbd3498e3c06a791efb34a3f37c9181eb6a08b: report false; generator false at line 208.

No other tracked source or configuration occurrence was found. No historical code was found that branches on the field to enable calibration, choose models, or control export.

### Commit chronology and evidence

#### 0ddbd3498e3c06a791efb34a3f37c9181eb6a08b

Date: 2026-09-19 00:57:57 +0530.

Subject: Phase 1 & 2: leakage-free evaluation, calibrated ensemble, production swap to predictor.py.

This commit added phase2_calibration.py and evaluation_results/phase2_calibration_report.json together. The new report contained production_switch false, and the generator contained production_switch False. This is the only tracked commit where the initial report and generator agree.

The same commit added the calibrated five/six-model production workflow and predictor changes. At that point the report still contained Random Forest; the later five-model production state came from a later commit.

#### 353c20f241d73f7e875508b1eb22eafc6943f9bb

Date: 2026-09-20 17:20:59 +0530.

Subject: Drop Random Forest from ensemble: fixes Render OOM crash, improves accuracy to 98.44% and Brier score.

The commit diff changed evaluation_results/phase2_calibration_report.json:8 from false to true, removed the rfc report entry, changed the ensemble name from six-model to five-model, and changed the reported ensemble metrics. It also changed predictor.py to remove Random Forest from the active model set.

The commit did not modify phase2_calibration.py. At that revision, its generator still wrote production_switch False. Therefore the report value was not produced by the checked-in generator in the same commit diff, or at minimum Git provides no evidence that it was regenerated from that generator. The safe conclusion is report/generator drift introduced during the production promotion change; the intent behind true is not recorded.

#### efb475ef5460cb720006fc8abc1dee58a041d165

Date: 2026-09-20 18:51:03 +0530.

Subject: Fix footer wording accuracy and remove Random Forest from phase2_calibration.py to prevent regression.

The commit removed Random Forest from phase2_calibration.py build_models and MODEL_NAMES and changed the generated ensemble wording to five-model. It did not change the production_switch value, which remained False in the generator. The tracked report remained true.

#### Subsequent commits

The later commits 14f35b271ca5a83feca845b213abff98ac2fcf7d, 08f6c3589e72ae3d2c67cdc237c7343f2b537b24, and current HEAD preserve the report true/generator false mismatch. No commit message, source branch, or tracked release note defines the field.

### Historical conclusion

The field does not have an evidenced runtime meaning. The chronology is consistent with a manually or separately generated report edit during the Random Forest removal/release promotion, but Git does not prove whether it was manually authored, copied from a separate run, or written by an unavailable script revision. The owner must identify the source of the report and define whether the field is historical metadata, a promotion approval marker, or obsolete.

## Phase B — Dependency and environment evidence

### Files found

- requirements.txt
- Dockerfile
- render.yaml
- .github/workflows/ci.yml
- evaluation_results/group_aware_model_evaluation/v3/environment_versions.json
- No pyproject.toml, poetry.lock, Pipfile.lock, Conda/environment YAML, constraints file, or resolved requirements lock was found.

### Evidence

- requirements.txt pins scikit-learn==1.9.0 but leaves FastAPI, pandas, NumPy, spaCy, joblib, and other dependencies as lower bounds or unpinned.
- Dockerfile and CI install requirements.txt, then run python -m spacy download en_core_web_sm. They do not pin the language-model version or checksum.
- render.yaml performs the same dependency and language-model installation steps.
- CI specifies Python 3.11, but not an exact patch release or complete dependency resolution.
- v3/environment_versions.json records one observed environment: Python 3.11.9, scikit-learn 1.9.0, spaCy 3.8.16, en_core_web_sm 3.8.0, NumPy 2.4.6, pandas 3.0.6, SciPy 1.17.1, joblib 1.6.0, and seed 42. This is a snapshot, not an authenticated lock or build attestation.
- Historical commit 44c5e92257fa4265b15eb2487bca3644985a6416 is titled “pin scikit-learn==1.8.0 and add lock file to prevent concurrent model downloads.” Its diff changed requirements.txt and download_models.py only; no dependency lock file was added. The “lock” was an application download lock, not a reproducible dependency lock.
- Historical commit c8aa0539ec437fe68522098eae5befe62223ec0b changed the scikit-learn requirement to 1.9.0 to match retrained model artifacts. This records a compatibility decision but does not identify the full environment or prove artifact origin.

### Classification

Dependency reproducibility remains **PARTIALLY RESOLVED** by documented versions and commands, but the complete reproducible environment is **STILL BLOCKED**. No dependency evidence resolves artifact authenticity.

## Phase C — Dataset provenance evidence

### Evidence found

- data/Fake.csv and data/True.csv exist locally and are ignored by .gitignore:11.
- Git does not track the dataset files. Git history shows no dataset-file commits.
- download_data.py:14-16 names a Hugging Face WELFake URL and download_data.py:94-95 names a Kaggle “Fake and Real News Dataset” fallback.
- download_data.py:58-96 can write data files from the mutable Hugging Face main URL; download_data.py:17-55 can create a small embedded demonstration dataset.
- Existing v1/v2/v3 source_provenance.json records current/local file hashes, sizes, row counts, schema, and label mapping. Those records are local evaluation evidence, not independently authenticated publisher records.
- The current local hashes match the recorded v3 hashes, but no file records an upstream release/version, acquisition date, publisher signature, or license binding.
- Project documentation repeatedly states that the exact source/revision of the 24,353-row corpus is unknown.

### Classification

Dataset existence, schema, labels, and local consistency are **PARTIALLY RESOLVED**. Upstream origin, revision, acquisition record, and authenticated source binding are **STILL BLOCKED**. Matching local hashes are not treated as authenticity evidence.

## Phase D — Artifact trust and reference-output evidence

### Evidence found

- No tracked artifact manifest generator, signed manifest, detached signature, checksum signed by an independently verified key, CI build attestation, or authenticated release record was found.
- Git history shows model distribution was moved to GitHub Releases in commits 7035951b128dc527dabc30d329d31ce049fc8578 and 94a3bde2bcfebe0066b817d46374dd5ef6e91e03. This proves the distribution mechanism was added, not that the assets are authenticated.
- download_models.py currently obtains artifact_manifest.json from the same release URL as the model assets.
- Existing evaluation artifact_hashes.json files cover evaluation outputs and source records; they do not provide an independently authenticated reference for the production pickles.
- Existing metrics and prediction/evaluation outputs are useful behavioral records but are not trusted reference probabilities tied to authenticated model bytes.
- The local v2.0-calibrated-models tag is an unsigned commit tag; no signed tag or signed release manifest was found.

### Classification

Artifact trust and independently authenticated reference outputs remain **STILL BLOCKED**. Local evaluation hashes and report metrics are **PARTIALLY RESOLVED** as consistency evidence only.

## Phase E — Task 17 blocker classification

| Task 17 blocker | Classification | Evidence and remaining gap |
|---|---|---|
| production_switch meaning | REQUIRES PROJECT-OWNER DECISION | Git proves initial false/false agreement and later report-only change to true, but no commit defines semantics. |
| Current runtime effect of production_switch | RESOLVED BY EXISTING EVIDENCE | predictor.py does not read it; active five-model set and averaging are explicit in source. |
| Dataset files and local hashes | PARTIALLY RESOLVED | Files exist and match local provenance records; upstream origin and historical build binding are absent. |
| Authenticated dataset origin | STILL BLOCKED | No publisher/revision/acquisition/license record is independently authenticated. |
| Training/calibration procedure | PARTIALLY RESOLVED | Tracked scripts define the current five-model procedure, seeds, splits, and calibration; historical execution and exact source revision remain unproven. |
| Complete dependency/environment reproducibility | STILL BLOCKED | Requirements are not fully pinned; no dependency lock, model checksum, container digest, or authenticated build record exists. |
| Trusted functional reference | STILL BLOCKED | No independently authenticated reference predictions/probabilities or trusted historical bundle. |
| Byte-identical reference | STILL BLOCKED | No independently trusted artifact hashes; local hashes are not proof of authenticity. |
| Artifact manifest generation | STILL BLOCKED | No local generator or authenticated manifest exists. |
| Release authenticity/trust root | STILL BLOCKED | Unsigned tag and same-source manifest do not establish origin. |
| Production loading approval | STILL BLOCKED | The authenticity and reference gaps remain; no production artifacts were loaded in this audit. |

## Exact files and Git revisions inspected

Files:

- phase2_calibration.py
- predictor.py
- artifact_contract.py
- download_models.py
- train.py
- evaluate_pipeline.py
- preprocessor.py
- download_data.py
- generate_held_out_test_set.py
- compare_calibration.py
- requirements.txt
- Dockerfile
- render.yaml
- .github/workflows/ci.yml
- README.md
- PROJECT_MASTER_DOCUMENTATION.md
- PROJECT_DOCUMENTATION_INDEX.md
- PROJECT_DOCUMENTATION_COVERAGE.md
- evaluation_results/phase1_evaluation_report.json
- evaluation_results/phase2_calibration_report.json
- evaluation_results/phase2_comparison.json
- evaluation_results/group_aware_model_evaluation/v1, v2, and v3 provenance/hash/environment records
- .gitignore
- filenames and metadata under data/ and models/ only

Git revisions/history:

- Current HEAD 8c41ae005f4bee178a2b0104cb29049f00182081.
- 0ddbd3498e3c06a791efb34a3f37c9181eb6a08b: initial Phase 1/2 report and generator.
- 2c9974f6e2732398364786d70e0669239aca1941: diagnostic logging, no production_switch change.
- 353c20f241d73f7e875508b1eb22eafc6943f9bb: report true and Random Forest removal from report/predictor.
- efb475ef5460cb720006fc8abc1dee58a041d165: Random Forest removal from generator.
- 44c5e92257fa4265b15eb2487bca3644985a6416: scikit-learn 1.8 and application download lock history.
- c8aa0539ec437fe68522098eae5befe62223ec0b: scikit-learn 1.9 compatibility change.
- 7035951b128dc527dabc30d329d31ce049fc8578 and 94a3bde2bcfebe0066b817d46374dd5ef6e91e03: GitHub Release download history.
- v2.0-calibrated-models tag: d7df986f59860959e64a2a201f0e2e0077649240, previously verified as an unsigned commit tag.

## Limitations and unresolved questions

- No network access was used, so public release contents were not rechecked.
- No production pickle/joblib content was inspected or deserialized.
- Git history cannot establish which machine, environment, dataset acquisition, or command generated the post-353 report.
- The owner must explain why production_switch changed in the report without a corresponding generator change.
- The owner must identify the upstream dataset revision and provide an independently authenticated release/build record or approve a clearly new release.
- No conclusion here treats matching hashes, local manifests, unsigned tags, filenames, timestamps, or metrics as authenticity proof.

## Recommended next action

Request the project owner’s written production_switch decision and historical report-generation record first. In parallel, recover an authenticated dataset source/revision and complete environment/build evidence. If those cannot be recovered, create a separately versioned new release from reviewed inputs and a controlled environment, explicitly without claiming historical reproduction, then establish an independent signing trust root before any production activation.

Do not load or rebuild the current production artifacts until those decisions and trust prerequisites are satisfied.

## Git state after audit

- HEAD remains 8c41ae005f4bee178a2b0104cb29049f00182081.
- Existing working-tree changes and untracked files remain preserved.
- New directory/report added: evaluation_results/historical_evidence_trace_2026-10-21/HISTORICAL_EVIDENCE_TRACE.md.
- No existing file was intentionally modified by this task.

