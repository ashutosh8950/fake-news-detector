# TruthScan Model Reproducibility and Trusted Release Plan

Date: 2026-10-21 (Asia/Calcutta)

## Executive verdict: CONDITIONAL FAIL — rebuildable in principle, historical production provenance not established

The repository contains enough code and local inputs to define a plausible controlled rebuild of the five-model calibrated ensemble, but it does not contain enough authenticated evidence to prove that the existing production bundle was produced from those inputs or that a fresh rebuild would be byte-identical. The current CSV files match the hashes and sizes recorded in the local group-aware provenance records, which establishes local consistency with those records only; it does not establish the original external dataset source, revision, or historical artifact lineage.

The existing production release blocker remains active. No production pickle/joblib file was loaded or deserialized, no dataset or model was downloaded, no model was retrained, and no production code, artifact, tag, prior audit report, or prior evaluation namespace was modified.

## Phase A — Trusted training-input inventory

### Available inputs and pipeline

- Dataset paths are `data/Fake.csv` and `data/True.csv`.
- They are present locally. Their current SHA-256 values and sizes match `evaluation_results/group_aware_model_evaluation/v3/source_provenance.json`:
  - `Fake.csv`: `672ab39a75ac75fef9ecbb1a84e2936e064b44a32197a4801d9d0fb63ca9d57e`, 30,163,788 bytes, 11,107 rows.
  - `True.csv`: `c3105d9266fd2ad484aad43b13801930434ffcd68894cc975128e52433a0c6ad`, 34,031,181 bytes, 13,246 rows.
- The provenance records document columns `title,text,subject,date`, labels Fake=0 and True=1, and label rules. They do not identify an authenticated upstream dataset revision or a signed acquisition record.
- `download_data.py:14-16,58-96` names Hugging Face WELFake as a primary download path and a Kaggle dataset as a manual fallback. It can also generate a 10-row-per-class demo dataset (`download_data.py:17-55`). None of these paths proves that the present 24,353-row corpus came from that exact source/version.
- `preprocessor.py:18-50` lowercases, removes URLs/HTML/punctuation/numeric content, removes non-ASCII letters, triples the title, and uses spaCy `en_core_web_sm` for stopword removal and lemmatization.
- `phase2_calibration.py:59-70` fits `TfidfVectorizer(ngram_range=(1,2), max_features=150000, sublinear_tf=True, analyzer="word", min_df=2, max_df=0.95)` on processed training text.
- `phase2_calibration.py:73-102` reconstructs the Phase 1 split from the local held-out CSV by `(title,text,class)` membership and requires exactly 20,700 training rows and 3,653 held-out rows.
- `phase2_calibration.py:49-56` defines the five production base estimators and `phase2_calibration.py:105-147` compares sigmoid and isotonic calibration using a seeded 20% inner split, five-fold `CalibratedClassifierCV`, and lower inner-validation Brier score.
- `phase2_calibration.py:165-262` fits the vectorizer, writes the vectorizer and five calibrated models, evaluates on the held-out rows, and writes the Phase 2 report.

### Estimator and calibration configuration

| Production key | Base estimator configuration | Calibration procedure |
|---|---|---|
| `lr` | `LogisticRegression(max_iter=1000, C=5.0, random_state=42)` | `CalibratedClassifierCV`, `cv=5`, `n_jobs=1`; choose sigmoid/isotonic by inner Brier score |
| `dt` | `DecisionTreeClassifier(max_depth=None, random_state=42)` | Same |
| `gbc` | `GradientBoostingClassifier(n_estimators=200, random_state=42)` | Same |
| `nb` | `MultinomialNB(alpha=0.01)` | Same |
| `svc` | `LinearSVC(C=1.0, max_iter=2000, random_state=42)` | Same; calibration supplies probabilities |

Recorded split/procedure settings include `random_state=42`, 15% outer held-out fraction in `evaluate_pipeline.py:33-35`, 20% inner calibration validation fraction, and five folds. The Phase 2 report records isotonic as selected for all five current entries.

