# Project Documentation Coverage Record

**Reviewed:** 12 October 2026
**Repository:** Fake News Detector (TruthScan)
**Repository root:** `.` (repository-relative paths)
**Remote:** `https://github.com/ashutosh8950/fake-news-detector`

This record separates this documentation review from older inventory notes. It does not claim complete repository coverage.

## Current Review Scope and Findings

Reviewed all four documentation files. Cross-checked the relevant behavior against `app.py`, `config.py`, `preprocessor.py`, `predictor.py`, `routers/api.py`, `distilbert_predictor.py`, `download_models.py`, `download_data.py`, `train.py`, `evaluate_pipeline.py`, `phase2_calibration.py`, `render.yaml`, `Dockerfile`, `requirements.txt`, `.github/workflows/ci.yml`, `README.md`, `frontend/index.html`, `frontend/app.js`, both evaluation reports, and both test modules.

Confirmed the five active classifier keys, artifact names/locations, API validation and rate limits, class mapping, title repetition, TF-IDF configuration, probability averaging, response fields, startup behavior, configured build commands, and the reported Phase 2 metric values. Git index inspection confirms `phase1_evaluation_report.json`, `phase2_calibration_report.json`, and `phase2_comparison.json` are tracked. The 24,353/20,700/3,653 counts and accuracy/Brier values are **observed in tracked reports**; the exact historical dataset source/revision is not recorded.

Corrections made in the Markdown documents: removed the personal absolute Windows path; added a beginner learning path and metric explanations; corrected OpenAPI to the current environment's 3.1.0; clarified `/metrics` excludes `/analyze/deep`; documented browser `localStorage` retention; corrected download/retraining/setup instructions and unsupported performance claims; documented the `production_switch` mismatch; and replaced unsupported verification claims with this record.

The PDF metadata identifies ReportLab, but no source script, command, or generation configuration was found in the repository. It was preserved unchanged. It is 49 pages, its extracted text contains the old absolute local path, and it may not reflect the updated Markdown.

### Evidence labels

- **Verified:** directly confirmed in checked-out code or configuration.
- **Observed locally:** present in a local report or artifact; origin/tracking/reproducibility may differ.
- **Reported, unverified:** stated in project material but not independently reproduced from repository evidence.
- **Unknown:** not established by available sources or not checked against a live/external system.

---

## 1. Inspection Method for This Update

- Read the Markdown handbook, index, and coverage record; extracted PDF metadata and searchable text with `pypdf`.
- Read `frontend/app.js` and `frontend/index.html`; inspected relevant sections of application/API/model-loading/training code and deployment configuration.
- Read report fields relevant to row counts, scores, calibration methods, and confusion/evaluation workflow. Did not independently rerun the expensive evaluation/calibration jobs.
- Inspected local model filenames/sizes but did not deserialize model artifacts.
- Did **not** inspect the full training datasets, notebook, or `frontend/style.css` in this update.
- Did **not** inspect external Hugging Face weights, GitHub Release payloads, or the live Render service.
- Did **not** establish a reproducible PDF build procedure or visually inspect every PDF page.
- The inventory below includes prior recorded statuses and sizes; entries not named in the current review scope were not re-audited here.

---

## 2. File Inventory and Status

Statuses: **Inspected** | **Partially inspected** | **Excluded** | **Inaccessible**

### 2.1 Core Application

| Path | Category | Status | Handbook Location |
|------|----------|--------|-------------------|
| `app.py` | Backend entry | Inspected (173 lines) | E.1, C, D, L, M |
| `config.py` | Configuration | Inspected (12 lines) | E.2, J |
| `predictor.py` | Inference | Inspected (184 lines) | E.4, D, I |
| `preprocessor.py` | NLP preprocessing | Inspected (51 lines) | E.3, I |
| `distilbert_predictor.py` | Optional ML | Inspected (54 lines) | E.6, I.6, G |
| `routers/api.py` | HTTP API | Inspected (142 lines) | E.5, G, D |

### 2.2 Training, Evaluation, Data Tooling

| Path | Category | Status | Handbook Location |
|------|----------|--------|-------------------|
| `train.py` | Legacy training | Inspected (169 lines) | E.7, I, N |
| `evaluate_pipeline.py` | Phase 1 eval | Inspected (361 lines) | E.8, I |
| `phase2_calibration.py` | Phase 2 calibration | Inspected (267 lines) | E.9, I |
| `compare_calibration.py` | Offline comparison | Inspected (161 lines) | E.12 |
| `generate_held_out_test_set.py` | Split helper | Inspected (28 lines) | E.13 |
| `download_models.py` | Artifact download | Inspected (116 lines) | E.10, J, M |
| `download_data.py` | Dataset download | Inspected (111 lines) | E.11, J, H |

### 2.3 Evaluation Results and Data

