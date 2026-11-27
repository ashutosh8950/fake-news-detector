# TruthScan — Fake News Detector: Project Master Documentation

**Version:** 2.0.0
**Reviewed:** 12 October 2026
**Repository root:** `.` (repository-relative paths are used throughout)
**Remote:** https://github.com/ashutosh8950/fake-news-detector
**Live Demo:** https://truthscan-fake-news-detector.onrender.com
**Primary source of truth:** Checked-out source code/configuration and tracked evaluation JSON reports. The held-out CSV and model binaries are separate generated/downloaded artifacts.

---

## Table of Contents

- [Start Here: Beginner's Guide](#start-here-beginners-guide)
- [Chapter A: Executive Overview](#chapter-a-executive-overview)
- [Chapter B: Repository and File Structure](#chapter-b-repository-and-file-structure)
- [Chapter C: System Architecture](#chapter-c-system-architecture)
- [Chapter D: Complete Application Workflows](#chapter-d-complete-application-workflows)
- [Chapter E: File-by-File and Function-Level Reference](#chapter-e-file-by-file-and-function-level-reference)
- [Chapter F: Technology Stack and Dependencies](#chapter-f-technology-stack-and-dependencies)
- [Chapter G: API and Interface Reference](#chapter-g-api-and-interface-reference)
- [Chapter H: Data Models and Persistence](#chapter-h-data-models-and-persistence)
- [Chapter I: Algorithms and ML Implementation](#chapter-i-algorithms-and-ml-implementation)
- [Chapter J: Setup and Configuration](#chapter-j-setup-and-configuration)
- [Chapter K: Testing and Quality Assurance](#chapter-k-testing-and-quality-assurance)
- [Chapter L: Security, Reliability, and Performance](#chapter-l-security-reliability-and-performance)
- [Chapter M: Deployment and Operations](#chapter-m-deployment-and-operations)
- [Chapter N: Design Decisions and Trade-offs](#chapter-n-design-decisions-and-trade-offs)
- [Chapter O: Limitations and Improvement Roadmap](#chapter-o-limitations-and-improvement-roadmap)
- [Chapter P: Glossary and Quick Reference](#chapter-p-glossary-and-quick-reference)
- [Chapter Q: AI Knowledge Base and Interview Preparation](#chapter-q-ai-knowledge-base-and-interview-preparation)
- [Appendix: Evaluation Data Reference](#appendix-evaluation-data-reference)

## Start Here: Beginner's Guide

### What TruthScan does

TruthScan is a small web application that accepts a news headline and article text and predicts whether the writing resembles examples labelled **fake** or **real** in its training data. The dashboard sends the text to a Python API. The API prepares numeric features, asks five saved classifiers for predictions, combines their probabilities, and returns a label and confidence percentage.

This is a pattern classifier, not a fact-checking service. It does not look up the article, verify its sources, or decide whether a claim is true. An answer of `REAL NEWS` is not independent evidence that the story is true; `FAKE NEWS` is not proof that it is false.

### What goes in and what comes back

- **Input:** an optional headline (up to 500 characters) and required article text (20 to 10,000 characters after surrounding whitespace is stripped).
- **Ensemble output:** `ensemble_label`, `overall_confidence`, each model's `label` and `confidence`, vote counts, processed word count, and `processing_time_ms`.
- **Deep-analysis output:** a separate optional DistilBERT result with `label`, `confidence`, and `processing_time_ms`; it is not part of the five-model ensemble.

For example, a user can paste a headline and article body and receive `REAL NEWS` with `overall_confidence: 68.0`. That number is **illustrative only**, not an observed prediction. It means the ensemble's averaged probability for the selected class was 0.68; it does not mean that independent fact-checkers found the article to be true with 68% certainty.

### The request path at a glance

```mermaid
flowchart LR
  U[Reader enters headline and article] --> W[Browser dashboard]
  W -->|POST /analyze| A[FastAPI validation and rate limit]
  A --> P[Clean text and spaCy lemmatization]
  P --> V[Saved TF-IDF vectorizer]
  V --> M[LR, DT, GBC, NB, and SVC]
  M --> E[Average calibrated P(real)]
  E --> R[JSON label, confidence, and model breakdown]
  R --> W
```

At application startup, `app.py` loads the vectorizer, five classifiers, and Phase 2 report from disk. It warms the spaCy pipeline and then attempts to load DistilBERT. The optional transformer failure is non-fatal; a missing calibrated ensemble artifact is fatal. The app process does **not** download missing model files on startup. Run `python download_models.py` first; Render and Docker configuration run that script during their build steps.

### Machine-learning words in plain language

| Term | Plain-language meaning here |
|---|---|
| **Dataset** | A collection of article examples. The evaluation report describes 24,353 rows: 11,107 labelled fake (`class = 0`) and 13,246 labelled real (`class = 1`). |
| **Sample / label** | One row is one sample; its `title` and `text` are the inputs and `class` is the answer supplied during training/evaluation. |
| **Training set** | The 20,700 rows used to fit the Phase 1/Phase 2 models. The scripts hold out the other 3,653 rows for final evaluation. |
| **Held-out test set** | Rows kept separate from model fitting and used to estimate performance on this particular dataset. It is not a guarantee about future or unrelated news. |
| **Preprocessing** | Consistent cleanup before learning and prediction: the title is repeated three times, text is lowercased and normalized, then spaCy tokenizes and lemmatizes it while removing stopwords and very short tokens. |
| **Token / tokenization** | A token is a piece of text, usually a word; tokenization splits text into those pieces. |
| **Stopword** | A common word such as “the” that this pipeline omits to reduce low-information features. |
| **Lemma / lemmatization** | A normalized dictionary form: for example, “running” can become “run.” This can let related word forms share features. |
| **N-gram** | A sequence of adjacent words. A unigram is one word (“public”); a bigram is two (“public health”). The vectorizer uses both one- and two-word features. |
| **TF-IDF feature** | A number representing how strongly a word or phrase characterizes an article relative to the training corpus. The models need numbers rather than raw sentences. |
| **Classifier** | A learned rule that maps those numeric features to a class prediction. |
| **Probability / threshold** | Each calibrated model estimates `P(class = 1)` (real). A value at least 0.5 predicts real; below 0.5 predicts fake. |
| **Ensemble** | A combination of model outputs. TruthScan averages the five models' `P(real)` values, then applies the same 0.5 threshold. The vote counts are supplementary display fields and do not choose the ensemble label. |

The detailed explanations and equations are in [Chapter I](#chapter-i-algorithms-and-ml-implementation). For a practical code tour, continue to [Chapter B](#chapter-b-repository-and-file-structure), then [Chapter C](#chapter-c-system-architecture), [Chapter D](#chapter-d-complete-application-workflows), and [Chapter J](#chapter-j-setup-and-configuration).

---

## Chapter A: Executive Overview

### A.1 What is TruthScan?

TruthScan is a **fake-news-pattern classification web application** that accepts a headline and article body and returns a `FAKE NEWS` or `REAL NEWS` prediction with a confidence percentage. It uses FastAPI, a TF-IDF text representation, spaCy preprocessing, and five saved scikit-learn classifiers. Here, “fake” and “real” are the training labels; they are not independently verified truth judgements for submitted articles.

### A.2 The Problem It Solves

Misinformation and deliberately fabricated news articles circulate widely on social media and messaging platforms. Readers often lack the time or tools to fact-check articles. TruthScan provides an instant, automated first-pass classification that estimates whether an article resembles patterns found in a large labeled corpus of known fake and real news.

**Important limitation:** TruthScan does *not* fact-check against live external sources. It scores patterns in training text. Individual classifier probabilities are calibrated before averaging; the ensemble's reported Brier score measures its probability error on the held-out data, but the ensemble itself has no separate post-averaging calibration step. Neither score establishes factual certainty on new articles.

### A.3 Intended Users and Use Cases

- Journalists and fact-checkers performing triage on incoming articles.
- Researchers studying automated misinformation detection.
- Developers integrating a fake news signal into news-aggregation or content-moderation pipelines.
- Students learning applied ML pipelines and FastAPI deployment patterns.

### A.4 Major Features (Verified)

| Feature | Status | Evidence |
|---------|--------|----------|
| Five-model TF-IDF ensemble (LR, DT, GBC, NB, SVC) | **Verified** | `predictor.py`, `models/calibrated/` |
| Probability calibration via CalibratedClassifierCV | **Verified** | `phase2_calibration.py`, `phase2_calibration_report.json` |
| spaCy NLP preprocessing with lemmatization | **Verified** | `preprocessor.py` |
| FastAPI REST API with 5 endpoints | **Verified** | `routers/api.py` |
| Rate limiting (slowapi) | **Verified** | `routers/api.py` L86/L115 |
| Input validation with Pydantic V2 | **Verified** | `routers/api.py` L20–L36 |
| Static frontend dashboard (HTML/CSS/JS) | **Verified** | `frontend/` |
| Docker containerization | **Verified** | `Dockerfile` |
| GitHub Actions CI/CD | **Verified** | `.github/workflows/ci.yml` |
| Render.com deployment | **Verified** | `render.yaml` |
| DistilBERT `/analyze/deep` endpoint | **Partially** | `distilbert_predictor.py`; optional, not in `requirements.txt` |
| In-memory API usage metrics | **Verified** | `routers/api.py` L17, L104–L106 |

### A.5 Key Performance Numbers (Observed from `phase2_calibration_report.json`)

| Model | Held-out Accuracy | Brier Score | Calibration Method |
|-------|-------------------|-------------|-------------------|
| Gradient Boosting | 98.66% | 0.011045 | isotonic |
| Decision Tree | 98.66% | 0.011670 | isotonic |
| Linear SVC | 97.84% | 0.016710 | isotonic |
| Logistic Regression | 97.43% | 0.020837 | isotonic |
| Naive Bayes | 94.96% | 0.039742 | isotonic |
| **Five-model Ensemble** | **98.44%** | **0.013835** | Average calibrated probability |

These numbers come from the Phase 2 report's **3,653-row held-out set**, with **20,700 training rows** (24,353 total). They describe this evaluation corpus and split, not expected accuracy on all news. The repository's evaluation report records the counts and results but does not prove the exact provenance/version of the local CSV files.

### A.6 Technology Stack Summary

- **Language:** Python 3.11
- **Web framework:** FastAPI 0.111+, Uvicorn/Gunicorn
- **ML:** scikit-learn 1.9.0, spaCy, joblib
- **Validation:** Pydantic V2 / pydantic-settings
- **Rate limiting:** slowapi
- **Logging:** loguru
- **Optional transformer:** Hugging Face Transformers (DistilBERT)
- **Frontend:** Vanilla HTML/CSS/JavaScript (no build step)
- **Container:** Docker (python:3.11-slim)
- **Hosting:** Render.com free tier

---

## Chapter B: Repository and File Structure

### B.1 Directory Tree

```
FAKE_NEWS_DETECTION/
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI pipeline
├── .venv/                       # Local virtual environment (excluded from analysis)
├── assets/
│   └── dashboard-preview.png    # Dashboard screenshot for README
├── data/
│   ├── Fake.csv                 # Fake-labelled examples (class 0)
│   └── True.csv                 # Real-labelled examples (class 1)
├── evaluation_results/
│   ├── held_out_test_set.csv    # 3,653-row locked evaluation set
│   ├── phase1_evaluation_report.json  # Phase 1 CV + final metrics
│   ├── phase2_calibration_report.json # Phase 2 calibrated model metrics (used by app)
│   └── phase2_comparison.json  # Uncalibrated vs calibrated comparison
├── frontend/
│   ├── index.html               # Single-page dashboard (299 lines)
│   ├── app.js                   # Dashboard JS logic (~26 KB)
│   └── style.css                # Dashboard styles (~37 KB)
├── models/
│   ├── calibrated/              # Production model artifacts
│   │   ├── dt_calibrated.pkl    # Decision Tree (calibrated) — 148 KB
│   │   ├── gbc_calibrated.pkl   # Gradient Boosting (calibrated) — 1.2 MB
│   │   ├── lr_calibrated.pkl    # Logistic Regression (calibrated) — 6 MB
│   │   ├── nb_calibrated.pkl    # Naive Bayes (calibrated) — 24 MB
│   │   ├── rfc_calibrated.pkl   # Random Forest (calibrated) — 89 MB (unused in prod)
│   │   ├── svc_calibrated.pkl   # Linear SVC (calibrated) — 6 MB
│   │   └── vectorizer.pkl       # TF-IDF vectorizer — 6.3 MB
│   └── deprecated_contaminated/ # Deprecated artifacts; do not load for production
├── notebooks/
│   └── FAKE_NEWS_DETECTION.ipynb  # Original exploration notebook (280 KB)
├── routers/
│   └── api.py                   # FastAPI router: all API endpoints
├── tests/
│   ├── __init__.py
│   ├── fixtures/
│   │   └── nasa_test_sample.csv # 283 KB held-out sample for integration test
│   ├── test_api.py              # Unit tests (mocked predictor)
│   └── test_nasa.py             # Integration tests (loads real models)
├── .dockerignore
├── .gitignore
├── app.py                       # FastAPI application entry point
├── compare_calibration.py       # Offline tool: uncalibrated vs calibrated comparison
├── config.py                    # Pydantic Settings configuration
├── distilbert_predictor.py      # Optional DistilBERT predictor
├── Dockerfile                   # Docker build definition
├── download_data.py             # Downloads or creates dataset
├── download_models.py           # Downloads calibrated artifacts from GitHub Releases
├── evaluate_pipeline.py         # Phase 1: CV + held-out evaluation
├── generate_held_out_test_set.py # Utility: regenerate locked split
├── phase2_calibration.py        # Phase 2: calibrates models, saves production artifacts
├── predictor.py                 # Production ensemble predictor (singleton)
├── preprocessor.py              # NLP text cleaning pipeline
├── README.md                    # Product overview and quick-start
├── render.yaml                  # Render.com deployment spec
├── requirements.txt             # Python dependencies
├── train.py                     # Legacy training script (not used in production)
├── PROJECT_MASTER_DOCUMENTATION.md # This handbook
├── PROJECT_DOCUMENTATION_INDEX.md  # Reading guide
├── PROJECT_DOCUMENTATION_COVERAGE.md # Verification record
└── PROJECT_MASTER_DOCUMENTATION.pdf # Existing rendered handbook; may be stale
```

The tree is a guide to the repository, not a claim that every listed data, model, or report artifact is tracked by Git. Large data, model, and generated evaluation files may be local or downloaded and are excluded by ignore rules. Source scripts define how to recreate some artifacts, but a current file's exact historical provenance is not always recorded.

### B.2 Navigation Guide

| Goal | Start Here |
|------|-----------|
| Understand what the app does | `README.md`, Chapter A |
| Change API endpoints or validation | `routers/api.py` |
| Change prediction logic | `predictor.py`, `preprocessor.py` |
| Retrain or recalibrate models | `evaluate_pipeline.py` → `phase2_calibration.py` |
| Change the frontend UI | `frontend/index.html`, `frontend/app.js`, `frontend/style.css` |
| Add a new environment variable | `config.py` |
| Debug model loading | `predictor.py::FakeNewsPredictor.load`, `download_models.py` |
| Understand model accuracy | `evaluation_results/phase2_calibration_report.json` |
| Deploy via Docker | `Dockerfile` |
| Deploy to Render | `render.yaml` |

---

## Chapter C: System Architecture

### C.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT BROWSER                       │
│            (HTML/CSS/JS served from /static)                │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP
┌───────────────────────────▼─────────────────────────────────┐
│                     FastAPI Application                      │
│                      (app.py + CORS)                         │
│                                                              │
│  ┌─────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │ SlowAPI     │  │  APIRouter     │  │ Static Files     │  │
│  │ Rate Limiter│  │ (routers/api)  │  │ (/static)        │  │
│  └─────────────┘  └───────┬────────┘  └──────────────────┘  │
│                           │                                  │
│              ┌────────────▼────────────┐                     │
│              │   FakeNewsPredictor      │                     │
│              │   (predictor.py)         │                     │
│              │   ┌──────────────────┐  │                     │
│              │   │ TF-IDF Vectorizer│  │                     │
│              │   │ (vectorizer.pkl) │  │                     │
│              │   └──────────────────┘  │                     │
│              │   ┌────────────────────┐│                     │
│              │   │ 5 Calibrated Models││  (lr, dt, gbc,      │
│              │   │  (*.pkl)           ││   nb, svc)          │
│              │   └────────────────────┘│                     │
│              └────────────┬────────────┘                     │
│                           │                                  │
│  ┌────────────────────────▼────────────────────────────┐    │
│  │              preprocessor.py                          │    │
│  │   clean_text → lemmatize (spaCy en_core_web_sm)      │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  DistilBertPredictor (distilbert_predictor.py)       │    │
│  │  Optional — loads from HuggingFace Hub               │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
              │ (artifact download)
┌─────────────▼──────────────────┐
│   GitHub Releases              │
│   (v2.0-calibrated-models)     │
│   *.pkl + calibration report   │
└────────────────────────────────┘
```

### C.2 Component Responsibilities

| Component | File(s) | Responsibility |
|-----------|---------|---------------|
| FastAPI App | `app.py` | Application factory, lifespan hooks, CORS, middleware, static file serving |
| API Router | `routers/api.py` | HTTP endpoint definitions, request/response schemas, rate limiting, metrics counters |
| Predictor | `predictor.py` | Singleton ensemble predictor; loads and holds model artifacts in memory |
| Preprocessor | `preprocessor.py` | Text normalization, cleaning, spaCy lemmatization |
| DistilBERT predictor | `distilbert_predictor.py` | Optional Transformer-based predictor; optional load from HuggingFace Hub |
| Configuration | `config.py` | Environment-aware settings via Pydantic |
| Frontend | `frontend/` | Browser-rendered dashboard; calls REST API via `fetch` |

### C.3 Data Flow Diagram (Analysis Request)

```
Browser
  │
  POST /analyze  {title, text}
  │
  ▼
SlowAPIMiddleware  →  rate limit check (10/min per IP)
  │
  ▼
routers/api.py::analyze()
  │   Pydantic validation (AnalyzeRequest)
  │   - text ≥ 20 chars, ≤ 10,000 chars
  │   - title optional, ≤ 500 chars
  │   - whitespace stripped
  ▼
predictor.predict(title, text)
  │
  ├─► preprocessor.preprocess(title, text)
  │     combined = "{title} {title} {title} {text}"
  │     clean_text() → lowercase, remove URLs/HTML/punctuation/numbers
  │     lemmatize_text() → spaCy tokenize, filter stop words, lemmatize
  │     returns: cleaned string
  │
  ├─► vectorizer.transform([processed])
  │     TF-IDF bigram vectorization (max 150,000 features)
  │     returns: sparse matrix (1 × vocab_size)
  │
  ├─► for each model in [lr, dt, gbc, nb, svc]:
  │     model.predict_proba(vectorized) → [P(class=0), P(class=1)]
  │     P(class=1) = probability the article is REAL
  │     confidence = max(P, 1-P) × 100
  │
  ├─► ensemble_probability = mean([P1_lr, P1_dt, P1_gbc, P1_nb, P1_svc])
  │     ensemble_is_fake = ensemble_probability < 0.5
  │     overall_confidence = calibrated ensemble confidence
  │
  └─► return {ensemble_is_fake, ensemble_label, overall_confidence,
              fake_votes, real_votes, total_models, models{}, processed_length}
  │
  ▼
routers/api.py::analyze()
  ├─► adds processing_time_ms
  ├─► updates _metrics counters
  ├─► logs result
  └─► returns JSON response
```

### C.4 Startup and model-loading sequence

```
uvicorn/gunicorn starts app:app
  │
  ├─► FastAPI.__init__ (title, version, lifespan)
  ├─► Middlewares registered (SlowAPI, CORS)
  ├─► Routes included from routers/api.py
  ├─► lifespan() begins
  │     ├── predictor.load()      ← loads vectorizer + 5 classifiers + Phase 2 JSON report
  │     ├── preprocess("warmup", ...) ← pre-warms spaCy model
  │     ├── distilbert_predictor.load() ← optional, non-fatal
  │     └── logs model accuracies + server URL
  └─► app begins serving already-registered routes
```

The `/static` mount and `/` route are registered when `app.py` is imported, before lifespan startup. Model downloads are a separate build/setup step in `render.yaml` and `Dockerfile`; the app's lifespan does not call `download_models.py`. Missing required ensemble files cause startup to fail. DistilBERT load failure only disables `/analyze/deep`.

### C.5 Model Training and Calibration Pipeline (Offline)

```
data/Fake.csv + data/True.csv  (24,353 rows total)
  │
  ▼
evaluate_pipeline.py
  ├── Preprocessing (preprocess all rows)
  ├── Stratified 15% hold-out split → evaluation_results/held_out_test_set.csv (3,653 rows)
  ├── 5-fold stratified CV on remaining 20,700 rows
  ├── Final held-out evaluation (6 models + majority-vote ensemble)
  └── → phase1_evaluation_report.json
  │
  ▼
phase2_calibration.py
  ├── Loads Phase 1 held-out split (immutable)
  ├── Fits fresh TF-IDF on 20,700 training rows
  ├── For each of 5 models (rfc excluded):
  │     ├── choose_calibration_method() → isotonic vs sigmoid via Brier score
  │     └── CalibratedClassifierCV.fit() → *.pkl → models/calibrated/
  ├── Saves vectorizer.pkl → models/calibrated/
  ├── Measures ensemble on held-out → 98.44% accuracy
  └── → phase2_calibration_report.json
```

---

## Chapter D: Complete Application Workflows

### D.1 Standard Analysis Request (POST /analyze)

**Trigger:** User pastes a news headline and article text into the dashboard and clicks "Analyze".

**Request:**
```json
{
  "title": "NASA Launches New Mars Rover",
  "text": "NASA successfully launched its latest Mars rover on Monday..."
}
```

**Step-by-step execution:**

1. **Rate limit check** (`SlowAPIMiddleware`): The client's IP is checked against the 10-requests/minute limit stored in slowapi's in-memory store. If exceeded, returns HTTP 429 with a structured JSON error.

2. **Pydantic validation** (`AnalyzeRequest`): Title is optional (defaults to `""`), text is required (20–10,000 chars). Both are whitespace-stripped before validators run.

3. **Model availability check**: If `predictor.loaded` is False (models still loading), returns HTTP 503.

4. **Preprocessing** (`preprocess(title, text)`):
   - Combines input as `"{title} {title} {title} {text}"` (triple-weight on title)
   - `clean_text()`: lowercases, strips URLs, HTML tags, brackets, punctuation, digits, special chars, normalizes whitespace
   - `lemmatize_text()`: passes through spaCy `en_core_web_sm` with parser/NER disabled; retains only lemmatized tokens that are non-stop-words and length > 2

5. **Vectorization**: `vectorizer.transform([processed])` converts the cleaned string to a sparse TF-IDF vector (bigrams, up to 150,000 features, sublinear TF, min_df=2, max_df=0.95).

6. **Per-model prediction**: For each model key in `["lr", "dt", "gbc", "nb", "svc"]`:
   - Calls `model.predict_proba(vectorized)[0]` → `[P(fake), P(real)]`
   - `P(class=1)` is the calibrated probability the article is real
   - Threshold at 0.5: `prediction = 1 (REAL) if P(class=1) >= 0.5`
   - `confidence = P(class=1) if prediction==1 else 1.0 - P(class=1)` (i.e., probability of the predicted class)

7. **Ensemble**: `ensemble_probability = mean([P1_lr, P1_dt, P1_gbc, P1_nb, P1_svc])`
   - `ensemble_is_fake = ensemble_probability < 0.5`
   - `overall_confidence = ensemble_probability * 100` if real, else `(1.0 - ensemble_probability) * 100`
   - Vote counts computed for display: `fake_votes = count of models where is_fake == True`

8. **Response assembly**: `processing_time_ms` added; `_metrics` counters incremented; result logged.

**Success response:**

The values in this response are **illustrative**, not a captured request or a claim about what the sample headline actually predicts.

```json
{
  "ensemble_is_fake": false,
  "ensemble_label": "REAL NEWS",
  "overall_confidence": 94.3,
  "fake_votes": 1,
  "real_votes": 4,
  "total_models": 5,
  "models": {
    "lr": {"name": "Logistic Regression", "label": "Real", "is_fake": false, "confidence": 97.5},
    "dt": {"name": "Decision Tree", "label": "Real", "is_fake": false, "confidence": 99.1},
    "gbc": {"name": "Gradient Boosting", "label": "Real", "is_fake": false, "confidence": 98.7},
    "nb": {"name": "Naive Bayes", "label": "Fake", "is_fake": true, "confidence": 55.2},
    "svc": {"name": "Linear SVC", "label": "Real", "is_fake": false, "confidence": 96.3}
  },
  "processed_length": 42,
  "processing_time_ms": 18.3
}
```

### D.2 Deep Analysis Request (POST /analyze/deep)

Similar to D.1 but uses `distilbert_predictor.predict_distilbert()` instead of the ensemble. Rate-limited to 5/minute.

1. Input validation (same `AnalyzeRequest` schema).
2. Check `distilbert_predictor.loaded`; if False → HTTP 503.
3. DistilBERT receives `"{title} {title} {title} {text}"` (triple-title, same weighting as ensemble).
4. `pipeline("text-classification")` with `truncation=True, max_length=512`.
5. Label mapping: `LABEL_0` → `"FAKE"`, `LABEL_1` → `"REAL"`.
6. Returns `{label, confidence, processing_time_ms}`.

**Note:** DistilBERT is *not* included in `requirements.txt`. It must be installed separately (`transformers`, `torch`). The endpoint returns HTTP 503 if the model is unavailable.

### D.3 Application Startup

See C.4. The key behavior is: **if calibrated model artifacts are missing, the server fails at startup** with a descriptive `RuntimeError`. This is a deliberate fail-fast design to prevent silent mis-prediction.

### D.4 Frontend Dashboard Interaction

The frontend (`frontend/index.html` + `frontend/app.js`) is a single-page application served by FastAPI. It calls `GET /health` on page load and every 30 seconds, calls `GET /models/info` for model metrics, and posts analysis requests to `/analyze` or `/analyze/deep`. It does **not** call `GET /metrics`.

On success, the browser renders the verdict, confidence, processing time, and per-model result. It also stores aggregate analysis counts and up to 10 recent entries in the browser's `localStorage`. Each entry includes a timestamp, mode, label, confidence, and the first 120 characters of the headline or article text. This data remains in that browser profile until cleared using **Clear history** or the browser's site-data controls; it is not stored in a project database. Do not paste sensitive text into the demo if retaining a snippet locally is unacceptable. The page displays friendly messages for validation, rate-limit, unavailable-model, server, and network errors.

### D.5 Model Download at Deploy Time

During Docker build or Render build: `python download_models.py` runs and downloads 6 `.pkl` files and the calibration JSON report from GitHub Releases (`v2.0-calibrated-models`). A `.download_lock` file prevents concurrent downloads from multiple workers.

---

## Chapter E: File-by-File and Function-Level Reference

### E.1 `app.py` — Application Entry Point

**Path:** `app.py`
**Responsibility:** Creates and configures the FastAPI application instance, registers middleware, includes the API router, serves the frontend, and defines the application lifespan (startup/shutdown).

**Key sections:**

#### `lifespan(app)` (Lines 30–67)
An `@asynccontextmanager` used as FastAPI's `lifespan` parameter. Runs startup tasks before `yield` and shutdown tasks after.

Startup tasks in order:
1. `predictor.load()` — loads 5 calibrated models + vectorizer + calibration metadata. **Fatal if files are missing** (raises `RuntimeError`).
2. `preprocess("warmup", "warmup text for spacy pre-warming")` — forces spaCy to load `en_core_web_sm` into memory before the first real request, eliminating 4-second first-request latency. Non-fatal if it fails.
3. `distilbert_predictor.load()` — attempts to download and load DistilBERT from HuggingFace Hub. Non-fatal; logs a warning on failure.
4. Logs model accuracy table and server URL.

#### `rate_limit_exception_handler(request, exc)` (Lines 80–107)
Custom handler for `RateLimitExceeded`. Extracts the `Retry-After` header from slowapi's default response and wraps it in a structured JSON body with `error`, `message`, and `retry_after_seconds` fields. Returns HTTP 429.

#### `global_exception_handler(request, exc)` (Lines 113–125)
Catches all unhandled exceptions. Generates a UUID `request_id`, logs the full traceback, and returns a sanitized JSON error (HTTP 500) with the request ID for correlation. Does **not** expose internal error details to the client.

#### CORS configuration (Lines 128–150)
Reads `ENVIRONMENT` env var. In `development`/`local`/`test` environments, allows `localhost:8000` in addition to the production origin. The `ALLOWED_ORIGINS` env var can override everything. Allows all methods and headers.

#### Frontend serving (Lines 155–167)
Mounts `frontend/` as `/static`. Registers `GET /` as a route that reads and returns `frontend/index.html`. Falls back to 404 HTML if index doesn't exist.

---

### E.2 `config.py` — Configuration

**Path:** `config.py`
**Lines:** 12

Defines a Pydantic `Settings` class that reads from environment variables (and optionally `.env`).

| Field | Default | Purpose |
|-------|---------|---------|
| `app_name` | `"Fake News Detection API"` | Used as FastAPI `title` |
| `environment` | `"development"` | Not currently used in logic (CORS uses raw `os.environ`) |
| `models_dir` | `"models"` | Base directory for model artifacts |
| `data_dir` | `"data"` | Base directory for CSV datasets |

`settings = Settings()` is a module-level singleton imported by `app.py`, `predictor.py`, and `train.py`.

---

### E.3 `preprocessor.py` — NLP Text Pipeline

**Path:** `preprocessor.py`
**Lines:** 51

This module is the NLP preprocessing layer shared between training and inference. It is imported by `predictor.py`, `train.py`, `evaluate_pipeline.py`, `phase2_calibration.py`, and `compare_calibration.py`.

```
Module-level initialization:
  nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
```
The model is loaded once at import time (module-level). The `parser` and `ner` components are disabled for performance since only tokenization, lemmatization, and stop word detection are needed.

#### `clean_text(text: str) -> str`
Applies a sequence of regex transformations:
1. Lowercase
2. Remove `[bracketed content]`
3. Remove URLs (`http://`, `https://`, `www.`)
4. Remove HTML tags (`<...>`)
5. Replace punctuation with spaces
6. Replace newlines with spaces
7. Remove words containing digits (e.g., `19th`, `covid19`)
8. Remove standalone numbers
9. Remove remaining non-alphabetic characters
10. Replace non-word characters with spaces
11. Collapse multiple whitespaces

Returns an empty string if input is not a string.

#### `lemmatize_text(text: str) -> str`
Passes `text` through spaCy's pipeline. For each token:
- Skip if it is a stop word (`token.is_stop`)
- Skip if the token text has length ≤ 2
- Retain the lemma (`token.lemma_`)

Returns the space-joined lemmas.

#### `preprocess(title: str = "", text: str = "") -> str`
The entry point called by all callers.
```
combined = f"{title} {title} {title} {text}"  # 3× title weight
cleaned = clean_text(combined)
return lemmatize_text(cleaned)
```

**Design note:** The preprocessor repeats the title three times during both training and inference, so the same transformation is used on both paths. This does not guarantee an exact threefold TF-IDF weight or prove that repetition improves evaluation results.

---

### E.4 `predictor.py` — Ensemble Prediction Engine

**Path:** `predictor.py`
**Lines:** 184

The production inference component. It loads and holds all model artifacts in memory and provides a `predict()` method.

#### Module-level constants
- `MODELS_DIR = "models/calibrated"` — path to calibrated `.pkl` files
- `PHASE2_REPORT_PATH = "evaluation_results/phase2_calibration_report.json"` — metadata source
- `MODEL_KEYS = ["lr", "dt", "gbc", "nb", "svc"]` — the 5 production models (Random Forest excluded)
- `MODEL_NAMES` — display name mapping

#### `_memory_usage() -> str`
Reads `/proc/self/status` to get RSS memory without adding a dependency. Falls back to `"RSS: unavailable"` on Windows and macOS. Used only for startup logging.

#### `_log_load_checkpoint(message: str) -> None`
Logs a timestamped message with current RSS memory. Called before and after loading each artifact to aid diagnosing slow startup or OOM issues.

#### `FakeNewsPredictor` class

**`__init__`**: Sets `vectorizer`, `models` (dict), `meta` (dict), `loaded = False`.

**`load()`** (Lines 58–119):
1. Checks `models/calibrated/vectorizer.pkl` exists; raises `FileNotFoundError` if not.
2. Loads `vectorizer.pkl` with `joblib.load`.
3. Loads each of 5 model `.pkl` files in `MODEL_KEYS` order.
4. Loads `phase2_calibration_report.json`.
5. Populates `self.meta` for each model: `name`, `accuracy` (percentage), `brier_score`, `calibration_method`.
6. Populates `self.meta["ensemble"]` if the report contains ensemble data.
7. Sets `self.loaded = True`.

**`predict(title="", text="") -> Dict`** (Lines 121–176):
- Validates `self.loaded`.
- Calls `preprocess(title, text)` → `vectorizer.transform([processed])`.
- For each model: `predict_proba()` → `P(class=1)` → binary label → confidence.
- Computes `ensemble_probability = mean(all P(class=1))`.
- Builds response dict.

Key insight: The production predictor uses **average calibrated probability** for the ensemble, not majority vote. This is more robust than counting votes and preserves confidence resolution.

**`get_model_info() -> Dict`**: Returns `self.meta`. Called by `GET /models/info`.

**`predictor = FakeNewsPredictor()`**: Module-level singleton. Loaded by the application lifespan.

---

### E.5 `routers/api.py` — HTTP API Router

**Path:** `routers/api.py`
**Lines:** 142

Defines all REST endpoints using `APIRouter`. Also defines Pydantic schemas and the slowapi `Limiter`.

#### Schemas

**`AnalyzeRequest`** (Lines 20–36):
```python
text:  str  (required, max_length=10000, min_length=20)
title: str  (optional, default="", max_length=500)
```
Validators:
- `strip_whitespace`: Strips leading/trailing whitespace from both fields (mode `before`).
- `check_length`: Rejects `text` shorter than 20 chars after stripping.

Validation errors return HTTP 422 (Pydantic's default unprocessable entity response).

**`HealthResponse`**, **`MetricsResponse`**: Typed response schemas for the two monitoring endpoints.

#### Metrics counter (`_metrics`)
```python
_metrics = {"total": 0, "fake": 0, "real": 0, "confidence_sum": 0.0}
```
Process-local in-memory counters. Reset on application restart. Not thread-safe at extreme concurrency (no lock), but the current Gunicorn setup uses 1 worker so races are not an issue.

#### `GET /health`
Returns `{status, models_loaded, uptime_seconds, api_version}`. Does not require model to be loaded. Uses `predictor.loaded` to report readiness.

#### `GET /models/info`
Returns `predictor.meta` dict (per-model name, accuracy, brier_score, calibration_method). Returns HTTP 503 if models not loaded.

#### `GET /metrics`
Returns aggregated successful `/analyze` counts, fake/real counts, average confidence, uptime, models_loaded, and api_version. The `/analyze/deep` handler does not increment these counters. Average confidence is computed as `confidence_sum / total` when `total > 0`, else 0.

#### `POST /analyze`
Rate limit: 10/minute per IP (slowapi key: remote address).
- Validates `AnalyzeRequest`.
- Calls `predictor.predict(title, text)`.
- Adds `processing_time_ms`.
- Updates `_metrics`.
- Logs result.
- Returns prediction dict.

#### `POST /analyze/deep`
Rate limit: 5/minute per IP.
- Same input schema.
- Calls `distilbert_predictor.predict_distilbert(title, text)`.
- Returns `{label, confidence, processing_time_ms}`.
- Returns HTTP 503 if DistilBERT not loaded.

---

### E.6 `distilbert_predictor.py` — Optional DistilBERT Predictor

**Path:** `distilbert_predictor.py`
**Lines:** 54

**Important:** The `transformers` library is *not* in `requirements.txt`. This module gracefully handles `ImportError`.

#### Module-level
```python
os.environ["TOKENIZERS_PARALLELISM"] = "false"
```
Prevents HuggingFace tokenizer fork warnings when used with Gunicorn.

Tries to import `pipeline` from `transformers`. Sets `TRANSFORMERS_AVAILABLE` flag.

#### `DistilBertPredictor` class

**`load()`**: If `TRANSFORMERS_AVAILABLE`, loads `pipeline("text-classification", model="GuptaAshutosh/truthscan-fake-news-distilbert", device=-1)`. CPU-only (`device=-1`). Non-fatal — sets `self.loaded = False` on failure.

**`predict_distilbert(title, text)`**:
- Does NOT use `preprocessor.preprocess()`. Instead concatenates: `f"{title} {title} {title} {text}"` (raw, not cleaned).
- Calls `self.classifier(processed, truncation=True, max_length=512)`.
- Maps label: `LABEL_0` → `"FAKE"`, `LABEL_1` → `"REAL"`.
- Returns `{"label": ..., "confidence": round(score * 100, 1)}`.

**Design note:** DistilBERT does *not* apply the same text cleaning as the ensemble. It relies on the transformer's tokenizer and attention mechanisms to handle raw text. This is appropriate because BERT-family models are pre-trained on natural language and do not benefit from aggressive regex cleaning.

**`distilbert_predictor = DistilBertPredictor()`**: Module-level singleton.

---

### E.7 `train.py` — Legacy Training Script

**Path:** `train.py`
**Lines:** 169

**Status:** Not used by the production server. This script trains the original (uncalibrated) 6-model set. The production artifacts come from `phase2_calibration.py`.

#### `ensure_data()`
Checks for `data/Fake.csv` and `data/True.csv`. If absent, tries `download_full_dataset()` then falls back to `create_sample_data()`.

#### `load_data()`
Reads both CSVs, labels them (`Fake.csv` = 0, `True.csv` = 1), copies the last 10 rows of each class into variables named as test rows, then concatenates and shuffles the remaining rows. Those copied rows are returned but are not used by `train()` for evaluation. Missing title/text values are filled with empty strings.

#### `train()`
1. Applies `preprocess()` to all rows (row-by-row with `.iterrows()`).
2. Uses a stratified 75%/25% split of the remaining rows for this script's own evaluation.
3. Fits TF-IDF vectorizer (same configuration as Phase 2).
4. Trains and evaluates all 6 models.
5. Saves each model as `models/{key}_model.pkl` and vectorizer as `models/vectorizer.pkl`.
6. Saves metadata as `models/model_meta.json`.

**Note:** This legacy path writes `models/{key}_model.pkl`, `models/vectorizer.pkl`, and `models/model_meta.json`. The production predictor loads only `models/calibrated/{lr,dt,gbc,nb,svc}_calibrated.pkl`, `vectorizer.pkl`, and `evaluation_results/phase2_calibration_report.json`; running `train.py` alone does not create that production set. Random Forest is present in the legacy path and on disk locally, but is excluded from the five-model production predictor.

---

### E.8 `evaluate_pipeline.py` — Phase 1 Rigorous Evaluation

**Path:** `evaluate_pipeline.py`
**Lines:** 361

A standalone evaluation script that does NOT use `train.py`'s trained models. It fits fresh models from scratch in each cross-validation fold and for the final held-out evaluation.

#### Constants
- `RANDOM_STATE = 42`
- `HELD_OUT_FRACTION = 0.15` → 15% of data becomes the permanent test set
- `CV_FOLDS = 5`
- `NEAR_DUPLICATE_THRESHOLD = 0.90`
- `NEAR_DUPLICATE_SAMPLE_SIZE = 500` (per class)

#### Key functions

**`build_models()`**: Creates fresh scikit-learn model instances with the same hyperparameters as `train.py` but as fresh objects (no shared state from training).

**`load_dataset()`**: Reads `data/Fake.csv` and `data/True.csv`, labels them, concatenates. Creates a `combined_text` column (title + text) used by duplicate checks.

**`exact_cross_class_duplicates(data)`**: Normalizes all text, finds articles appearing in both the fake and real class. Zero found in the actual dataset — no label contamination detected.

**`sample_near_duplicates(data)`**: Samples 500 articles per class, sorts by text length, uses a sliding window of 5 for pairwise `difflib.SequenceMatcher` comparison. Zero near-duplicate pairs found in the actual run (rate 0.0%).

**`vectorize(train_text, test_text)`**: Fits a fresh TF-IDF vectorizer (same config as `train.py`) on train, transforms both.

**`metric_record(y_true, y_pred)`**: Computes accuracy, weighted precision/recall/F1, confusion matrix.

**`run_cross_validation(texts, labels)`**: Runs 5-fold stratified CV. Fits a fresh TF-IDF vectorizer in each fold (correct — no data leakage from vectorizer fitting on the full dataset).

**`majority_vote(predictions)`**: Six-model majority vote with tie-break rule: 3-3 ties go to class 1 (real). Counted 21 ties in the actual held-out evaluation.

**`evaluate_final(...)`**: Fits all models on all non-held-out rows, evaluates on the locked held-out set.

**`main()`**: Orchestrates all 6 steps, saves results to `evaluation_results/phase1_evaluation_report.json`.

---

### E.9 `phase2_calibration.py` — Production Calibration

**Path:** `phase2_calibration.py`
**Lines:** 267

Produces the production model artifacts used by the application.

#### `load_phase1_data()`
Reconstructs the exact Phase 1 train/held-out split by:
1. Loading all data from `data/Fake.csv` and `data/True.csv`.
2. Loading `held_out_test_set.csv`.
3. Matching held-out rows by (title, text, class) tuple membership.
4. **Validates exact row counts**: expects 20,700 training + 3,653 held-out. Raises `ValueError` if counts don't match.

This design ensures Phase 2 calibration never contaminates the held-out test set.

#### `choose_calibration_method(estimator, train_vectors, labels)`
For each candidate method in `["sigmoid", "isotonic"]`:
1. Splits training data 80/20 (inner split).
2. Fits `CalibratedClassifierCV` with 5-fold CV on the 80%.
3. Evaluates Brier score on the 20%.
4. Returns the method with the **lower Brier score** (better calibration).

**Result:** All 5 production models selected `isotonic` calibration (observed from `phase2_calibration_report.json`).

**Reproduction caveat:** The checked-out script currently initializes the generated report's `production_switch` field to `false`; the local report currently says `true`. `predictor.py` does not read this field. Treat the report values as observed evaluation results, but do not assume rerunning the current script will reproduce every metadata field unchanged.

#### `metrics_for_model(labels, predictions, probabilities)`
Computes accuracy, Brier score, and a 10-bin reliability/calibration curve using `sklearn.calibration.calibration_curve`.

#### `main()`
1. Loads and preprocesses 20,700 training + 3,653 held-out rows.
2. Fits TF-IDF on training data, saves `models/calibrated/vectorizer.pkl`.
3. For each of 5 models: selects calibration method, fits calibrated model, saves `*_calibrated.pkl`.
4. Computes ensemble on held-out set.
5. Saves `evaluation_results/phase2_calibration_report.json`.

---

### E.10 `download_models.py` — Artifact Download Script

**Path:** `download_models.py`
**Lines:** 116

Downloads pre-trained calibrated artifacts from GitHub Releases so the server can run without local training. The application does not invoke this downloader automatically at startup.

**GitHub Release URL:** `https://github.com/ashutosh8950/fake-news-detector/releases/download/v2.0-calibrated-models`

#### `models_are_valid(models_dir, metadata_dir)`
Returns `True` only if:
- `vectorizer.pkl` exists and is larger than 1 MB
- Each of the five calibrated classifier files and the vectorizer listed in `MODEL_FILES` exists
- `phase2_calibration_report.json` exists

#### `download_models(models_dir, metadata_dir)`
- Checks `models_are_valid()` first; skips download if already valid.
- Creates a `.download_lock` file to prevent concurrent downloads (relevant for multi-worker deployments).
- Downloads each file with `requests.get(..., stream=True, timeout=300)`.
- Writes files chunk by chunk (`chunk_size=8192`).
- Removes lock file in `finally` block.

---

### E.11 `download_data.py` — Dataset Acquisition Script

**Path:** `download_data.py`
**Lines:** 111

Not used by the production server. Used when re-training from scratch.

**Downloader behavior:** first attempts the Hugging Face `GonzaloA/fake_news` CSV (WELFake) and writes rows labelled 0/1 to `data/Fake.csv` and `data/True.csv`. If that download fails, `train.py` can fall back to 10 embedded examples per class. The script also names the Kaggle “Fake and Real News” dataset as a manual alternative. These paths do **not** prove that the 24,353-row corpus in the existing evaluation report came from a particular source or exact dataset revision; provenance is not stored alongside that report.

#### `create_sample_data()`
Creates minimal demo data from the hard-coded `SAMPLE_FAKE` and `SAMPLE_TRUE` tuples. Output is not suitable for training a production model.

#### `download_full_dataset()`
Attempts to download from HuggingFace. Parses the CSV, splits by `label` column (0=fake, 1=real), saves `data/Fake.csv` and `data/True.csv`.

---

### E.12 `compare_calibration.py` — Comparison Utility

**Path:** `compare_calibration.py`
**Lines:** 161

An offline diagnostic tool comparing uncalibrated models (from `train.py`) against calibrated models (from `phase2_calibration.py`). Not used by the server.

Loads both sets of artifacts, applies both to the Phase 1 held-out set, computes accuracy and Brier scores, and saves a comparison report to `evaluation_results/phase2_comparison.json`.

---

### E.13 `generate_held_out_test_set.py` — Split Regeneration Utility

**Path:** `generate_held_out_test_set.py`
**Lines:** 28

A thin wrapper around `evaluate_pipeline.load_dataset()` that regenerates the Phase 1 held-out split CSV without running the full evaluation. Useful when the held-out CSV has been deleted but you need Phase 2 calibration.

---

### E.14 `frontend/index.html` — Dashboard HTML

**Path:** `frontend/index.html`
**Lines:** 299

Single-page application. Loads styles from `/static/style.css` and scripts from `/static/app.js`. Uses hash anchors for section navigation (`#dashboard`, `#analyze`, `#models`). References:
- Google Fonts (Inter, JetBrains Mono, Space Grotesk, Syne) via CDN.
- Internal canvas (`#particles`) for animated background.
- Live status display (`#status-pill`, `#status-text`, `#status-dot`).
- Dashboard statistics are held in browser `localStorage`; the frontend does not poll `GET /metrics`.
- Analysis form (`#analyze-form`) posting to `/analyze`.
- Model cards grid (`#models`).
- Dark/light theme toggle (`#theme-toggle`).

---

### E.15 `frontend/app.js` — Dashboard JavaScript

**Path:** `frontend/app.js`
**~26 KB / ~1,000 lines**

Handles all client-side logic:
- Particle canvas animation.
- API health polling (every 30 seconds).
- Metrics loading and stat counter animation.
- Form submission and result rendering.
- Deep analysis mode toggle.
- Model cards with accuracy bars.
- Error handling (429 rate-limit friendly message, 503, 500).
- Theme persistence via `localStorage`.
- Responsive navigation (mobile hamburger menu).

---

### E.16 `tests/test_api.py` — Unit Tests

**Path:** `tests/test_api.py`
**Lines:** 86

Uses `pytest` + FastAPI's `TestClient` (backed by `httpx`). Mocks `predictor.load`, `predictor.loaded`, `predictor.meta`, `predictor.predict`, and `preprocess` using `unittest.mock.patch`.

Tests:
1. `test_health` — verifies `/health` returns 200, `status=="ok"`, `models_loaded==True`.
2. `test_models_info` — verifies `/models/info` returns 200 with expected keys.
3. `test_analyze_real_news` — posts real news payload, mocked predict returns REAL NEWS, verifies response.
4. `test_analyze_fake_news` — posts fake news payload, mocked predict returns FAKE NEWS, verifies response.
5. `test_frontend_serving` — verifies `GET /` returns HTML containing "TruthScan".

**Limitation:** These tests use fully mocked predictors. They verify HTTP routing and schema behavior but not the correctness of model predictions.

---

### E.17 `tests/test_nasa.py` — Integration Tests

**Path:** `tests/test_nasa.py`
**Lines:** 38

Module-scoped `TestClient` that triggers the full application lifespan (loading real models). Loads 2 fake and 2 real articles from `tests/fixtures/nasa_test_sample.csv`.

For each sample:
- Posts to `/analyze` with real title and text.
- Asserts HTTP 200.
- Asserts `ensemble_is_fake` matches the expected class.
- Asserts `overall_confidence > 50.0`.
- Asserts `fake_votes + real_votes == total_models`.
- Asserts `processing_time_ms < 2000`.
- Asserts `processed_length > 10`.

**These tests load real production models.** They were observed passing in the test run noted in the coverage record.

---

### E.18 `Dockerfile` — Container Build

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    python -m spacy download en_core_web_sm
COPY . .
EXPOSE 8000
RUN python download_models.py
CMD ["gunicorn", "app:app", "--workers", "1", "--worker-class",
     "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "120"]
```

Key decisions:
- `python:3.11-slim` — minimal base image.
- `download_models.py` runs as a `RUN` step (build-time download). Models are baked into the final image layer.
- 1 Gunicorn worker is configured. The memory limit/reasonableness of that count depends on the current host plan and was not measured in this review.
- 120s timeout — needed because model loading and spaCy warm-up take tens of seconds on first start.

---

### E.19 `render.yaml` — Render.com Deployment

```yaml
services:
  - type: web
    name: truthscan-fake-news-detector
    env: python
    buildCommand: |
      pip install -r requirements.txt
      python -m spacy download en_core_web_sm
      python download_models.py
    startCommand: gunicorn app:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120
    plan: free
    envVars:
      - key: PYTHON_VERSION
        value: "3.11.0"
```

Build command downloads models at deploy time. Models are NOT baked into a container in the Render deployment — they are downloaded fresh each build to `models/calibrated/` on Render's ephemeral build filesystem. `$PORT` is provided by Render.

---

### E.20 `.github/workflows/ci.yml` — CI Pipeline

Triggers on push or PR to `main`. Steps:
1. Checkout code.
2. Set up Python 3.11.
3. Install dependencies + spaCy model.
4. Download calibrated models.
5. Run `pytest -v tests/` (all tests, including integration tests that load real models).

---

## Chapter F: Technology Stack and Dependencies

### F.1 Python Dependencies (`requirements.txt`)

| Package | Version | Role |
|---------|---------|------|
| `fastapi` | ≥0.111.0 | Web framework and request handling |
| `uvicorn[standard]` | ≥0.30.0 | ASGI server (development/direct use) |
| `scikit-learn` | ==1.9.0 | ML models, TF-IDF, calibration |
| `pandas` | ≥2.0.0 | Data loading and manipulation (training scripts) |
| `numpy` | ≥1.24.0 | Array operations in inference |
| `spacy` | (latest) | NLP tokenization and lemmatization |
| `python-multipart` | ≥0.0.9 | Required by FastAPI for form data |
| `aiofiles` | ≥23.2.0 | Async file operations |
| `requests` | ≥2.31.0 | HTTP client for model/data download scripts |
| `joblib` | ≥1.3.0 | Pickle-based model serialization/deserialization |
| `gunicorn` | ≥22.0.0 | Production WSGI/ASGI server |
| `pytest` | (latest) | Test runner |
| `httpx` | (latest) | Async HTTP client, required by FastAPI TestClient |
| `loguru` | (latest) | Structured, colored logging |
| `pydantic-settings` | (latest) | Environment variable parsing |
| `slowapi` | (latest) | Rate limiting middleware for FastAPI |

**Not in requirements.txt (optional):**
- `transformers` — Hugging Face Transformers (for DistilBERT)
- `torch` — PyTorch (required by Transformers)

**spaCy model (installed separately):**
- `en_core_web_sm` — English small model, downloaded via `python -m spacy download en_core_web_sm`

### F.2 Version Pin Rationale

`scikit-learn` is pinned to `==1.9.0` because scikit-learn is not guaranteed to produce bitwise-identical predictions across versions, and the production model artifacts were serialized with 1.9.0. Using a different version could silently change prediction behavior or fail to load artifacts.

### F.3 Frontend Dependencies

All loaded from CDN (no build step required):
- Google Fonts: Inter, JetBrains Mono, Space Grotesk, Syne
- No JavaScript framework — pure vanilla ES6+

---

## Chapter G: API and Interface Reference

### G.1 `GET /health`

**Purpose:** Liveness and readiness check.
**Rate limit:** None
**Authentication:** None

**Response 200:**

The following uptime number is illustrative; it is not a live measurement.

```json
{
  "status": "ok",
  "models_loaded": true,
  "uptime_seconds": 142.7,
  "api_version": "2.0.0"
}
```

### G.2 `GET /models/info`

**Purpose:** Returns per-model accuracy statistics from Phase 2 held-out evaluation.
**Rate limit:** None
**Authentication:** None

**Response 200** (structure from `predictor.meta`):
```json
{
  "lr": {
    "name": "Logistic Regression",
    "accuracy": 97.43,
    "brier_score": 0.020837,
    "calibration_method": "isotonic"
  },
  "dt": {"name": "Decision Tree", "accuracy": 98.66, ...},
  "gbc": {"name": "Gradient Boosting", "accuracy": 98.66, ...},
  "nb": {"name": "Naive Bayes", "accuracy": 94.96, ...},
  "svc": {"name": "Linear SVC", "accuracy": 97.84, ...},
  "ensemble": {
    "name": "Five-model average calibrated probability ensemble",
    "accuracy": 98.44,
    "brier_score": 0.013835
  }
}
```

**Response 503:** `{"detail": "Models not loaded yet"}` (returned if called before startup completes)

### G.3 `GET /metrics`

**Purpose:** Process-local counters and average confidence for successful `POST /analyze` requests only. `/analyze/deep` does not update these server counters. They reset when the process restarts; the endpoint has no persistent database behind it.
**Rate limit:** None

**Response 200** (sample values are illustrative):
```json
{
  "total_requests": 47,
  "fake_detected": 28,
  "real_detected": 19,
  "avg_confidence": 93.4,
  "uptime_seconds": 1800.5,
  "models_loaded": true,
  "api_version": "2.0.0"
}
```

### G.4 `POST /analyze`

**Purpose:** Classify an article using the 5-model TF-IDF ensemble.
**Rate limit:** 10 requests/minute per client IP
**Authentication:** None

**Request body** (`application/json`):
```json
{
  "title": "string (optional, max 500 chars)",
  "text": "string (required, 20–10,000 chars)"
}
```

**Validation errors (422):**
- `text` shorter than 20 characters after stripping
- `text` longer than 10,000 characters
- `title` longer than 500 characters

**Rate limit exceeded (429):**
```json
{
  "error": "rate_limited",
  "message": "You're sending requests too quickly. Please wait a moment and try again.",
  "retry_after_seconds": 45
}
```

**Service unavailable (503):**
```json
{"detail": "Models are still loading, please try again"}
```

**Successful response (200):**

The predicted labels and numeric values below are **illustrative**, not results from a measured request.

```json
{
  "ensemble_is_fake": true,
  "ensemble_label": "FAKE NEWS",
  "overall_confidence": 91.7,
  "fake_votes": 4,
  "real_votes": 1,
  "total_models": 5,
  "models": {
    "lr": {"name": "Logistic Regression", "label": "Fake", "is_fake": true, "confidence": 89.3},
    "dt": {"name": "Decision Tree", "label": "Fake", "is_fake": true, "confidence": 97.8},
    "gbc": {"name": "Gradient Boosting", "label": "Fake", "is_fake": true, "confidence": 94.1},
    "nb": {"name": "Naive Bayes", "label": "Real", "is_fake": false, "confidence": 55.2},
    "svc": {"name": "Linear SVC", "label": "Fake", "is_fake": true, "confidence": 91.0}
  },
  "processed_length": 67,
  "processing_time_ms": 23.4
}
```

**Field definitions:**
- `ensemble_is_fake` (bool): True if ensemble_probability < 0.5
- `ensemble_label` (str): "FAKE NEWS" or "REAL NEWS"
- `overall_confidence` (float): Ensemble confidence percentage (50–100)
- `fake_votes` / `real_votes` (int): Number of individual models predicting each class
- `total_models` (int): Always 5 in production
- `models` (dict): Per-model results keyed by model code
- `processed_length` (int): Word count of processed input
- `processing_time_ms` (float): Server-side inference time in milliseconds

### G.5 `POST /analyze/deep`

**Purpose:** Classify using DistilBERT transformer model.
**Rate limit:** 5 requests/minute per client IP
**Note:** Returns 503 if transformers/torch not installed or if HuggingFace Hub is unavailable.

**Same request schema as `/analyze`.**

**Response 200** (sample values are illustrative):
```json
{
  "label": "FAKE",
  "confidence": 97.9,
  "processing_time_ms": 312.5
}
```

### G.6 `GET /` (Frontend)

Returns `frontend/index.html` as `text/html`. Serves the dashboard.

### G.7 `GET /static/{path}` (Static Files)

Serves `frontend/` directory contents. CSS, JS, and images.

### G.8 `GET /docs`

FastAPI's auto-generated Swagger UI. The current workspace environment has FastAPI 0.141.1 and generates an OpenAPI 3.1.0 document. `requirements.txt` specifies `fastapi>=0.111.0` rather than pinning one version, so a different installed version can change generated documentation details.

---

## Chapter H: Data Models and Persistence

### H.1 No Database

TruthScan uses **no database**. There is no SQL/NoSQL store, ORM, or migration system. All state is either:
- **On-disk model artifacts** — `.pkl` files in `models/calibrated/`
- **In-memory at runtime** — model objects held in `FakeNewsPredictor`, metrics counters in `_metrics`
- **CSV files** — training data in `data/`, evaluation results in `evaluation_results/`

### H.2 Training Dataset Schema

**`data/Fake.csv`** (11,107 rows, ~30 MB):

| Column | Type | Description |
|--------|------|-------------|
| title | string | Article headline |
| text | string | Article body |
| subject | string | Topic category |
| date | string | Publication date (not used in training) |
| class | int | Added by code: 0 = fake |

**`data/True.csv`** (13,246 rows, ~34 MB):

Same schema, `class` = 1 (real).

**Evaluation-report counts:** 24,353 rows (11,107 fake + 13,246 real), as recorded in `phase1_evaluation_report.json`. The report does not record a dataset source or revision. `download_data.py` currently attempts the Hugging Face WELFake CSV first and offers the Kaggle “Fake and Real News” URL as a manual alternative; either route may produce data that differs from the corpus behind these reported metrics.

### H.3 Model Artifact Schema

All production artifacts reside in `models/calibrated/`:

| File | Type | Size | Description |
|------|------|------|-------------|
| `vectorizer.pkl` | `TfidfVectorizer` | 6.3 MB | Fitted TF-IDF vectorizer (150K feature vocabulary) |
| `lr_calibrated.pkl` | `CalibratedClassifierCV` wrapping `LogisticRegression` | 6 MB | Calibrated LR |
| `dt_calibrated.pkl` | `CalibratedClassifierCV` wrapping `DecisionTreeClassifier` | 148 KB | Calibrated DT |
| `gbc_calibrated.pkl` | `CalibratedClassifierCV` wrapping `GradientBoostingClassifier` | 1.2 MB | Calibrated GBC |
| `nb_calibrated.pkl` | `CalibratedClassifierCV` wrapping `MultinomialNB` | 24 MB | Calibrated NB (large due to isotonic calibration data) |
| `svc_calibrated.pkl` | `CalibratedClassifierCV` wrapping `LinearSVC` | 6 MB | Calibrated SVC |

**Note:** The current local workspace contains `rfc_calibrated.pkl` (about 89 MB), but it is not loaded by the production predictor. The README attributes the exclusion to constrained deployment memory; an actual Render out-of-memory event and current plan limits were not verified here.

### H.4 Evaluation Data Schema

**`evaluation_results/held_out_test_set.csv`** (3,653 rows):

| Column | Type | Description |
|--------|------|-------------|
| title | string | Article headline |
| text | string | Article body |
| class | int | Ground truth label (0=fake, 1=real) |

This is a generated/local evaluation input and is not downloaded by `download_models.py`. That downloader fetches five calibrated classifier files, `vectorizer.pkl`, and `phase2_calibration_report.json`; Phase 2 calibration needs the held-out CSV and Phase 1 report locally.

**`evaluation_results/phase2_calibration_report.json`**:
The primary source of accuracy metadata used by `predictor.load()`. Loaded at startup and served via `GET /models/info`.

### H.5 In-Memory State

| Variable | Location | Lifetime | Content |
|----------|----------|---------|---------|
| `predictor.vectorizer` | `predictor.py` | Application lifetime | `TfidfVectorizer` object |
| `predictor.models` | `predictor.py` | Application lifetime | Dict of 5 calibrated classifier objects |
| `predictor.meta` | `predictor.py` | Application lifetime | Model accuracy metadata dict |
| `_metrics` | `routers/api.py` | Application lifetime (resets on restart) | Successful `/analyze` counts and confidence sum; deep requests are excluded |
| `distilbert_predictor.classifier` | `distilbert_predictor.py` | Application lifetime | HuggingFace pipeline object (if loaded) |

---

## Chapter I: Algorithms and ML Implementation

### I.0 The evaluation words, with examples

The **positive class** in these reports is `class = 1` (real); `class = 0` means fake. A model predicts a label from article features. A probability is a score between 0 and 1; it is not proof or a source check. For this app, each model's probability is `P(real)`, and a score of **0.5 or greater** predicts real. The production ensemble averages five `P(real)` scores and then applies that threshold. The five individual vote counts are shown for context but do not determine the ensemble label.

For a tiny illustration, suppose the five models output `0.60`, `0.65`, `0.70`, `0.75`, and `0.70` for `P(real)`. Their average is `0.68`, so the ensemble says real with `overall_confidence: 68.0`. These values are illustrative; they are not a test run. If the average were `0.32`, it would predict fake with confidence `68.0` (one minus the probability of real).

The Phase 2 report measures the average ensemble and individual models on the **same 3,653 held-out articles**. The separate Phase 1 report also records cross-validation and final held-out metrics for its six-model workflow. Do not compare numbers without naming the phase, split, and metric.

| Measure | Meaning | Project-specific note |
|---|---|---|
| **Accuracy** | Correct predictions divided by all predictions. | A high value can hide poor results for a smaller class. Phase 2 ensemble accuracy is 98.44% on its 3,653-row held-out set. |
| **Precision** | Of the items predicted as a class, the fraction that truly has that class. | The Phase 1 report records weighted precision; the Phase 2 report does not report precision. |
| **Recall** | Of the items truly in a class, the fraction the model found. | The Phase 1 report records weighted recall; the Phase 2 report does not report recall. |
| **F1** | A combined score balancing precision and recall. | The Phase 1 report records weighted F1; it is not a Phase 2 result. |
| **Confusion matrix** | Counts correct/incorrect predictions by actual and predicted class. | Phase 1 uses label order `[0, 1]` (fake, real). It helps reveal which class was confused with the other. |
| **Brier score** | Mean squared difference between predicted probability and the binary outcome; lower is better. | Phase 2 ensemble Brier score is 0.013835 on the same held-out set. For a single true-real example (`y=1`), `p=0.8` contributes `(0.8-1)^2=0.04`, while `p=0.4` contributes `0.36`. |
| **Calibration** | Whether predictions at a probability level occur at roughly that frequency over many examples. | For instance, among cases assigned about 0.8 probability of real, roughly 80% should be real for good calibration. The script selects sigmoid or isotonic calibration by inner training-only Brier score; all five selected isotonic in the saved report. |

These measures describe behavior on the named evaluation data only. They do not establish universal reliability, equal error rates across populations, or factual correctness on a new article.

### I.1 Feature Extraction: TF-IDF

**Class:** `sklearn.feature_extraction.text.TfidfVectorizer`

**Configuration:**
```python
TfidfVectorizer(
    ngram_range=(1, 2),     # unigrams and bigrams
    max_features=150_000,    # at most 150K terms, selected by corpus term frequency
    sublinear_tf=True,       # apply 1 + log(tf) transformation
    analyzer='word',
    min_df=2,                # ignore terms appearing in fewer than 2 documents
    max_df=0.95              # ignore terms appearing in more than 95% of documents
)
```

**How it works:**
- Converts preprocessed text strings into sparse numerical vectors.
- Each dimension corresponds to a word or word-pair (bigram) from the vocabulary.
- `sublinear_tf=True` dampens the influence of very high term frequencies.
- `min_df=2` removes extremely rare terms (likely noise).
- `max_df=0.95` removes terms that appear in almost every document (generic filler words that survived lemmatization).

**Why bigrams?** Bigrams capture short phrases like "white house" or "stock market" that have strong discriminative signal. The original notebook used only unigrams; `train.py` added bigrams as an improvement.

### I.2 Text Preprocessing Pipeline

**Triple title weighting:** `preprocess()` concatenates the title three times before the article text. This makes headline terms appear repeatedly in the input, but it does not guarantee exactly three times the final TF-IDF weight: sublinear term frequency and vector normalization also affect the resulting features. The pipeline implements the weighting; its causal benefit was not isolated experimentally in the repository.

**Lemmatization:** Reduces vocabulary size and groups morphological variants (e.g., "running", "ran", "runs" → "run"), improving generalization.

**Stop word removal:** Reduces feature space by removing high-frequency words (the, a, is, etc.) that carry little discriminative information.

### I.3 Classification Models

#### Logistic Regression (`lr`)
- Hyperparameters: `C=5.0, max_iter=1000, random_state=42`
- Works well on high-dimensional sparse text features.
- `C=5.0` is weaker regularization than the default `C=1.0` (scikit-learn's `C` is inverse regularization strength).
- Held-out accuracy (Phase 2): **97.43%**

#### Decision Tree (`dt`)
- Hyperparameters: `max_depth=None` (fully grown), `random_state=42`
- Unusual for text classification due to instability, but performs well in this dataset.
- Held-out accuracy (Phase 2): **98.66%**
- Likely benefits from clear stylistic splits in fake vs. real news vocabulary.

#### Gradient Boosting Classifier (`gbc`)
- Hyperparameters: `n_estimators=200, random_state=42`
- Tied highest individual held-out accuracy at **98.66%** with Decision Tree.
- Slower to train than other models but produces better calibrated probabilities.

#### Naive Bayes (`nb`)
- Class: `MultinomialNB`, hyperparameters: `alpha=0.01`
- Fastest inference. Works well with TF-IDF features.
- Lowest accuracy at **94.96%** but included for ensemble diversity.
- Smoothing parameter `alpha=0.01` is very low (nearly no smoothing).

#### Linear SVC (`svc`)
- Hyperparameters: `C=1.0, max_iter=2000, random_state=42`
- Does not natively support `predict_proba()`. `CalibratedClassifierCV` wraps it to add probability calibration.
- Held-out accuracy (Phase 2): **97.84%**

### I.4 Probability Calibration

**Method:** `sklearn.calibration.CalibratedClassifierCV`

Calibration adjusts model output probabilities so they match the actual observed frequency of the positive class. An uncalibrated model predicting 90% confidence may not actually be correct 90% of the time.

**Two calibration methods evaluated:**
1. **Sigmoid (Platt scaling):** Fits a logistic regression on the model's raw scores. Good for well-ordered but poorly-scaled probabilities.
2. **Isotonic regression:** Non-parametric, fits a monotone piecewise constant function. More flexible but requires more calibration data.

**Selection criterion:** Lower Brier score on an inner 20% validation split. All 5 models selected isotonic regression.

**Brier score:** `B = (1/n) * sum((p_i - y_i)²)`. Lower is better. Measures the mean squared error of probability predictions. A perfect model has B=0; a model predicting 50% always has B=0.25.

**Production ensemble method:** Average calibrated P(class=1) across all 5 models. Unlike majority vote, this preserves the magnitude of each model's probability. This is a design choice, not evidence that averaging is universally superior. The saved report measures the ensemble Brier score and accuracy; it does not separately fit a post-averaging calibration layer.

### I.5 Training Dataset Statistics (Phase 1 Report)

- **Total rows:** 24,353
- **Class distribution:** 11,107 fake (45.6%), 13,246 real (54.4%) — slightly imbalanced
- **Held-out size:** 3,653 (15%, stratified)
- **Training rows for CV + final fit:** 20,700
- **Cross-class duplicate check:** 0 exact duplicates between fake and real classes (**Observed**)
- **Near-duplicate rate:** 0.0% in sampled check (**Observed**)

### I.6 DistilBERT Model

**HuggingFace ID:** `GuptaAshutosh/truthscan-fake-news-distilbert`
**Type:** Fine-tuned `distilbert-base-uncased` for binary text classification
**Claimed accuracy:** 99.97% (5-fold CV + held-out evaluation on September 16, 2026)

**Status:** **Inferred** — the model weights are hosted externally on HuggingFace Hub and were not locally inspected. The 99.97% figure comes from the README and has not been independently verified from this repository's evaluation scripts. The DistilBERT training script is not present in this repository.

**Inference behavior (Verified from `distilbert_predictor.py`):**
- Input: `f"{title} {title} {title} {text}"` (raw, not regex-cleaned)
- Truncated to 512 tokens by the tokenizer
- Label mapping: `LABEL_0` → FAKE, `LABEL_1` → REAL

### I.7 Phase 1 Cross-Validation Results (Observed from `phase1_evaluation_report.json`)

| Model | Mean CV Accuracy | Std | Stable? |
|-------|-----------------|-----|---------|
| Logistic Regression | 97.21% | 0.23% | Yes |
| Decision Tree | 97.59% | 0.24% | Yes |
| Gradient Boosting | 98.18% | 0.21% | Yes |
| Random Forest | 96.51% | 0.25% | Yes |
| Naive Bayes | 94.72% | 0.46% | Yes |
| Linear SVC | 97.94% | 0.18% | Yes |

All models show stable performance across folds (std < 2%). Gradient Boosting leads in CV accuracy.

---

## Chapter J: Setup and Configuration

### J.1 Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.11 | Pinned in CI and Render config |
| pip | Latest | |
| Internet access | — | Required for model download during setup |

Use a full copy of the project's expected `data/Fake.csv` and `data/True.csv` only for retraining. The checked-out evaluation report records the evaluated row counts, but the repository does not record the exact provenance/revision of those local files.

### J.2 Local Installation Steps

```bash
git clone https://github.com/ashutosh8950/fake-news-detector.git
cd fake-news-detector
```

**Windows PowerShell:**

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m spacy download en_core_web_sm
python download_models.py
python app.py
```

If PowerShell blocks activation scripts, skip activation and run the virtual-environment interpreter directly, for example `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`, then `.\.venv\Scripts\python.exe app.py`.

**Linux/macOS:**

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m spacy download en_core_web_sm
python download_models.py
python app.py
```

The spaCy model and calibrated artifacts are separate downloads and require network access. The app process does not download missing artifacts automatically.

**Check the local server:**

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

```bash
curl http://127.0.0.1:8000/health
```

Look for `"status": "ok"` and `"models_loaded": true`. The interactive API page is at `http://127.0.0.1:8000/docs`.

**Optional DistilBERT:** The base requirements do not include Transformers or PyTorch. Install them separately only when testing that path; the packages/model require substantial downloads, and the endpoint remains unavailable if loading fails.

### J.3 Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `PORT` | `8000` | No | HTTP port |
| `ENVIRONMENT` | `production` for CORS | No | `app.py` reads the process environment directly; `development`, `local`, or `test` adds localhost CORS defaults |
| `ALLOWED_ORIGINS` | (production URL) | No | Comma-separated CORS allowed origins |
| `APP_NAME` | `"Fake News Detection API"` | No | Pydantic Settings `app_name` |
| `MODELS_DIR` | `"models"` | No | Base path for model artifacts |
| `DATA_DIR` | `"data"` | No | Base path for CSV data |

**Note:** No `.env.example` file exists in the repository. `config.py` defines `Settings.environment` as `development`, while CORS in `app.py` reads `os.environ` and defaults to `production`; these are different defaults. Pydantic loads `.env` into `settings`, but direct `os.environ` CORS reads do not use `settings.environment`. Set process environment variables explicitly when configuring CORS.

### J.4 Re-training from Scratch (Optional)

To regenerate evaluation/model artifacts, first obtain the full matching dataset files with `title` and `text` columns. The downloader currently attempts the WELFake Hugging Face CSV; that is not guaranteed to recreate the exact corpus/counts in the existing report. Its built-in fallback has only 10 examples per class and cannot reproduce the reported metrics. The script also points to the Kaggle “Fake and Real News” dataset as a manual source, but the exact source/revision used for the existing 24,353-row evaluation is not recorded.

```bash
# 1. Download training data
python download_data.py

# 2. Run Phase 1 evaluation (generates held-out split + evaluation report)
python evaluate_pipeline.py
# Takes ~20-40 minutes depending on hardware

# 3. Run Phase 2 calibration (generates production model artifacts)
python phase2_calibration.py
# Takes ~30-60 minutes depending on hardware

# 4. (Optional) Compare calibrated vs uncalibrated
python compare_calibration.py
```

**Important:** `phase2_calibration.py` requires the Phase 1 split/report and exactly 20,700 training rows plus 3,653 held-out rows. `train.py` is a separate legacy workflow and does not create the calibrated production artifacts expected by the app. The Phase 1 and Phase 2 commands can take substantial time; their durations depend on hardware and were not benchmarked for this guide.

### J.5 Docker Setup

```bash
# Build (downloads models during build)
docker build -t fake-news-detector .

# Run
docker run -p 8000:8000 fake-news-detector

# With environment variables
docker run -p 8000:8000 -e ENVIRONMENT=development fake-news-detector
```

### J.6 Running Tests

```bash
# Run all tests (requires real models to be loaded for test_nasa.py)
python -m pytest -v tests/

# Run only unit tests (no model loading required)
python -m pytest -v tests/test_api.py

# Run only integration tests (loads real models)
python -m pytest -v tests/test_nasa.py
```

---

## Chapter K: Testing and Quality Assurance

### K.1 Test Structure

```
tests/
├── __init__.py
├── fixtures/
│   └── nasa_test_sample.csv   # Held-out articles for integration tests
├── test_api.py                # 5 mocked unit tests
└── test_nasa.py               # 1 integration test (4 samples)
```

### K.2 Test Execution Results (Observed)

Verified for this documentation update with `.venv\Scripts\python.exe -m pytest -v tests/` on Python 3.11.9: **6 passed, 2 deprecation warnings** in 29.02 seconds. This confirms the current test suite run, not model accuracy beyond the checked-in evaluation reports.

### K.3 What Is and Is Not Tested

**Tested (Unit — mocked):**
- Health endpoint response structure
- Models info endpoint response structure
- Analyze endpoint with fake result (mocked)
- Analyze endpoint with real result (mocked)
- Frontend HTML serving

**Tested (Integration — real models):**
- 4 articles from `nasa_test_sample.csv` (2 fake, 2 real): correct ensemble classification, confidence >50%, valid vote counts, response time <2s, processed_length >10

**NOT Tested:**
- Input validation edge cases (empty text, exactly 20 chars, max_length boundary, HTML injection)
- Rate limiting behavior (429 responses)
- Model loading failure scenarios (missing artifact files)
- Concurrent request behavior
- CORS headers in responses
- `/metrics` endpoint accumulation across multiple requests
- `/analyze/deep` endpoint (DistilBERT)
- Error handling: prediction exception path (HTTPException 500)
- Global exception handler (500 path)
- All 3,653 held-out test articles

### K.4 Test Commands

```bash
# All tests
python -m pytest -v tests/

# With coverage
python -m pytest --cov=. tests/

# Only fast unit tests
python -m pytest -v tests/test_api.py -k "not nasa"
```

---

## Chapter L: Security, Reliability, and Performance

### L.1 Input Validation

**Verified controls:**
- Pydantic `max_length=10000` on `text` and `max_length=500` on `title` constrain the accepted values of those individual fields. These limits do not cap the HTTP request-body size before the body is received and parsed.
- Minimum 20-char `text` requirement prevents trivially empty requests.
- Whitespace stripping prevents whitespace-only bypass.

**Potential gaps:**
- No HTML escaping in API responses (not needed — API returns structured JSON, not HTML).
- The application code has no explicit request-body size limit or application-level `Content-Type` enforcement. The tests do not establish how every non-JSON request is handled.
- spaCy's `nlp()` processes whatever text survives regex cleaning; no explicit DoS protection on text length before spaCy (however, max_length=10,000 chars with triple title = 30,500 chars maximum to spaCy).

### L.2 Rate Limiting

**Verified:** slowapi limits `/analyze` to 10/minute per IP and `/analyze/deep` to 5/minute per IP. Enforced at middleware level.

**Limitation:** The rate limiter is in-memory and process-local. A multi-worker deployment would not share rate limit counters. The current single-worker Gunicorn config is unaffected.

### L.3 Authentication and Authorization

**None implemented.** The API is fully public. Anyone with the URL can call all endpoints. This is appropriate for the current use case (public demo) but would need change for a production deployment with user-specific quotas or gated access.

### L.4 Secrets Handling

- `.env` is listed in `.gitignore`; that does not by itself prove no credentials exist elsewhere.
- GitHub token / HuggingFace token: not required for public model downloads.
- `.gitignore` correctly excludes `.env`, `*.pkl`, `data/`, `models/`, and `*.log`.
- This documentation review found no credential-like strings in the Markdown/PDF text scan. It did find a personal local Windows path in the old PDF; that PDF was preserved unchanged because its build process could not be verified.

### L.5 Error Response Sanitization

**Verified:** `global_exception_handler` logs full exception tracebacks server-side but returns only a generic message and request ID to the client. Internal stack traces, file paths, and variable values are never exposed.

### L.6 Performance Observations

No model-loading, inference-latency, or process-memory benchmark was run for this documentation update. The model file sizes listed in Chapter H are local on-disk sizes, not runtime memory measurements. `tests/test_nasa.py` asserts a per-sample `processing_time_ms < 2000`; that is a test bound, not a published latency benchmark. The API logs request length, label, confidence, and measured processing time, not article text in its normal analysis log line.

### L.7 Dependency Risks

- **scikit-learn pinned to 1.9.0:** This pin is security-relevant. Check for security advisories against 1.9.0 periodically.
- **joblib pickle loading:** Loading untrusted `.pkl` files is a security risk. The production setup downloads models only from the trusted GitHub Releases URL. Do not allow user-supplied pickle files.
- **`requests` library:** Used for model/data download. Correct use of `timeout=300` prevents hanging. SSL verification is on by default.

---

## Chapter M: Deployment and Operations

### M.1 Render.com Deployment

**Service configuration in `render.yaml`:** Python web service, plan `free`; no region is specified in this repository. Current plan resources and live region were not checked.
**Build:** `pip install -r requirements.txt && python -m spacy download en_core_web_sm && python download_models.py`
**Start:** `gunicorn app:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120`

**Note:** The configured Python build downloads model files during each build. Render filesystem persistence and current plan limits can change; live storage behavior was not tested.

### M.2 Docker Deployment

```bash
docker build -t fake-news-detector .
docker run -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e ALLOWED_ORIGINS=https://yourdomain.com \
  fake-news-detector
```

Models are downloaded during `docker build` and baked into the image. No download at container startup.

### M.3 Health Monitoring

- `GET /health` returns `models_loaded: true/false` and `uptime_seconds`.
- `GET /metrics` returns request counts and average confidence.
- loguru writes structured logs to stdout; redirect to file or log aggregator as needed.

### M.4 CI/CD Pipeline

GitHub Actions runs on every push/PR to `main`:
1. Install dependencies
2. Download models
3. Run full pytest suite

Failure in any step blocks merge (if branch protection is enabled).

### M.5 Known Operational Issues

- **Cold start latency:** Host- and plan-dependent; no current live measurement is available.
- **Single worker:** `render.yaml` configures one Gunicorn worker. The README attributes constrained deployment resources as motivation; current host memory and scaling behavior were not tested.
- **No persistent metrics:** `/metrics` counters reset on restart.

---

## Chapter N: Design Decisions and Trade-offs

### N.1 Average Calibrated Probability vs. Majority Vote

**Decision:** Production ensemble uses average P(class=1) from calibrated models.
**Alternative:** Majority vote (used in Phase 1 evaluation).
**Evidence:** `predictor.py` L155, `phase2_calibration.py` L243.

**Trade-off:** Average probability is more expressive — a 4-1 vote where all 4 models are 95%+ confident is treated differently from a 3-2 vote where all models are 55% confident. However, it requires all models to produce calibrated probabilities, which is why calibration was added in Phase 2.

### N.2 Random Forest Excluded from Production

**Decision:** RF is trained in `train.py` and evaluated in `evaluate_pipeline.py` but excluded from `predictor.py`.
**Reason (from README):** "Random Forest was removed because its calibrated artifact caused memory issues on constrained deployment environments." (`rfc_calibrated.pkl` is 89 MB.)
**Evidence:** `predictor.py` MODEL_KEYS list excludes `"rfc"`. `rfc_calibrated.pkl` exists in `models/calibrated/` but is not loaded.
**Trade-off:** Reduced ensemble size. The Phase 2 report gives 98.44% accuracy for the five-model averaged-probability ensemble; Phase 1 reports a different six-model majority-vote result. These are different workflows and should not be presented as an apples-to-apples model comparison. The README cites constrained deployment memory as the reason for the exclusion; current hosting memory limits were not checked here.

### N.3 spaCy Pre-warm in Lifespan

**Decision:** `preprocess("warmup", "warmup text")` is called at startup.
**Reason:** Eliminates ~4-second first-request latency caused by spaCy's lazy model loading.
**Evidence:** `app.py` L45–49 comment: "spaCy pre-warm (loads model into memory)".
**Trade-off:** Adds ~1-2 seconds to startup time in exchange for consistent first-request latency.

### N.4 DistilBERT as Optional Dependency

**Decision:** `transformers` and `torch` are not in `requirements.txt`.
**Observed behavior:** The app attempts to load the Hugging Face model at startup only when Transformers is importable. A load failure is non-fatal; `/analyze/deep` returns 503 when the model is unavailable. Live deployment availability was not tested.

### N.5 Phase 1 + Phase 2 Separation

**Decision:** Calibration is a separate phase (script) from initial training.
**Reason:** Prevents data leakage — calibration uses the same held-out test set that was used for Phase 1 evaluation. Calibration only sees training rows.
**Evidence:** `phase2_calibration.py::load_phase1_data()` reconstructs and validates the exact Phase 1 split.

### N.6 Model Artifacts Distributed via GitHub Releases

**Decision:** Pre-trained `.pkl` files hosted on GitHub Releases, downloaded by `download_models.py`.
**Reason:** Keeps large binary files out of the git repository (gitignored). Allows CI and Render to fetch artifacts without re-training.
**Trade-off:** Adds a network dependency at setup time. If GitHub Releases are unavailable, setup fails.

### N.7 No Database

**Decision:** No persistence layer.
**Trade-off:** Simple deployment and no operational overhead. Costs: no request logging persistence, no user accounts, no per-user rate limits, no audit trail.

---

## Chapter O: Limitations and Improvement Roadmap

### O.1 Confirmed Limitations

1. **Domain specificity:** The README describes the intended corpus as US political news from 2016–2017, but the exact provenance/revision of the local evaluation data was not established here. Performance on other topics and time periods is unknown.

2. **No live fact-checking:** TruthScan cannot verify claims against current events. It classifies stylistic/statistical patterns, not factual accuracy.

3. **Deployment cold starts:** Model loading can delay readiness; actual duration depends on the host and plan and was not measured in this review.

4. **No persistent metrics:** `/metrics` resets on restart.

5. **DistilBERT availability:** Optional dependencies/model loading may fail; the endpoint returns 503 when unavailable. Its current live-deployment status is unknown because it was not tested.

6. **Single worker:** No concurrency beyond one simultaneous blocking inference call (Uvicorn's async loop helps but scikit-learn's predict_proba is synchronous and blocking).

7. **Rate limits are per-process:** Multi-worker deployments would not enforce correct per-IP rate limits.

8. **Confidence ≠ factual certainty:** Confidence values are calibrated probabilities on the training distribution, not ground truth accuracy for new articles.

### O.2 Potential Risks Requiring Investigation

1. **scikit-learn 1.9.0 security advisories:** The pinned version should be monitored for CVEs.
2. **Pickle deserialization:** If the GitHub Releases URL or download_models.py were compromised, malicious `.pkl` files could execute arbitrary code at load time.
3. **Tokenizers parallelism setting:** `TOKENIZERS_PARALLELISM=false` is set globally for DistilBERT. This could affect other HuggingFace usage if added to the same process.
4. **Missing model files:** If GitHub Releases are deleted or renamed, `download_models.py` and the CI pipeline will fail.

### O.3 Recommended Improvements

**High priority:**
- Add a `.env.example` file documenting all environment variables.
- Add test coverage for input validation edge cases and error paths.
- Add a persistent log store (file rotation with loguru, or external aggregator).
- Move metrics to a proper metrics library (Prometheus/statsd) for multi-worker deployments.

**Medium priority:**
- Validate model performance on non-political news categories.
- Add `/analyze/batch` endpoint for bulk classification.
- Implement async model inference using `run_in_executor` to avoid blocking the event loop.
- Add integration tests for rate limiting, 503 scenarios, and error handling.

**Low priority / Future features:**
- Add authentication/API keys for rate limiting per user.
- Persist request logs to a database for analytics.
- Add a confidence calibration reliability curve endpoint.
- Publish DistilBERT training scripts for reproducibility.
- Add multi-language support.

---

## Chapter P: Glossary and Quick Reference

### P.1 Glossary

| Term | Definition |
|------|-----------|
| **TF-IDF** | Term Frequency–Inverse Document Frequency. A numerical statistic reflecting how important a word is to a document in a corpus. Used as the feature representation for all scikit-learn models. |
| **Bigram** | A sequence of two adjacent words. `ngram_range=(1,2)` includes both single words and word pairs. |
| **Calibrated probability** | A model's output probability adjusted so that P(y=1) = k corresponds to the event occurring in approximately k fraction of cases. |
| **Brier score** | Mean squared error of probability predictions. Lower is better; 0 = perfect. A constant 0.5 forecast scores 0.25. |
| **CalibratedClassifierCV** | scikit-learn wrapper that applies sigmoid or isotonic regression calibration to a base classifier. |
| **Ensemble** | Combination of multiple model predictions into a single output. Here: average of 5 calibrated P(class=1) values. |
| **Phase 1** | The initial evaluation phase: cross-validation + held-out evaluation to establish baseline metrics. |
| **Phase 2** | The calibration phase: fits calibrated classifiers on Phase 1 training data, evaluates on the same held-out set. |
| **Held-out test set** | A 15% stratified sample (3,653 rows) that was locked before any model was trained. Used only for final evaluation. |
| **Lifespan** | FastAPI's asynccontextmanager for running code at startup and shutdown. |
| **spaCy** | Industrial-strength NLP library. Used here for lemmatization and stop word removal. |
| **lemmatization** | Reducing words to their base form (lemma). "running" → "run". |
| **slowapi** | FastAPI-compatible rate limiting library based on Python `limits`. |
| **ASGI** | Asynchronous Server Gateway Interface. Protocol used by FastAPI and Uvicorn. |
| **Gunicorn** | WSGI/ASGI server for production. Used with UvicornWorker class for ASGI compatibility. |
| **WELFake** | A public fake news detection dataset containing ~44,000 articles from multiple sources. |

### P.2 Important Paths

| Path | Purpose |
|------|---------|
| `app.py` | Application entry point |
| `predictor.py::predictor` | Production singleton predictor |
| `preprocessor.py::preprocess` | Text cleaning function |
| `routers/api.py` | All API endpoint definitions |
| `models/calibrated/*.pkl` | Production model artifacts |
| `evaluation_results/phase2_calibration_report.json` | Model accuracy metadata |
| `evaluation_results/held_out_test_set.csv` | Locked evaluation set |
| `frontend/` | Dashboard source files |

### P.3 Common Commands

```bash
# Start server locally
python app.py

# Download production models
python download_models.py

# Run all tests
python -m pytest -v tests/

# Train models (optional, from scratch)
python download_data.py
python evaluate_pipeline.py
python phase2_calibration.py

# Build Docker image
docker build -t fake-news-detector .

# Run Docker container
docker run -p 8000:8000 fake-news-detector

# Check API health
curl http://localhost:8000/health

# Analyze an article
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"title": "Test headline", "text": "This is the article body text that is long enough."}'
```

### P.4 API Quick Reference

| Method | Path | Rate Limit | Description |
|--------|------|-----------|-------------|
| GET | `/health` | None | Liveness/readiness |
| GET | `/models/info` | None | Per-model accuracy |
| GET | `/metrics` | None | Usage statistics |
| POST | `/analyze` | 10/min/IP | Ensemble classification |
| POST | `/analyze/deep` | 5/min/IP | DistilBERT classification |
| GET | `/` | None | Dashboard HTML |
| GET | `/static/*` | None | CSS/JS/assets |
| GET | `/docs` | None | Swagger UI |

---

## Chapter Q: AI Knowledge Base and Interview Preparation

### Q.1 30-Second Project Explanation

> "TruthScan is a FastAPI app that classifies a news headline and body by learned patterns in labelled examples; it does not fact-check claims. Its production path cleans text, converts it to TF-IDF features, and averages real-class probabilities from five calibrated scikit-learn classifiers. The Phase 2 report records 98.44% accuracy on a 3,653-article held-out split from a 24,353-row corpus. That is a dataset-specific result, not a guarantee for new topics or current news. The repository configures deployment to Render, but I would describe live availability only after checking the service."

### Q.2 Two-Minute Technical Explanation

> "The system has two main layers: preprocessing and inference.
>
> In preprocessing, an incoming article's title is concatenated three times with the body, then lowercased and cleaned by regular expressions; spaCy tokenizes it, removes stopwords and short tokens, and replaces retained tokens with lemmas. Repetition increases headline-term counts but does not guarantee exactly triple TF-IDF weight.
>
> The cleaned text then gets vectorized by a TF-IDF vectorizer fitted on the training corpus. TF-IDF creates a sparse numerical vector representing unigrams and bigrams across a 150,000-feature vocabulary.
>
> Five scikit-learn classifiers — each wrapped in scikit-learn's `CalibratedClassifierCV` with isotonic regression — then predict the probability that the article is real. The average of those five calibrated probabilities is the ensemble's P(real). If that average is below 0.5, the article is classified as fake; otherwise, real. The confidence shown to the user is the ensemble probability of the predicted class.
>
> Everything loads once at application startup into a singleton `FakeNewsPredictor` object. The FastAPI application uses an ASGI lifespan hook to load models before accepting requests, and slowapi enforces rate limits of 10 requests per minute per IP address."

### Q.3 Technical Implementation Walkthrough

**Q: Walk me through what happens when a user submits a news article.**

A:
1. The browser's JavaScript posts `{title, text}` as JSON to `POST /analyze`.
2. slowapi middleware checks the IP rate limit (10/min). If exceeded, returns 429.
3. FastAPI routes to `routers/api.py::analyze()`.
4. Pydantic's `AnalyzeRequest` validates: text ≥ 20 chars, ≤ 10,000 chars; both fields whitespace-stripped.
5. `predictor.predict(title, text)` is called.
6. Inside predict: `preprocessor.preprocess(title, text)` triples the title, cleans with regex, lemmatizes with spaCy. Returns a clean string.
7. `vectorizer.transform([clean_string])` → sparse matrix.
8. Each of 5 calibrated models computes `predict_proba()` → `P(class=1)`.
9. Mean of 5 P(class=1) values → ensemble probability. Threshold at 0.5 → final label.
10. Result dict returned to the API handler, which adds `processing_time_ms` and updates in-memory metrics.
11. JSON response sent to browser; JavaScript renders the verdict, confidence bar, and per-model breakdown.

---

### Q.4 Key Interview Questions and Answers

**Q1: What is TF-IDF and why is it used here?**

A: TF-IDF stands for Term Frequency–Inverse Document Frequency. It converts text into numerical vectors by weighting each word by how often it appears in a document (TF) and how rare it is across all documents (IDF). Common words like "the" get low IDF scores; distinctive words get high scores. It's used here because it is computationally efficient, works very well for text classification tasks, produces interpretable features, and is a proven baseline for news classification. The bigram setting `(1,2)` also captures two-word phrases for richer signal.

**Q2: Why were 5 models chosen instead of just the best one?**

A: The implementation averages probabilities from five different classifiers, preserving more information than a vote count. The report records 98.44% held-out accuracy for the ensemble; Gradient Boosting and Decision Tree each record 98.66%, so the ensemble did **not** have the highest accuracy in this evaluation. A benefit such as robustness to model errors is a hypothesis that would need separate testing, not something established by this score alone.

**Q3: What is probability calibration and why does it matter?**

A: Calibration checks whether predicted probabilities match observed frequencies over groups of examples. If cases assigned about 0.8 probability of `class = 1` are real about 80% of the time, those scores are calibrated at that level. The script chooses sigmoid or isotonic calibration using an inner training-only validation split and the Brier score; all five selected isotonic in the saved report. Calibration helps make probability averaging more interpretable, but does not prove future predictions reliable or independently calibrate the averaged ensemble.

**Q4: How does the code prevent data leakage?**

A: Three mechanisms:
1. `evaluate_pipeline.py` creates the held-out split and saves it to CSV *before* fitting any model. Models are never fitted on held-out data.
2. `phase2_calibration.py::load_phase1_data()` reconstructs and validates the exact Phase 1 split by matching rows, and **validates exact row counts** (20,700 / 3,653). A mismatch raises a ValueError.
3. In cross-validation, a *fresh* TF-IDF vectorizer is fitted inside each fold (not fitted on the full training set) to prevent leakage of vocabulary statistics.

**Q5: Why does preprocessing triple the title?**

A: `preprocess()` repeats the title three times before the body. This is an implemented design choice intended to emphasize headline terms. Because TF-IDF applies sublinear term-frequency scaling and vector normalization, the final weight is not exactly three times larger. The repository does not include an ablation that measures whether this choice improves accuracy.

**Q6: What happens if the models aren't loaded when a request comes in?**

A: At startup, `predictor.load()` is called in the FastAPI lifespan hook. If the artifact files are missing, it raises a `RuntimeError` that kills the application process immediately — fail-fast behavior. If the server does start but a request arrives before models are ready (a race condition that shouldn't happen given synchronous loading), `POST /analyze` checks `predictor.loaded` and returns HTTP 503 with a message to retry.

**Q7: Why is Random Forest excluded from the production ensemble?**

A: The local Random Forest artifact is about 89 MB and `predictor.py::MODEL_KEYS` excludes it. The README attributes the exclusion to constrained deployment memory. Current Render memory limits and an actual out-of-memory event were not verified here. The Phase 2 five-model score and Phase 1 six-model majority-vote score come from different workflows, so they should not be treated as a controlled comparison.

**Q8: How does rate limiting work?**

A: The `slowapi` library wraps FastAPI using middleware. The `Limiter` is keyed by `get_remote_address` (client IP). A `@limiter.limit("10/minute")` decorator on the route checks an in-memory counter for the IP. On the 11th request within 60 seconds, it raises `RateLimitExceeded`. The custom exception handler in `app.py` catches this and returns a structured JSON 429 with `retry_after_seconds`.

**Q9: What is Brier score and which model has the best one?**

A: Brier score = mean squared error of predicted probabilities. Lower is better; perfect = 0. Gradient Boosting has the best individual Brier score (0.011045). The 5-model ensemble has a Brier score of 0.013835 — better calibration than LR, NB, and SVC but slightly worse than DT (0.011670) and GBC (0.011045).

**Q10: How are model artifacts distributed without storing them in git?**

A: They're gitignored (`.gitignore` includes `*.pkl` and `models/`). They're uploaded as assets to a GitHub Release tagged `v2.0-calibrated-models`. `download_models.py` fetches them from the release URL using `requests` with streaming. During Docker builds and Render deployments, this script runs as a build step.

**Q11: How does the DistilBERT model differ architecturally from the ensemble?**

A: The ensemble uses sparse unigram/bigram TF-IDF features with traditional classifiers. DistilBERT uses a transformer pipeline and tokenizes raw concatenated text up to 512 tokens. Contextual architecture does not establish that this particular fine-tuned model reliably understands sarcasm or factual context. Its training evidence and reported 99.97% accuracy are not independently available in this repository, and its optional dependency/model load can fail.

**Q12: What's the difference between the Phase 1 and Phase 2 ensembles?**

A: Phase 1 evaluates six classifiers, including Random Forest, and reports a discrete majority-vote ensemble. Phase 2 fits five calibrated classifiers (excluding Random Forest) and reports the mean of their class-1 probabilities. These are different model workflows and aggregation rules; neither reported accuracy alone proves one design is universally better. The probability average preserves score magnitudes, while majority vote uses only class decisions.

---

### Q.5 Architecture and Design Questions

**Q: Why FastAPI over Flask or Django?**

A: *Inferred* — FastAPI offers automatic request/response validation via Pydantic, async support (ASGI), automatic OpenAPI/Swagger documentation, and type hints throughout. For a pure API with no server-rendered templates, it's a natural fit. Flask would require manual validation; Django is heavyweight for this use case. The actual original design rationale is unknown.

**Q: Why Gunicorn with 1 worker instead of multiple?**

A: `render.yaml` configures one Gunicorn worker. Multiple workers generally create additional process memory requirements, but the current deployment memory budget and safe worker count were not measured here. I would first measure resident memory and concurrency under the actual host plan before changing this setting.

**Q: How would you scale this to handle 1,000 requests per minute?**

A: *Recommended* — Several approaches:
1. Run multiple Gunicorn workers on a machine with enough RAM (e.g., 4 workers × ~100 MB = 400 MB for models).
2. Move inference to a dedicated inference service and add a load balancer.
3. Use async inference by running `predict_proba` in a thread pool via `asyncio.run_in_executor`.
4. Implement a shared Redis cache for recently-analyzed texts.
5. Upgrade to GPU-based inference for DistilBERT.
6. Use rate limiting with Redis backend for accurate per-IP limits across workers.

---

### Q.6 Debugging Scenarios

**Q: The server starts but always returns 503 on `/analyze`. What would you check?**

A:
1. Check logs for errors during `predictor.load()` in the lifespan hook.
2. Verify `models/calibrated/` contains the five classifier files (`lr_calibrated.pkl`, `dt_calibrated.pkl`, `gbc_calibrated.pkl`, `nb_calibrated.pkl`, `svc_calibrated.pkl`) and `vectorizer.pkl`; also verify `evaluation_results/phase2_calibration_report.json` exists.
3. If the server exits before responding to `/health`, inspect its startup log for the missing path; failed ensemble loading is fatal, so a health response may not be available.
4. Run `python download_models.py` from the repository root, then restart the app.
5. If only `/analyze/deep` returns 503, check optional Transformers/PyTorch installation and whether the Hugging Face model loaded; ensemble `/analyze` does not depend on DistilBERT.

**Q: Predictions seem wrong — all articles return 50% confidence. What could cause this?**

A: *Inferred possibilities:*
1. The wrong version of the vectorizer was loaded (vocabulary mismatch with models).
2. Preprocessing is producing empty strings (e.g., spaCy failure to lemmatize).
3. The calibration report row counts don't match the training split, causing calibration to produce near-uniform probabilities.
4. Wrong scikit-learn version (different from 1.9.0 used to serialize models).

**Q: The `test_nasa.py` integration test fails with `AssertionError: assert False is True` on `ensemble_is_fake`. What would you check?**

A:
1. Verify the correct model artifacts are loaded (run `GET /models/info` and check accuracy values match the calibration report).
2. Check if `preprocessor.py` was modified — preprocessing changes could shift predictions.
3. Verify the `nasa_test_sample.csv` fixture hasn't been corrupted or replaced.
4. Run the suspect article through `/analyze` manually and inspect `models` dict to see which individual models are disagreeing.

---

### Q.7 Honest Discussion of Limitations

**Q: How reliable is TruthScan in the real world?**

A (honest): The 98.44% accuracy is measured on a held-out set from the same distribution as the training data — US political news from 2016–2017. Performance on:
- Articles from different time periods: **Unknown**.
- Articles about science, sports, entertainment, or finance: **Unknown and likely lower**.
- Articles in non-English languages: **Not supported**.
- Sophisticated disinformation that mimics real news writing style: **Likely fails**.

The system detects stylistic patterns characteristic of the training corpus's fake articles. A clever fake news article written in the exact style of a Reuters wire story could fool it completely.

**Q: What would you improve first if given two weeks?**

A: *Recommended priority:*
1. Add test coverage for input validation, error paths, and rate limiting.
2. Add an `.env.example` file for developer onboarding.
3. Run the ensemble on a broader, more recent dataset to measure domain generalization.
4. Add async inference (run_in_executor) to prevent blocking the event loop.

---

## Appendix: Evaluation Data Reference

### Phase 1 Cross-Validation Summary

| Model | Mean CV Accuracy | Std |
|-------|-----------------|-----|
| Logistic Regression | 97.21% | 0.23% |
| Decision Tree | 97.59% | 0.24% |
| Gradient Boosting | 98.18% | 0.21% |
| Random Forest | 96.51% | 0.25% |
| Naive Bayes | 94.72% | 0.46% |
| Linear SVC | 97.94% | 0.18% |

### Phase 2 Held-Out Evaluation Summary

| Model | Held-out Accuracy | Brier Score | Calibration |
|-------|-------------------|-------------|-------------|
| Logistic Regression | 97.43% | 0.020837 | isotonic |
| Decision Tree | 98.66% | 0.011670 | isotonic |
| Gradient Boosting | 98.66% | 0.011045 | isotonic |
| Naive Bayes | 94.96% | 0.039742 | isotonic |
| Linear SVC | 97.84% | 0.016710 | isotonic |
| **5-Model Ensemble** | **98.44%** | **0.013835** | avg calibrated P |

### Duplicate Check Results (Phase 1)

- Exact cross-class duplicates: **0** (**Observed**)
- Near-duplicate rate (fake class, 500-sample): **0.0%** (**Observed**)
- Near-duplicate rate (real class, 500-sample): **0.0%** (**Observed**)

---

*End of PROJECT_MASTER_DOCUMENTATION.md*
*Reviewed: 12 October 2026 | Repository: TruthScan | Version 2.0.0*