### Production artifact writers and historical relationship

- `phase2_calibration.py` is the writer for the current five-model production bundle: `vectorizer.pkl`, `lr_calibrated.pkl`, `dt_calibrated.pkl`, `gbc_calibrated.pkl`, `nb_calibrated.pkl`, and `svc_calibrated.pkl`.
- `train.py:38-45,95-160` is a separate legacy six-model uncalibrated workflow. It writes `*_model.pkl`, includes Random Forest, uses a different tail-row exclusion and an adaptive 25% split, and does not write the calibrated production artifact names.
- `evaluate_pipeline.py:54-65,271-353` is a Phase 1 evaluation workflow. It evaluates six uncalibrated models and a six-model majority-vote ensemble, creates `held_out_test_set.csv`, and writes `phase1_evaluation_report.json`; it does not write production model files.
- `phase2_calibration.py` then consumes that held-out file and Phase 1 report but fits its own five-model calibrated artifacts. The Phase 1 report therefore provides evaluation/split context, not proof of the bytes currently in the production bundle.
- `evaluation_results/phase2_comparison.json` compares old and new evaluation results, but its metrics and filenames are not an authenticated build record.
- The local `models/calibrated/` directory also contains `rfc_calibrated.pkl`, although current Phase 2 code and `predictor.py:30` use only five models. This is legacy/extra state, not part of the current required bundle.

### Dependencies and environment records

- `requirements.txt` pins `scikit-learn==1.9.0` but leaves most dependencies as lower bounds and does not pin Python, spaCy, the `en_core_web_sm` model, NumPy, SciPy, pandas, joblib, or transitive dependencies.
- `evaluation_results/group_aware_model_evaluation/v3/environment_versions.json` records one environment: Python 3.11.9, scikit-learn 1.9.0, spaCy 3.8.16, `en_core_web_sm` 3.8.0, NumPy 2.4.6, pandas 3.0.6, SciPy 1.17.1, joblib 1.6.0, seed 42. This is useful evidence, but it is not a lockfile or independently authenticated build attestation.
- No `pyproject.toml`, `poetry.lock`, `Pipfile.lock`, Conda lockfile, fully resolved requirements lockfile, spaCy model checksum, container digest, or build attestation was found.
- The notebook contains historical estimator examples with different settings, including `random_state=0` and scikit-learn 1.6-rendered output. It must not be treated as the production build recipe without further reconciliation.

## Phase B — Reproducibility assessment

Reproducibility here means the ability to perform a reviewed rebuild from identified inputs. It does not mean the current local bundle is authentic, and it does not imply byte identity.

| Required artifact | Classification | Evidence and unresolved issue |
|---|---|---|
| `vectorizer.pkl` | Partially reproducible | Writer and vectorizer settings are in `phase2_calibration.py`; current data and preprocessing are present. Exact historical source revision, spaCy model/package environment, row ordering, held-out reconstruction, and build provenance are not authenticated. Byte identity is not established. |
| `lr_calibrated.pkl` | Partially reproducible | Base estimator, seed, calibration candidates, split fraction, fold count, and output path are documented. Historical training run, exact dependency resolution, upstream data identity, and serialized bytes are not authenticated. |
| `dt_calibrated.pkl` | Partially reproducible | Same limitation; deterministic seed is recorded, but library implementation and complete build environment are not locked. |
| `gbc_calibrated.pkl` | Partially reproducible | Same limitation; gradient boosting serialization and training behavior depend on the exact resolved environment and source revision. |
| `nb_calibrated.pkl` | Partially reproducible | Same limitation; the calibration wrapper and isotonic payload are specified, but historical serialization and exact input lineage are not proven. |
| `svc_calibrated.pkl` | Partially reproducible | Same limitation; `LinearSVC` itself has no native probability interface and relies on the documented calibration wrapper. |
| `phase2_calibration_report.json` | Partially reproducible | The current script writes its schema and metrics, but the checked-in report says `production_switch: true` while current `phase2_calibration.py:204` hard-codes `production_switch: false`. This indicates source/report drift or post-generation editing. |
| `artifact_manifest.json` | Not currently reproducible | No local manifest or manifest-generation script was found. The current downloader expects a manifest from the release source, but its authenticity is unresolved. |