| Path | Category | Status | Handbook Location |
|------|----------|--------|-------------------|
| `evaluation_results/phase2_calibration_report.json` | Metrics | Inspected (294 lines) | I, G, A |
| `evaluation_results/phase1_evaluation_report.json` | Metrics | Inspected (273 lines) | I, H |
| `evaluation_results/phase2_comparison.json` | Comparison | Not read (exists, 5.8 KB) | — |
| `evaluation_results/held_out_test_set.csv` | Test data | Not read (9.5 MB, binary CSV) | H |
| `data/Fake.csv` | Training data | Not read (30 MB, binary CSV) | H |
| `data/True.csv` | Training data | Not read (34 MB, binary CSV) | H |
| `tests/fixtures/nasa_test_sample.csv` | Test fixture | Not read (283 KB CSV) | K |

### 2.4 Frontend

| Path | Category | Status | Handbook Location |
|------|----------|--------|-------------------|
| `frontend/index.html` | UI | Partially inspected (80 of 299 lines) | E.14 |
| `frontend/app.js` | UI logic | Not inspected (25,965 bytes) | E.15 |
| `frontend/style.css` | UI styles | Not inspected (36,836 bytes) | — |

### 2.5 Tests

| Path | Category | Status | Handbook Location |
|------|----------|--------|-------------------|
| `tests/__init__.py` | Test config | Inspected (15 bytes, empty) | — |
| `tests/test_api.py` | Unit tests | Inspected (86 lines) | E.16, K |
| `tests/test_nasa.py` | Integration tests | Inspected (38 lines) | E.17, K |

### 2.6 Deployment and Configuration

| Path | Category | Status | Handbook Location |
|------|----------|--------|-------------------|
| `Dockerfile` | Container | Inspected (25 lines) | E.18, M |
| `render.yaml` | Cloud deploy | Inspected (13 lines) | E.19, M |
| `.github/workflows/ci.yml` | CI/CD | Inspected (36 lines) | E.20, M |
| `requirements.txt` | Dependencies | Inspected (17 lines) | F |
| `.gitignore` | SCM | Inspected (17 lines) | — |
| `.dockerignore` | Docker | Inspected (10 lines) | — |
| `README.md` | Documentation | Inspected (309 lines) | — |

### 2.7 Model Artifacts (Binary — Not Deeply Inspected)

| Path | Category | Status | Notes |
|------|----------|--------|-------|
| `models/calibrated/vectorizer.pkl` | Model artifact | Excluded (binary) | Size: 6.3 MB |
| `models/calibrated/lr_calibrated.pkl` | Model artifact | Excluded (binary) | Size: 6 MB |
| `models/calibrated/dt_calibrated.pkl` | Model artifact | Excluded (binary) | Size: 148 KB |
| `models/calibrated/gbc_calibrated.pkl` | Model artifact | Excluded (binary) | Size: 1.2 MB |
| `models/calibrated/nb_calibrated.pkl` | Model artifact | Excluded (binary) | Size: 24 MB |
| `models/calibrated/rfc_calibrated.pkl` | Model artifact | Excluded (binary) | Size: 89 MB; not loaded in production |
| `models/calibrated/svc_calibrated.pkl` | Model artifact | Excluded (binary) | Size: 6 MB |
| `models/deprecated_contaminated/` | Deprecated | Excluded | Contaminated artifacts; do not use |

### 2.8 Other Files

| Path | Category | Status | Notes |
|------|----------|--------|-------|
| `notebooks/FAKE_NEWS_DETECTION.ipynb` | Notebook | Excluded (binary, 280 KB) | Original exploration notebook |
| `assets/dashboard-preview.png` | Asset | Excluded (binary, 1.4 MB) | Dashboard screenshot |
| `.venv/` | Virtual env | Excluded | Python virtual environment |
| `__pycache__/` | Build artifact | Excluded | Compiled Python bytecode |
| `.pytest_cache/` | Test cache | Excluded | Pytest cache files |
| `.git/` | VCS | Excluded | Git repository internals |

---

## 3. Verification Performed

### 3.1 Repository claims checked

| Claim area | Evidence used | Result / qualification |
|---|---|---|
| Request validation, routes, rate limits, response fields | `routers/api.py`, `app.py`, `tests/test_api.py` | Text length 20–10,000 after stripping; title up to 500; `/analyze` 10/minute and `/analyze/deep` 5/minute; 422/429/500/503 paths documented. |
| Model loading and output | `predictor.py`, `download_models.py`, local `models/calibrated/` | Five active keys are LR, DT, GBC, NB, SVC. The vectorizer and report are also required. The app does not download them at startup. |
| Text processing and features | `preprocessor.py`, `phase2_calibration.py` | Title concatenation, cleanup, spaCy lemmas/stopword removal, unigrams/bigrams, 150,000 feature cap documented. Exact title influence is not asserted. |
| Evaluation counts and scores | Tracked `evaluation_results/phase1_evaluation_report.json`, `phase2_calibration_report.json` | Observed 24,353 total, 20,700 training, 3,653 held out; Phase 2 ensemble 0.984396 accuracy and 0.013835 Brier. The exact CSV provenance is not recorded. |
| Model methods and setup | `train.py`, `evaluate_pipeline.py`, `phase2_calibration.py`, `download_data.py`, `requirements.txt` | Legacy training differs from production calibrated artifacts; data download does not guarantee reproduction of the reported corpus. OS-specific setup now provided. |
| Frontend and privacy | `frontend/index.html`, `frontend/app.js` | API calls, localStorage stats/history, 10-entry cap, and 120-character snippet recorded. |
| Deployment | `Dockerfile`, `render.yaml`, `.github/workflows/ci.yml` | Build/start commands verified. Live service state, current host limits, and cold-start timings were not tested. |

