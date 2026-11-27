# TruthScan Configuration and Rebuild Readiness Audit

Date: 2026-10-21 (Asia/Calcutta)

## Executive verdict

**BLOCKED PENDING MISSING INPUTS OR DEPENDENCIES.**

The production_switch conflict is real but does not currently control model selection or inference. The Phase 2 report records JSON boolean true, while the current calibration script writes Python boolean False, serialized as JSON false. No production code reads this field. It remains a release-state/configuration ambiguity that requires an owner decision before a new release record is accepted.

The repository is close to being able to run an isolated rebuild experiment from local source and data, but it is not ready for acceptance-grade rebuild approval. A complete dependency/environment lock, authenticated dataset origin record, and independently trusted reference are missing. Without a trusted reference, functional-equivalence and byte-identical tests are unavailable; without an independent trust root, a new bundle would remain unauthenticated.

No production artifact was loaded, downloaded, modified, overwritten, or retrained.

## Phase A — production_switch analysis

### Evidence

1. evaluation_results/phase2_calibration_report.json, top-level JSON key production_switch at line 8, records true with type JSON boolean. PowerShell parsed it as System.Boolean.
2. phase2_calibration.py:197-205 constructs the report and writes "production_switch": False, which becomes JSON boolean false.
3. predictor.py:64-83 verifies the report, then loads the vectorizer and five model files. It does not read report["production_switch"].
4. predictor.py:30-36 defines the active model set as lr, dt, gbc, nb, and svc.
5. predictor.py:88-106 reads per-model metrics and calibration method from the report, but not production_switch.
6. predictor.py:126-150 computes class-1 probabilities and the average five-model probability with a 0.5 threshold.
7. phase2_calibration.py:209-254 builds those five calibrated models, averages their class-1 probabilities, and writes the Phase 2 ensemble report. The field is metadata only in the current implementation.
8. PROJECT_MASTER_DOCUMENTATION.md:808-810, PROJECT_DOCUMENTATION_COVERAGE.md:151-154, and the Task 16 report record the same mismatch and state that predictor.py does not read the field.

### Semantics and impact

- Recorded value: true, boolean, in the local Phase 2 report.
- Current generated value: false, boolean, in the checked-out calibration script.
- Current application behavior: no change to estimator choice, calibration method, five-model membership, averaging, threshold, labels, or probability interface.
- Release/audit meaning: unresolved. The name suggests a promotion flag, but current code gives it no operational semantics.
- It is not safe to silently normalize the report to either value because that would erase evidence of source/report drift.

### Required owner decision

Local evidence cannot determine which value was intended historically. The owner must provide an authoritative build/release record explaining true, explicitly deprecate the field, or define its promotion semantics and identify the approved artifacts/report. Until then, preserve the historical report unchanged and use a separate, unambiguous release-state field for any new build.

## Phase B — Rebuild prerequisite inventory

Classification meanings are the requested categories: VERIFIED FROM LOCAL EVIDENCE, DOCUMENTED BUT NOT INDEPENDENTLY VERIFIED, MISSING, CONFLICTING, and NOT APPLICABLE.