### Direct answers to the required questions

- **Are the training data identical to the existing production bundle’s data?** Not proven. The current CSVs match local provenance records, and the Phase 2 report has matching row counts, but no authenticated record binds those CSV bytes to the historical production build.
- **Does the training code reproduce the production configurations?** It defines a plausible current five-model configuration and matches the Phase 2 report’s model names/method. It cannot prove that the historical bundle was built by this exact source revision; the report/code `production_switch` mismatch is concrete evidence of drift.
- **Are calibration method and data partition known?** Largely, yes for the intended current procedure: 20,700/3,653 outer partition, seeded 20% inner split, five-fold CV, Brier selection, and isotonic reported for all five. The historical execution record and exact row membership provenance remain incomplete.
- **Are seeds and dependency versions sufficient?** Seeds are documented, but dependency declarations are not fully locked. The environment record is a snapshot, not an authenticated reproducible environment specification.
- **Can preprocessing and language-model versions be reconstructed?** The source implementation is available and one environment record names spaCy and `en_core_web_sm` versions. A complete, verified package/model lock and source revision are missing.
- **Would a rebuild be byte-identical?** No basis exists to claim that. A controlled rebuild may be functionally equivalent; byte identity would require the exact source tree, data bytes/order, Python and dependency builds, serialization behavior, and build process, followed by a byte-for-byte comparison. Matching metrics or local hashes would not prove historical origin.

## Phase C — Proposed trusted release process

### 1. Freeze and review inputs

Create a clean, reviewed source revision containing the exact training/preprocessing/calibration code. Record the Git commit and review approval. Use only verified dataset files whose hashes, sizes, schema, row counts, label mapping, and upstream source/revision are recorded. Preserve the exact held-out split and its generation procedure.

### 2. Make the build reproducible enough to audit

Use a controlled build environment with a fully resolved dependency lock, Python version, OS/container image digest, spaCy package version, and `en_core_web_sm` model version/checksum. Record the exact command line, environment variables, CPU/thread settings, random seeds, vectorizer settings, estimator settings, calibration protocol, and output paths. Treat nondeterminism as a documented risk; do not promise byte identity unless it is demonstrated.

### 3. Build and validate in isolation

Write all outputs into a new versioned staging directory. Generate the vectorizer, five calibrated models, and calibration report from the reviewed build. Validate class labels, probability shape/range, feature dimensions, report structure, model set, preprocessing regression fixtures, and evaluation thresholds. Never overwrite the existing local bundle during this task or during a failed build.

### 4. Generate a complete manifest

The manifest should cover exactly:

- `vectorizer.pkl`
- `lr_calibrated.pkl`
- `dt_calibrated.pkl`
- `gbc_calibrated.pkl`
- `nb_calibrated.pkl`
- `svc_calibrated.pkl`
- `phase2_calibration_report.json`

It should include each file’s size and SHA-256, bundle/release ID, source commit, dataset identities and hashes, dependency lock identity, preprocessing/configuration fingerprint, calibration metadata, build timestamp, and schema version. Extra files should be rejected or explicitly classified outside the production bundle.

### 5. Establish the trust root independently

The initial signing key must be verified through an owner-controlled channel separate from the artifact host: for example, a previously authenticated project domain, an organization security repository with an already trusted maintainer path, or an out-of-band confirmation by the project owner. Record the key fingerprint, authorized release identities, rotation policy, revocation mechanism, and compromise response. Merely placing a public key beside the manifest is insufficient if the same attacker can replace both.

An acceptable alternative is an independently authenticated release attestation/digest whose identity and authority are verified through a separate trust system. HTTPS transport and a checksum file hosted beside the artifacts are not, by themselves, independent authentication.

### 6. Sign and bind the release