### 3.2 Discrepancies recorded

- The current workspace FastAPI is 0.141.1 and emits OpenAPI 3.1.0; dependency requirements do not pin FastAPI to that exact version.
- `/metrics` server counters update in `POST /analyze` only, not `/analyze/deep`.
- The current `phase2_calibration.py` writes `production_switch: false`; the tracked Phase 2 report says `true`. `predictor.py` does not read this field.
- The tracked Phase 2 report has the stated metrics, but report/script disagreement means not every metadata field is reproducible as-is.
- Coverage statuses/file sizes in Section 2 came from a prior inventory and were not all recounted during this review. No deliverable size claims are used as validation evidence here.

### 3.3 Sensitive-data and PDF checks

- Searched the three Markdown files and extracted PDF text for Windows user paths, email addresses, common GitHub/Hugging Face/AWS token patterns, and private-key headers. No credential-like pattern or email was found. This is a text-pattern scan, not a dedicated secrets scanner or repository-wide history scan.
- The personal Windows path was found in all three original Markdown files and on PDF page 4. The Markdown paths were replaced with repository-relative wording. The PDF remains unchanged and still contains that path.
- `pypdf` read the PDF metadata: title “TruthScan — Fake News Detector: Project Master Documentation”, ReportLab producer, 49 pages. The extracted text contains the major chapters and representative claims from the **pre-edit** Markdown; token overlap at review start was approximately 99%. This is not a visual check and does not establish parity with the updated Markdown.

### 3.4 Commands and validation results

Record final results after running them for this update:

| Check | Result |
|---|---|
| `git diff --check` | Passed cleanly after the final documentation edits. |
| `.venv\Scripts\python.exe -m pytest -v tests/` | **6 passed, 2 deprecation warnings**, 29.02 seconds, Python 3.11.9. |
| Internal Markdown links | Custom relative-file/heading check: `broken links: []`; the checker emitted a Python `FutureWarning` from a regex pattern, but no broken links were reported. |
| PDF metadata/text | Read with global Python `pypdf`: 49 pages; title present; pre-edit Markdown chapter snippets found. No visual page inspection. |
| PDF SHA-256 | `29898F0C473860CD7EBDB8BA1D93B9593236864C4F09E2D317E7A2BC87A3643D` after final edit. |
| Workspace `.venv` PDF module | `pypdf` is not installed there; global Python was used for PDF inspection. |
| Final `git status --short` | `M README.md`, `M frontend/style.css`, and the three new documentation files are present; the PDF remains unchanged. |

No `validate_docs.py` is present in the repository; no result is claimed for it. No PDF-generation command was found or run.

## 4. Remaining Unknowns and Checks Not Performed

- Exact source and revision of the 24,353-row corpus, and whether local CSVs exactly match the report-generation inputs.
- Why `production_switch` differs between the current calibration script and local report; a retraining run was not performed.
- DistilBERT training/evaluation evidence for the README's 99.97% result; the training scripts/weights were not inspected.
- Current live Render behavior, rate-limit behavior behind a proxy, cold-start time, deployment memory limits, and live DistilBERT availability.
- GitHub Release availability/content and full deserialization safety of downloaded pickle files.
- Full `frontend/style.css`, notebook, all CSV contents, and `phase2_comparison.json` were not reviewed in this update.
- PDF generation command/source and visual page-by-page readability were not established. The existing PDF may be stale; it was intentionally preserved.

## 5. Documentation Gaps to Revisit

1. Record dataset provenance/revision alongside evaluation reports so training can be reproduced.
2. Resolve and document the `production_switch` metadata mismatch.
3. Add reproducible DistilBERT training/evaluation evidence before presenting its score as verified.
4. Establish a versioned PDF build command and validate the rendered artifact before replacing it.
5. Document current CSS and notebook details only if they are needed by maintainers.

## 6. Changes in This Documentation Update

- Added a beginner-first explanation, architecture flow, terminology, metrics, OS-specific setup, evaluation/training distinctions, browser retention behavior, and practical interview material to the master handbook.
- Reworked the index into five-minute and beginner-to-advanced reading paths with evidence labels.
- Replaced absolute paths and stale validation claims; recorded reviewed sources, actual discrepancies, unknowns, and checks for this update.
- Did not regenerate the PDF because there is no verified build command in the repository, and the existing PDF was intentionally left unchanged.

---

*Coverage record last updated: 12 October 2026*