| Prerequisite | Classification | Evidence and limitation |
|---|---|---|
| data/Fake.csv present | VERIFIED FROM LOCAL EVIDENCE | Present locally; v3/source_provenance.json records 11,107 rows, SHA-256 672ab39a75ac75fef9ecbb1a84e2936e064b44a32197a4801d9d0fb63ca9d57e, and size 30,163,788 bytes. Matching the record does not verify upstream origin. |
| data/True.csv present | VERIFIED FROM LOCAL EVIDENCE | Present locally; records show 13,246 rows, SHA-256 c3105d9266fd2ad484aad43b13801930434ffcd68894cc975128e52433a0c6ad, and size 34,031,181 bytes. Same origin limitation. |
| Dataset upstream source/revision | MISSING | download_data.py names mutable Hugging Face main and a Kaggle fallback; no authenticated source revision is recorded for the current corpus. |
| Schema and label mapping | VERIFIED FROM LOCAL EVIDENCE | Provenance records ordered columns title,text,subject,date; Fake=0 and True=1. Training/calibration scripts implement that mapping. |
| Historical dataset-to-bundle binding | MISSING | No trusted build record binds the current CSV bytes to the existing production files. |
| Held-out split | DOCUMENTED BUT NOT INDEPENDENTLY VERIFIED | held_out_test_set.csv exists; Phase 1/2 requires 3,653 held-out and 20,700 training rows and reconstructs membership by title,text,class. Historical generation and authenticated membership evidence are absent. |
| Preprocessing | VERIFIED FROM LOCAL EVIDENCE | preprocessor.py:18-50 implements cleaning, triple-title concatenation, spaCy stopword removal, and lemmatization. |
| spaCy/model identity | DOCUMENTED BUT NOT INDEPENDENTLY VERIFIED | v3/environment_versions.json records spaCy 3.8.16 and en_core_web_sm 3.8.0, but no lockfile, model checksum, or authenticated environment record exists. |
| TF-IDF configuration | VERIFIED FROM LOCAL EVIDENCE | phase2_calibration.py:59-70 records n-grams (1,2), max_features 150000, sublinear TF, word analyzer, min_df 2, max_df 0.95. |
| Five estimator configurations | VERIFIED FROM LOCAL EVIDENCE | phase2_calibration.py:49-56 records LR, DT, GBC, NB, and SVC settings and seeds where applicable. |
| Calibration procedure | VERIFIED FROM LOCAL EVIDENCE | phase2_calibration.py:105-147 and 209-220 compare sigmoid/isotonic using seeded 20% inner validation, five-fold calibration, and lower Brier score. |
| Calibration selection result | DOCUMENTED BUT NOT INDEPENDENTLY VERIFIED | Current report records isotonic for all five, but the report is not authenticated and historical execution is not independently attested. |
| Random seeds | VERIFIED FROM LOCAL EVIDENCE | RANDOM_STATE=42 appears in Phase 1/2; stochastic estimator seeds are recorded. Some library behavior remains version-dependent. |
| Complete dependency lock | MISSING | requirements.txt pins only scikit-learn exactly; most dependencies are lower bounds. No pyproject.toml, poetry.lock, Pipfile.lock, or resolved requirements lock was found. |
| Environment snapshot | DOCUMENTED BUT NOT INDEPENDENTLY VERIFIED | v3 records Python 3.11.9, NumPy 2.4.6, pandas 3.0.6, SciPy 1.17.1, joblib 1.6.0, spaCy 3.8.16, model 3.8.0, and scikit-learn 1.9.0. It is not a trusted build attestation. |
| Artifact writer | VERIFIED FROM LOCAL EVIDENCE | phase2_calibration.py:190-222 and 260-262 writes the vectorizer, five calibrated model files, and report. |
| Output names/membership | VERIFIED FROM LOCAL EVIDENCE | artifact_contract.py:14-22, download_models.py:25-27, and predictor.py:30 define the five-model bundle. Local extra rfc_calibrated.pkl is not active production membership. |
| Manifest generator | MISSING | No local manifest-generation script or trusted manifest exists. |
| Artifact authenticity/trust root | MISSING | Existing hashes and unsigned release metadata do not authenticate origin. |
| Trusted reference predictions/bundle | MISSING | No independently trusted reference probabilities, predictions, or signed historical bundle is available. |
| Byte-identical reference hashes | MISSING | Local hashes cannot serve as an independent reference. |
| production_switch semantics | CONFLICTING | Report says true; generator writes false; runtime ignores the field. Owner decision is required. |
| Legacy train.py as production path | NOT APPLICABLE | It is an uncalibrated six-model workflow with different splitting and output names. |

## Rebuild readiness

Static evidence supports planning an isolated build from local data and the current Phase 2 script. The code paths, estimator settings, calibration procedure, local CSVs, held-out file, and output names are present. This would be exploratory only and must use a new namespace; it must not touch models/calibrated or prior evaluation namespaces.

Acceptance-grade rebuild is not ready because the exact environment is not locked, dataset origin is not authenticated, the production_switch meaning is unresolved, and no trusted reference exists for comparison or authenticity.

## Phase C — Rebuild acceptance criteria

### Procedural reproducibility

Require a clean reviewed source revision; authenticated dataset source/revision and hashes; exact held-out membership; complete dependency/runtime lock; spaCy model identity/checksum; preprocessing/vectorizer/estimator/calibration configuration; seeds; exact commands; and outputs written only to a versioned non-production directory.

Current status: UNAVAILABLE.

### Functional equivalence

Require an independently trusted reference bundle or reference prediction/probability corpus. Define the corpus, labels, per-model outputs, ensemble output, and justified tolerances before running the rebuild. Do not derive tolerances from observed rebuild results.

Current status: UNAVAILABLE. No trusted reference exists.