Sign the manifest, and bind it to the release ID and reviewed source revision. Publish the signed manifest and release assets together, while retaining the independently distributed trust-root evidence. A signed manifest authenticates the bytes in that release; it does not prove that the model is good, unbiased, safe, or historically identical to an older bundle.

### 7. Verify before deserialization

The deployment downloader must first verify the trust root, signature, release/source binding, manifest schema, exact file set, sizes, and hashes in staging. Only after these checks pass may the application perform `joblib.load`/pickle deserialization. Then perform bundle compatibility validation before activation.

### 8. Activate and roll back safely

Use a single versioned bundle directory and an atomic activation pointer/symlink/manifest reference. Keep the prior known-good release until health, startup, inference, and resource checks pass. A failure must leave the prior release active. Record the active bundle ID and verification evidence in deployment logs.

### 9. Retain audit evidence and handle key compromise

Retain the signed manifest, trust-root verification, key fingerprint, source commit, dataset records, dependency lock, build logs, environment/container digest, compatibility-test results, deployment approval, active-bundle ID, and rollback evidence. On key compromise, revoke the key, publish a replacement trust-root statement through the independent channel, invalidate affected release IDs, rebuild or re-attest as necessary, and require a fresh verification before activation.

## Artifact authenticity versus reproducibility

These are separate gates:

- A signed bundle can be authentic to its publisher while remaining non-reproducible.
- A reproducible build can produce the same outputs repeatedly but is not authenticated unless its release identity and manifest are trusted.
- A local SHA-256 snapshot can detect later changes but cannot establish who produced the file or whether the file was ever an official release.
- The present repository has partial rebuild inputs, but neither historical authenticity nor byte-identical reproduction has been established.

## Phase D — Smallest legitimate remediation path

| Route | Benefits | Required recovery/evidence | Assessment |
|---|---|---|---|
| Rebuild from verified inputs, then sign a new release | Uses available source/data, creates a clean provenance boundary, and can produce a trusted new bundle | Confirm dataset source/revision, freeze current source, lock environment, validate the split/configuration, build in isolation, sign manifest independently | Feasible, but must be labelled a new release unless its equivalence to the historical bundle is proven |
| Obtain a bundle and signature from an independently authenticated publisher | Fastest way to preserve an official historical release if the publisher can prove custody | Publisher-supplied signed manifest/attestation, independently verified key, exact release ID, asset hashes, and compatibility evidence | Preferred if the original owner can provide it; not currently available in repository evidence |
| Recover missing provenance/build inputs first | May establish whether current bytes are the historical production output | Original training run logs, exact source commit, dataset acquisition record, dependency lock, environment/container identity, manifest/signature, release publication record | Required before claiming historical reproduction; current repository does not contain all of this |

### Recommendation

First request recovery of the original owner-controlled release manifest/signature and build record. If that cannot be recovered, use the controlled rebuild route from the current verified local dataset only as a **new, explicitly versioned release**, not as a claim that it reproduces the historical production bundle. The current data/code are sufficient to plan that rebuild, but the upstream dataset identity, exact historical source revision, complete environment lock, and signing trust root must be resolved before production approval.

## Release validation checklist

- [ ] Independent trust root and signing-key fingerprint verified out of band.
- [ ] Source commit reviewed and recorded; working tree clean for the build.
- [ ] Dataset upstream identity, revision, labels, schema, row counts, and hashes recorded.
- [ ] Exact held-out split and training/calibration partitions recorded.
- [ ] Fully resolved dependency lock, Python/runtime, spaCy package, and language-model version/checksum recorded.
- [ ] Preprocessing regression fixtures and configuration fingerprint pass.
- [ ] Five expected estimators/configurations and all seeds recorded.
- [ ] Calibration method-selection protocol, folds, fraction, and selected methods recorded.
- [ ] Manifest covers every required artifact and rejects missing/extra files.
- [ ] Manifest signature and release/source binding verify before any deserialization.
- [ ] Hash and size verification pass in isolated staging.
- [ ] Real-bundle class-label, probability, feature-dimension, report-schema, and ensemble compatibility tests pass.
- [ ] Clean deployment smoke test, readiness/health test, resource test, and rollback drill pass.
- [ ] Active release ID and complete audit evidence retained.
- [ ] Production approval issued separately from reproducibility and authenticity results.

