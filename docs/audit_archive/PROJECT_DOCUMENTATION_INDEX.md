# Project Documentation Index

**Project:** TruthScan / Fake News Detector
**Repository root:** `.` (use repository-relative paths)
**Repository URL configured in project:** `https://github.com/ashutosh8950/fake-news-detector`
**Demo URL configured in project:** `https://truthscan-fake-news-detector.onrender.com` (live availability not checked)
**Review date:** 12 October 2026
**Evidence priority:** Current source/configuration first; tracked evaluation reports and tests second. The held-out CSV and model binaries are separate generated/downloaded artifacts.

This is the navigation page. The editable handbook is [PROJECT_MASTER_DOCUMENTATION.md](PROJECT_MASTER_DOCUMENTATION.md). The existing [PDF handbook](PROJECT_MASTER_DOCUMENTATION.pdf) was created with ReportLab according to its metadata, but no reproducible project generation command was found; it may be out of date. Review evidence and remaining uncertainty are in [PROJECT_DOCUMENTATION_COVERAGE.md](PROJECT_DOCUMENTATION_COVERAGE.md).

---

## Which Document to Open First

Start with [Start Here: Beginner's Guide](PROJECT_MASTER_DOCUMENTATION.md#start-here-beginners-guide) if TruthScan or machine learning is new to you. Read the Markdown master before relying on the PDF; the PDF regeneration process could not be reproduced from repository evidence.

## Five-Minute Overview

1. [What TruthScan does and cannot establish](PROJECT_MASTER_DOCUMENTATION.md#chapter-a-executive-overview).
2. [Request flow and startup](PROJECT_MASTER_DOCUMENTATION.md#chapter-c-system-architecture).
3. [The measured Phase 2 results and metric meanings](PROJECT_MASTER_DOCUMENTATION.md#i0-the-evaluation-words-with-examples).
4. [Local setup and health check](PROJECT_MASTER_DOCUMENTATION.md#j2-local-installation-steps).

## Beginner-to-Advanced Reading Path

1. [Beginner's Guide: inputs, outputs, and core terms](PROJECT_MASTER_DOCUMENTATION.md#start-here-beginners-guide).
2. [Repository guide and file roles](PROJECT_MASTER_DOCUMENTATION.md#chapter-b-repository-and-file-structure).
3. [Architecture, startup, and request lifecycle](PROJECT_MASTER_DOCUMENTATION.md#chapter-c-system-architecture), then [worked prediction flow](PROJECT_MASTER_DOCUMENTATION.md#chapter-d-complete-application-workflows).
4. [Preprocessing, TF-IDF, models, calibration, and metrics](PROJECT_MASTER_DOCUMENTATION.md#chapter-i-algorithms-and-ml-implementation).
5. [Data and saved artifacts](PROJECT_MASTER_DOCUMENTATION.md#chapter-h-data-models-and-persistence), then [API and frontend](PROJECT_MASTER_DOCUMENTATION.md#chapter-g-api-and-interface-reference) and [source-file explanations](PROJECT_MASTER_DOCUMENTATION.md#chapter-e-file-by-file-and-function-level-reference).
6. [Setup/retraining](PROJECT_MASTER_DOCUMENTATION.md#chapter-j-setup-and-configuration), [testing](PROJECT_MASTER_DOCUMENTATION.md#chapter-k-testing-and-quality-assurance), [deployment](PROJECT_MASTER_DOCUMENTATION.md#chapter-m-deployment-and-operations), and [troubleshooting](PROJECT_MASTER_DOCUMENTATION.md#q6-debugging-scenarios).
7. [Limitations](PROJECT_MASTER_DOCUMENTATION.md#chapter-o-limitations-and-improvement-roadmap), [glossary and commands](PROJECT_MASTER_DOCUMENTATION.md#chapter-p-glossary-and-quick-reference), and [interview preparation](PROJECT_MASTER_DOCUMENTATION.md#chapter-q-ai-knowledge-base-and-interview-preparation).

For a code change, consult the matching source row in the module map, the relevant [Chapter E entry](PROJECT_MASTER_DOCUMENTATION.md#chapter-e-file-by-file-and-function-level-reference), and its workflow/API chapter. Check [coverage and evidence](PROJECT_DOCUMENTATION_COVERAGE.md) before repeating an unverified claim. Update the Markdown when verified behavior changes; only regenerate the PDF if its generation procedure can be established and checked.

---

## What the Project Is

TruthScan is a FastAPI application that classifies a news headline plus article body by patterns learned from labelled examples using:

- A **production five-model calibrated scikit-learn ensemble** (TF-IDF + LR, DT, GBC, NB, Linear SVC).
- An optional **Hugging Face DistilBERT** classifier for `/analyze/deep`.
- A **vanilla HTML/CSS/JS dashboard** served from the same process.

It does **not** fact-check claims or consult live news sources. The 24,353-row evaluation report records labels/counts but not the exact source revision. The README describes a 2016–2017 US news dataset; current downloader behavior also attempts WELFake, so exact corpus provenance is unverified.

---

## Entry Points

| Entry | Path | Role |
|-------|------|------|
| HTTP app object | `app.py` → `app` | FastAPI instance, lifespan, CORS, rate-limit handler, frontend mount |
| Local run | `python app.py` | Uvicorn on `PORT` or 8000 |
| Docker / Render | `Dockerfile`, `render.yaml` | Gunicorn + one Uvicorn worker |
| API routes | `routers/api.py` | `/health`, `/models/info`, `/metrics`, `/analyze`, `/analyze/deep` |
| Ensemble inference | `predictor.py` → `FakeNewsPredictor.predict` | spaCy preprocess, TF-IDF, calibrated probabilities, average ensemble |
| Text cleaning | `preprocessor.py` → `preprocess` | Triple-title weighting, regex clean, spaCy lemmas |
| DistilBERT | `distilbert_predictor.py` | Optional transformer pipeline |
| Frontend | `frontend/index.html`, `frontend/app.js` | Dashboard UI |
| Artifact download | `download_models.py` | GitHub Release `v2.0-calibrated-models` |
| Training (offline) | `evaluate_pipeline.py` → `phase2_calibration.py` | Phase 1 eval then Phase 2 calibration |

---

## Module Map

| Layer | Files | Handbook Chapter |
|-------|-------|-----------------|
| HTTP + middleware | `app.py`, `routers/api.py` | E.1, E.5, G |
| Inference engine | `predictor.py`, `preprocessor.py` | E.3, E.4, I |
| Optional transformer | `distilbert_predictor.py` | E.6, I.6 |
| Configuration | `config.py` | E.2, J |
| Frontend | `frontend/index.html`, `frontend/app.js`, `frontend/style.css` | E.14, E.15 |
| Offline training | `train.py` | E.7 |
| Offline evaluation | `evaluate_pipeline.py`, `phase2_calibration.py` | E.8, E.9, I |
| Offline utilities | `compare_calibration.py`, `generate_held_out_test_set.py` | E.12, E.13 |
| Artifact management | `download_models.py`, `download_data.py` | E.10, E.11, J |
| Tests | `tests/test_api.py`, `tests/test_nasa.py` | K |
| Deployment | `Dockerfile`, `render.yaml`, `.github/workflows/ci.yml` | E.18–E.20, M |

---

## Evidence Status

| Status | Meaning |
|---|---|
| **Verified in current source/config** | Confirmed directly in the checked-out implementation or configuration. |
| **Observed in local report/artifact** | Present in local generated files; not necessarily tracked in Git or reproducible from the current code without the original inputs. |
| **Reported, unverified** | Claimed by README or external model metadata, but not independently supported by repository training/evaluation code. |
| **Unknown** | The repository does not establish the fact, or a live/external system was not checked. |

## Key Facts

| Fact | Value | Source |
|------|-------|--------|
| Ensemble accuracy / Brier score | 98.44% / 0.013835 on 3,653 Phase 2 held-out rows | **Verified in tracked report**; not universal-performance evidence |
| Dataset counts | 24,353 total; 11,107 fake and 13,246 real | **Verified in tracked report**; exact source/revision **unknown** |
| Production models | 5 (LR, DT, GBC, NB, SVC) | **Verified** in `predictor.py::MODEL_KEYS` |
| Calibration selection | isotonic for all 5 | **Verified in tracked report**; current script/report `production_switch` fields differ |
| API version | 2.0.0 | **Verified** in `routers/api.py` |
| OpenAPI document | 3.1.0 with workspace FastAPI 0.141.1 | **Observed** in current `.venv`; dependency is a lower bound, not pinned |
| Server metrics scope | successful `/analyze` requests only | **Verified** in `routers/api.py`; deep requests do not increment server counters |
| Browser retention | last 10 snippets (up to 120 characters) and aggregate stats in `localStorage` | **Verified** in `frontend/app.js` |
| Python target | 3.11 in Docker, CI, and Render config | **Verified** in repository configuration |

---

## Critical Warnings

> **Do not use `models/deprecated_contaminated/` artifacts.** They were serialized before the Phase 1 held-out split was established and are training-set contaminated.

> **`scikit-learn` is pinned to `==1.9.0`.** Use that version when loading the provided serialized artifacts; pickle compatibility across library versions is not guaranteed.

> **Random Forest is not loaded in production.** `predictor.py::MODEL_KEYS` has five models. A large `rfc_calibrated.pkl` is present in the current local workspace, but artifact presence and current host memory limits are environment-dependent; the README cites memory constraints as the reason for exclusion.

> **DistilBERT accuracy (99.97%) is reported but unverified.** The README claims this value, but the repository has no corresponding training/evaluation script. Local and live endpoint availability are also not guaranteed.

> **Do not equate the two metrics displays.** `GET /metrics` counts `/analyze` only; the dashboard stores its own client-side counts for successful ensemble and deep analyses.

---

*Index last updated: 12 October 2026*
