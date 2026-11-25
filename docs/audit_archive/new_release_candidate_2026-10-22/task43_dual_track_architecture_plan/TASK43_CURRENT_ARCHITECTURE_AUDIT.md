# Task 43 — Current Architecture Audit

## Scope and evidence status

This is a static audit of the current repository. “Verified” means observed in source; prior audit conclusions are identified as prior findings. No model or dataset was loaded.

## Existing TruthScan path — verified

- `app.py` creates the FastAPI application, installs CORS/rate limiting/error handling, serves `frontend/`, and includes `routers.api`.
- Application lifespan calls `predictor.load()`, warms spaCy through `preprocess()`, and optionally loads the external DistilBERT pipeline. Startup fails if the calibrated bundle is absent or fails `artifact_contract.py` verification.
- `routers/api.py` defines Pydantic `AnalyzeRequest` with required `text` (20–10,000 characters) and optional `title` (up to 500 characters), plus `/health`, `/models/info`, `/metrics`, `/analyze`, and `/analyze/deep`.
- `predictor.py` uses the five calibrated keys `lr`, `dt`, `gbc`, `nb`, and `svc`; it verifies the artifact bundle before `joblib.load`, preprocesses title/text, extracts calibrated class-1 probability, and returns `Fake`/`Real` per-model results plus `FAKE NEWS`/`REAL NEWS` ensemble output.
- `preprocessor.py` loads `en_core_web_sm` at module import, lowercases and cleans text, removes URLs/numbers/punctuation, lemmatizes and removes stopwords, and repeats the title three times.
- `distilbert_predictor.py` is a separate optional external model path. It maps `LABEL_0`/`0` to `FAKE` and `LABEL_1`/`1` to `REAL`; its model is identified by a Hugging Face repository string in source.
- `frontend/index.html` and `frontend/app.js` present the article analyzer, fake/real result, confidence, per-model breakdown, metrics, and optional Deep Analysis mode.

## Training and artifact boundaries — verified

`train.py` reads `data/Fake.csv` and `data/True.csv`, fits TF-IDF and six development estimators, and writes model files. `phase2_calibration.py` reads the local data and writes calibrated artifacts under `models/calibrated/` plus the Phase 2 report. These are not to be invoked for this planning task. Prior Tasks 14–42 report that the production data/artifacts remain provenance-blocked; this audit does not revalidate those records.

`download_models.py` is a provisioning path that writes staged model files and metadata, while `predictor.py` is the deserialization boundary. Existing artifact safeguards are separate from dataset rights and release authorization.

## Reuse versus separation

Reusable infrastructure: FastAPI hosting patterns, request validation concepts, rate limiting, structured errors, health/readiness conventions, static UI shell, logging/request IDs, and the principle of verifying artifacts before deserialization.

Must remain separate: model directories, artifact manifests, preprocessing contracts, label semantics, metrics, dataset/license evidence, grouping policies, evidence handling, and route names or response schemas that could make claim verification look like fake/real classification.

## Current limitations

The existing app’s startup path assumes the production classifier and its artifacts are the application model. It has no claim-verification route, evidence schema, source-citation display, or explicit `INSUFFICIENT_EVIDENCE` outcome. The current UI and API language (“fake”, “real”, “confidence”) must not be reused for FEVER claims without a separate contract.