## Exact files and configuration inspected

Source/configuration:

- `preprocessor.py`
- `train.py`
- `evaluate_pipeline.py`
- `phase2_calibration.py`
- `generate_held_out_test_set.py`
- `download_data.py`
- `compare_calibration.py`
- `requirements.txt`
- `Dockerfile`
- `render.yaml`
- `.github/workflows/ci.yml`
- `README.md`
- `config.py`
- `artifact_contract.py`
- `predictor.py`
- `download_models.py`
- `notebooks/FAKE_NEWS_DETECTION.ipynb` (metadata/code-text search only)

Evidence and metadata:

- `data/Fake.csv` and `data/True.csv` (names, sizes, timestamps, and SHA-256 only; no training run)
- `evaluation_results/held_out_test_set.csv` (existence/role, not used to retrain)
- `evaluation_results/phase1_evaluation_report.json`
- `evaluation_results/phase2_calibration_report.json`
- `evaluation_results/phase2_comparison.json`
- `evaluation_results/group_aware_model_evaluation/v1/` provenance/hash records
- `evaluation_results/group_aware_model_evaluation/v2/` provenance/hash records
- `evaluation_results/group_aware_model_evaluation/v3/` provenance, environment, configuration, selection, and validation records
- model directory filenames/sizes only; no pickle/joblib contents read

## Commands executed

- `git rev-parse HEAD`
- `git branch --show-current`
- `git status --short`
- metadata-only recursive listings of `data/`, `models/`, source files, and dependency/lock candidates
- numbered source inspection of the training, preprocessing, evaluation, calibration, download, and release files listed above
- read-only `rg` searches for model writers, calibration, seeds, artifact paths, and dependency metadata
- JSON metadata inspection of Phase 1/Phase 2 and group-aware evaluation records
- `Get-FileHash data/Fake.csv -Algorithm SHA256`
- `Get-FileHash data/True.csv -Algorithm SHA256`
- `git log --oneline --decorate -- ...` for training/calibration source history
- creation of this new report directory only

No training, model loading, deserialization, package installation, dataset download, model download, signing, tag modification, commit, push, deployment, or production-file write was performed.

## Git state

### Before this audit

- HEAD: `8c41ae005f4bee178a2b0104cb29049f00182081`
- Branch: `main`
- Existing user changes were present and preserved, including modified application/source files, untracked documentation, `artifact_contract.py`, `duplicate_aware_manifest.py`, existing evaluation directories, and tests.
- Existing audit directory `evaluation_results/trusted_provenance_audit_2026-10-21/` was not modified.

### After this audit

- HEAD remains `8c41ae005f4bee178a2b0104cb29049f00182081`.
- Existing working-tree changes remain unchanged.
- New audit directory added: `evaluation_results/model_reproducibility_release_plan_2026-10-21/`.
- No production code, model artifact, evaluation namespace, tag, or previous report was modified.

## Work status and estimates

- Completed: trusted-input inventory, training/calibration/reproducibility assessment, artifact-by-artifact classification, release trust-root design, remediation comparison, and release checklist.
- Remaining: recover an authenticated historical release/build record or execute a separately approved controlled rebuild and signed release; then implement/validate the trusted-release verifier path in a future task.
- Recommended next implementation task: define and review the signed manifest schema, independent trust-root distribution, and a synthetic end-to-end signature-verification test without touching real production artifacts.
- Estimated next-task duration: approximately 2–4 hours for schema/design and synthetic verification; 1–2 days for an owner-authenticated controlled rebuild and release evidence if required.
- Estimated total remaining duration: approximately 1–2 business days after provenance inputs are supplied, excluding any prolonged model rebuild or owner review.