### Byte-identical reproduction

Require independently trusted reference hashes for every required artifact and control of serialization-relevant inputs. A byte match supports equality to that trusted reference; it does not prove historical origin unless the reference itself is authenticated.

Current status: UNAVAILABLE. Existing local hashes are not an independent reference.

### Release authenticity

Require an independently verified trust root, signing-key fingerprint or release-attestation identity, a signed manifest binding source revision/release ID to every artifact digest, verification before deserialization, bundle compatibility checks, atomic activation, and rollback evidence.

Current status: UNAVAILABLE. No trusted manifest, signature, or authenticated release digest exists.

## Phase D — Recommended next action

### Decision: BLOCKED PENDING MISSING INPUTS OR DEPENDENCIES

This is not READY FOR AN ISOLATED REBUILD EXPERIMENT at acceptance-grade scope. An exploratory rebuild could be planned, but it would not resolve the release blocker and would produce no trusted comparison result.

Minimum prerequisites:

1. Owner decision and written semantics for production_switch, including explanation of the historical true value.
2. Authenticated dataset origin/revision, or an explicit decision to create a new release from current local data without claiming historical reproduction.
3. Fully resolved dependency/runtime lock, including spaCy model identity/checksum.
4. Separate non-production output namespace and write guard.
5. Independently trusted reference predictions or release bundle if equivalence is required.
6. Independent trust-root/signing design before any release-authenticity claim.

Recommended next implementation task: resolve the owner decision, then create a synthetic non-production rebuild harness that validates output paths, manifest completeness, compatibility checks, and pre-deserialization trust verification without loading real artifacts.

## Exact files inspected

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
- README.md
- Dockerfile
- render.yaml
- .github/workflows/ci.yml
- PROJECT_MASTER_DOCUMENTATION.md
- PROJECT_DOCUMENTATION_INDEX.md
- PROJECT_DOCUMENTATION_COVERAGE.md
- evaluation_results/phase1_evaluation_report.json
- evaluation_results/phase2_calibration_report.json
- evaluation_results/phase2_comparison.json
- evaluation_results/held_out_test_set.csv (existence/role only)
- evaluation_results/group_aware_model_evaluation/v3/source_provenance.json
- evaluation_results/group_aware_model_evaluation/v3/environment_versions.json
- evaluation_results/group_aware_model_evaluation/v3/artifact_hashes.json
- filenames, sizes, and timestamps under models/ only; no pickle/joblib contents

## Actions and limitations

Performed:

- Read-only source and documentation inspection with line references.
- Read-only JSON metadata inspection.
- Parsed production_switch and confirmed boolean type.
- Checked dataset existence, metadata, and SHA-256 against recorded provenance.
- Checked for lockfiles and manifest presence.
- Recorded Git state before and after.
- Created only this new report.

Not performed:

- No production pickle/joblib opened, loaded, or deserialized.
- No model, dataset, language model, or package downloaded.
- No retraining or rebuild.
- No production, training, calibration, deployment, artifact, tag, evaluation namespace, or prior audit report edited.
- No signing key, signature, release, commit, push, or deployment created.

Limitations:

- Static inspection cannot establish historical execution environment or prove that the local bundle came from the inspected code.
- Local dataset hashes establish consistency with local records, not external authenticity.
- Functional and byte-identical tests are unavailable without a trusted reference.
- Owner intent and public release contents were not independently re-established in this audit.

## Git state

### Before audit

- HEAD: 8c41ae005f4bee178a2b0104cb29049f00182081
- Branch: main
- Pre-existing modified and untracked files, including prior audit directories, were preserved.

### After audit

- HEAD remains 8c41ae005f4bee178a2b0104cb29049f00182081.
- Existing working-tree changes remain preserved.
- New directory added: evaluation_results/configuration_rebuild_readiness_2026-10-21/
- No other repository state was intentionally changed.

## Work status and estimates

- Completed: production_switch analysis, prerequisite inventory/classification, rebuild acceptance criteria, and next-action recommendation.
- Remaining: obtain the owner decision, recover/authenticate missing dataset and environment provenance, then conduct any approved isolated rebuild.
- Estimated next task: 2–4 hours for the synthetic rebuild-harness/trust-verification design after the configuration decision; 1–2 business days if authenticated inputs and a controlled rebuild are supplied.
- Estimated total remaining duration: approximately 1–2 business days after missing provenance, lock, and trust-root inputs are available; longer if the historical bundle must be reconstructed.

