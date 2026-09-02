# Fake News Detection Project Report

## Verification note

This report is based only on the current workspace files and code in this project. I did not modify any code.

I also verified the current test status with:

`\.venv\Scripts\python -m pytest -q tests`

Result: it exited with code 1 and printed: `No module named pytest`.

This means the project contains tests, but the current local environment here does not have `pytest` installed.

---

# 1. PROJECT OVERVIEW

## What problem does this project solve?
This project solves a text-classification problem: deciding whether a news article is fake or real.

The actual workflow is:
- receive article title + text
- clean the text
- convert it to numerical features
- run multiple ML models
- combine the votes with a weighted ensemble
- return a verdict such as “FAKE NEWS” or “REAL NEWS” and a confidence score

This is implemented in [app.py](app.py), [routers/api.py](routers/api.py), [predictor.py](predictor.py), and [train.py](train.py).

## Who would use it?
The code suggests these users:
- readers who want to check if a story feels suspicious
- journalists or editors checking incoming stories
- fact-checking teams
- media monitoring tools
- anyone building a fake-news detection system

The project is designed as a web app and API, not a specialist newsroom tool only.

## Complete workflow from input to output
Step by step, based on the code:

1. The user opens the frontend in [frontend/index.html](frontend/index.html) and enters:
   - title (optional)
   - article text

2. The browser sends JSON to the API at `/analyze` using the frontend JavaScript in [frontend/app.js](frontend/app.js).

3. The FastAPI server receives the request in [routers/api.py](routers/api.py).

4. Request validation runs:
   - whitespace is stripped
   - text must be at least 20 characters
   - title and text are limited in length

5. The server calls `predictor.predict(...)` from [predictor.py](predictor.py).

6. `predict()` does:
   - preprocess title + text
   - transform text using the saved TF-IDF vectorizer
   - run all six trained classifiers
   - compute per-model confidence
   - aggregate weighted votes
   - decide final label and overall confidence

7. The API returns something like:
   - `ensemble_label`
   - `ensemble_is_fake`
   - `overall_confidence`
   - `fake_votes`
   - `real_votes`
   - `processing_time_ms`
   - model-level breakdown

8. The frontend displays:
   - verdict card
   - confidence gauge
   - vote tally
   - per-model breakdown
   - history

9. There is also a deeper route `/analyze/deep` that uses DistilBERT instead of the classic ML pipeline.

---

# 2. MY PROJECT EXPLANATION

## 30-second explanation
Situation:
I built a fake-news detection system for news articles that can be checked quickly and automatically.

Task:
My job was to turn article text into a trustworthy prediction of whether it is real or fake.

Action:
I used a FastAPI backend, cleaned and lemmatized the text with spaCy, converted it to TF-IDF features, and ran an ensemble of six ML models: Logistic Regression, Decision Tree, Gradient Boosting, Random Forest, Naive Bayes, and Linear SVC. The app then combines their votes into one result with confidence.

Result:
The user gets a fast verdict and confidence score, and the system can also use a DistilBERT deeper analysis path when available.

## 60-second explanation
Situation:
Many articles online look credible, but people need a quick way to check if they are misinformation.

Task:
I wanted to build a simple API and web app that could classify a news article in seconds.

Action:
I created a FastAPI application with a frontend in [frontend/index.html](frontend/index.html). The backend preprocesses the title and text, removes noise, normalizes the content, and converts it to TF-IDF features. Then six trained models each vote on the article. The final label comes from an accuracy-weighted ensemble. I also added rate limiting, health checks, model metadata, and a DistilBERT “deep analysis” option.

Result:
The project gives a clear fake/real verdict, a confidence score, and a traceable model breakdown, making it useful for quick article validation and API-based integration.

## 2-minute explanation
Situation:
The rise of misinformation makes it hard to tell whether a story is genuine or manipulated, especially when people are sharing headlines without checking the facts.

Task:
I needed to build a practical detection system that could take article text as input and return a reliable classification without requiring a human to read and verify everything manually.

Action:
I built the project as a FastAPI service that serves both the API and a browser-based UI. In the training pipeline in [train.py](train.py), I load the dataset from [data](data), clean title and body text, combine the title with repeated weighting, and use spaCy for lemmatization and stopword removal. Then I convert the text into bigram TF-IDF features. I train six models: Logistic Regression, Decision Tree, Gradient Boosting, Random Forest, Multinomial Naive Bayes, and Linear SVC. The model meta is saved so the app can use each model’s historical accuracy as a voting weight. At runtime, [predictor.py](predictor.py) loads the vectorizer and all saved models once, preprocesses the input, runs each model, and computes a weighted ensemble verdict. The app also exposes a DistilBERT route for deeper analysis when the model is available. I added validation, logging, rate limiting, Docker support, and deployment config.

Result:
The app provides a usable fake-news detection service with a clean UI, API access, and explainable output per model. It is designed to be fast, modular, and easy to deploy, while also supporting a transformer-based second opinion.

---

# 3. ARCHITECTURE

## Complete architecture and data flow in simple English

### High-level architecture
The project has:
- a Python backend using FastAPI
- a frontend static web page
- a training pipeline
- a model loading layer
- optional DistilBERT deep analysis

Relevant files:
- [app.py](app.py)
- [routers/api.py](routers/api.py)
- [predictor.py](predictor.py)
- [train.py](train.py)
- [preprocessor.py](preprocessor.py)
- [distilbert_predictor.py](distilbert_predictor.py)
- [frontend/index.html](frontend/index.html)
- [frontend/app.js](frontend/app.js)

### Simple flow
1. The user enters an article in the browser.
2. Browser sends POST request to `/analyze`.
3. FastAPI validates the request body.
4. The request hits the route in [routers/api.py](routers/api.py).
5. The route calls `predictor.predict`.
6. `predict()` preprocesses the text.
7. The preprocessed text is vectorized using the saved TF-IDF model.
8. Six models each give a fake/real prediction.
9. Accuracy-weighted voting decides final label.
10. Response is sent back to the frontend as JSON.
11. Frontend draws verdict, confidence meter, and per-model votes.

### Training architecture
1. [download_data.py](download_data.py) checks for dataset files.
2. If missing, it tries to download the dataset or falls back to sample data.
3. [train.py](train.py) loads the dataset from [data](data).
4. Text is cleaned and lemmatized.
5. TF-IDF vectorizer is fit on the processed training data.
6. Six classifiers are trained.
7. Models are saved to [models](models).
8. Accuracy metadata is saved to [models/model_meta.json](models/model_meta.json).

### Runtime architecture
At server startup in [app.py](app.py):
- load all models
- warm up spaCy
- optionally load DistilBERT
- print model accuracies

This avoids slow first-use latency.

### Deployment architecture
- [Dockerfile](Dockerfile) builds the app in a container.
- [render.yaml](render.yaml) configures deployment on Render.
- [download_models.py](download_models.py) downloads model artifacts if missing.
- The app runs with Gunicorn + Uvicorn workers.

### Important fact
There is no database in this codebase. Model artifacts are persisted as pickle files in [models](models) and JSON metadata in [models/model_meta.json](models/model_meta.json).

---

# 4. TECHNOLOGY STACK

Below is the actual stack as it appears in the code.

## FastAPI
- What it is: modern Python web framework
- Why used here: API layer, validation, docs, easy deployment
- Where used: [app.py](app.py), [routers/api.py](routers/api.py)
- Why good choice: simple to build REST API and integrate with frontend, automatic OpenAPI docs, easy for service deployment

## Uvicorn and Gunicorn
- What they are: ASGI server and production WSGI/ASGI process manager
- Why used: serve the FastAPI app in production
- Where: [Dockerfile](Dockerfile), [app.py](app.py), [render.yaml](render.yaml)
- Why good choice: common FastAPI production pairing and supports concurrency

## scikit-learn
- What it is: Python ML library
- Why used: training and inference of classifiers
- Where: [train.py](train.py), [predictor.py](predictor.py)
- Why good choice: fast, mature, supports model training, vectorizers, and metrics

## TF-IDF Vectorizer
- What it is: term-frequency times inverse-document-frequency text representation
- Why used: converts text to numeric features for ML
- Where: [train.py](train.py), [predictor.py](predictor.py)
- Why good choice: very effective for text classification and lightweight compared with deep models

## spaCy
- What it is: NLP library
- Why used: lemmatization and stopword removal
- Where: [preprocessor.py](preprocessor.py)
- Why good choice: fast and production-oriented for English text preprocessing

## pandas and numpy
- What they are: data handling and numerical libraries
- Why used: read CSV data, manipulate dataset columns, compute arrays/vectors
- Where: [train.py](train.py), [download_data.py](download_data.py)
- Why good choice: standard for ML data pipelines

## joblib
- What it is: Python serialization library
- Why used: save and load trained models and vectorizers
- Where: [train.py](train.py), [predictor.py](predictor.py)
- Why good choice: common for scikit-learn models and efficient persistence

## Pydantic / pydantic-settings
- What it is: request validation and settings management
- Why used: validate article fields and environment config
- Where: [routers/api.py](routers/api.py), [config.py](config.py)
- Why good choice: clean request validation and settings handling

## SlowAPI
- What it is: rate limiting library for FastAPI
- Why used: protect `/analyze` and `/analyze/deep`
- Where: [routers/api.py](routers/api.py), [app.py](app.py)
- Why good choice: built for FastAPI, easy to add with decorators

## Loguru
- What it is: structured logging library
- Why used: startup logs, model loading logs, error logs
- Where: [app.py](app.py), [train.py](train.py), [predictor.py](predictor.py)
- Why good choice: clean log output with minimal config

## pytest and httpx
- What they are: testing libraries
- Why used: validate API behavior and integration
- Where: [tests/test_api.py](tests/test_api.py), [tests/test_nasa.py](tests/test_nasa.py), [requirements.txt](requirements.txt)
- Why good choice: standard Python testing stack for FastAPI

## DistilBERT / Hugging Face Transformers
- What it is: transformer-based language model
- Why used: deeper text analysis path
- Where: [distilbert_predictor.py](distilbert_predictor.py)
- Why good choice: stronger contextual understanding for a second opinion model

## Docker
- What it is: container platform
- Why used: package app and dependencies
- Where: [Dockerfile](Dockerfile)
- Why good choice: consistent deployment across environments

## Render
- What it is: hosting platform
- Why used: deploy the service
- Where: [render.yaml](render.yaml)
- Why good choice: simple deployment for Python/FastAPI services

## Database
- What it is: persistent data store
- Why used: not present
- Where: nowhere in project
- Why good choice: not needed here because the app stores model files rather than records
- Important fact: no database is used in the current codebase.

---

# 5. CODEBASE

## Entry point
Main runtime entry point is [app.py](app.py).

It:
- creates the FastAPI app
- loads models at startup
- mounts static frontend
- includes the API router
- runs uvicorn when executed directly

## Important folders
- [data](data): dataset files
- [models](models): trained model artifacts and metadata
- [frontend](frontend): browser UI
- [routers](routers): API routes
- [tests](tests): automated tests
- [.github/workflows](.github/workflows): CI pipeline config

## Important files
- [app.py](app.py): app startup, CORS, frontend serving
- [routers/api.py](routers/api.py): API endpoints and validation
- [train.py](train.py): ML training pipeline
- [predictor.py](predictor.py): ensemble prediction logic
- [preprocessor.py](preprocessor.py): cleanup and NLP preprocessing
- [distilbert_predictor.py](distilbert_predictor.py): optional transformer model
- [download_data.py](download_data.py): dataset bootstrap
- [download_models.py](download_models.py): model artifact download
- [config.py](config.py): env/config settings
- [requirements.txt](requirements.txt): dependencies
- [Dockerfile](Dockerfile): container build
- [render.yaml](render.yaml): deployment settings

## Important functions
- `lifespan(...)` in [app.py](app.py): startup loading of models and warmup
- `health()` in [routers/api.py](routers/api.py): system status endpoint
- `models_info()` in [routers/api.py](routers/api.py): returns model metadata
- `analyze()` in [routers/api.py](routers/api.py): classic ensemble prediction
- `analyze_deep()` in [routers/api.py](routers/api.py): DistilBERT path
- `clean_text()` in [preprocessor.py](preprocessor.py): strips punctuation and noise
- `lemmatize_text()` in [preprocessor.py](preprocessor.py): applies spaCy lemma logic
- `preprocess()` in [preprocessor.py](preprocessor.py): combines title+text and returns cleaned text
- `ensure_data()` in [train.py](train.py): dataset check
- `load_data()` in [train.py](train.py): load and split data
- `train()` in [train.py](train.py): full model training
- `FakeNewsPredictor.load()` in [predictor.py](predictor.py): loads saved artifacts
- `FakeNewsPredictor.predict()` in [predictor.py](predictor.py): ensemble prediction
- `FakeNewsPredictor.get_model_info()` in [predictor.py](predictor.py): returns saved metadata
- `DistilBertPredictor.load()` in [distilbert_predictor.py](distilbert_predictor.py): loads transformer model
- `DistilBertPredictor.predict_distilbert()` in [distilbert_predictor.py](distilbert_predictor.py): deep analysis

## Important classes
- `Settings` in [config.py](config.py): env-based app configuration
- `AnalyzeRequest` in [routers/api.py](routers/api.py): request schema
- `HealthResponse` in [routers/api.py](routers/api.py): health response schema
- `FakeNewsPredictor` in [predictor.py](predictor.py): runtime ensemble engine
- `DistilBertPredictor` in [distilbert_predictor.py](distilbert_predictor.py): transformer inference engine

## API endpoints
Verified from [routers/api.py](routers/api.py):

- `GET /health`
  - returns app status, whether models loaded, uptime

- `GET /models/info`
  - returns model metadata with accuracy values

- `POST /analyze`
  - expects JSON with `title` and `text`
  - returns ensemble label, confidence, model votes, processing time

- `POST /analyze/deep`
  - expects same payload
  - returns DistilBERT label and confidence
  - rate-limited separately

One technical note:
The README says “3 specialized endpoints,” but the actual code has four routes: health, models info, analyze, and analyze/deep. That means the README wording is slightly simplified, but the code is the source of truth.

---

# 6. CORE FEATURES

These are the major features that actually exist in the project:

## 1. Six-model ML ensemble
The project trains and uses six models:
- Logistic Regression
- Decision Tree
- Gradient Boosting
- Random Forest
- Naive Bayes
- Linear SVC

This is defined in [train.py](train.py) and [predictor.py](predictor.py).

## 2. TF-IDF + n-gram text representation
The vectorizer uses:
- `TfidfVectorizer`
- `ngram_range=(1, 2)`
- `max_features=150_000`
- `min_df=2`
- `max_df=0.95`

This is in [train.py](train.py).

## 3. Preprocessing with spaCy
The project:
- lowercases text
- removes URLs and HTML tags
- strips punctuation
- removes digits
- lowercases
- lemmatizes
- removes stopwords
- combines title and text

This is in [preprocessor.py](preprocessor.py).

## 4. Weighted voting ensemble
The final decision is not a simple majority vote. It uses model accuracy as weight.

This is in [predictor.py](predictor.py):
- each model gets a weight from `model_meta.json`
- fake and real totals are accumulated by weighted vote
- final verdict is the side with larger total weight

## 5. Confidence score
The app returns:
- `overall_confidence`
- per-model confidence
- fake_votes and real_votes

This is calculated in [predictor.py](predictor.py).

## 6. Health and metadata endpoints
The app exposes:
- health status
- model accuracy metadata
- readiness for deployment verification

## 7. DistilBERT “deep analysis”
This is an optional second model path using Hugging Face, via [distilbert_predictor.py](distilbert_predictor.py).

## 8. Frontend UI
The browser UI in [frontend/index.html](frontend/index.html) and [frontend/app.js](frontend/app.js):
- accepts article input
- runs analysis
- shows result
- shows recent history
- allows sample fake/real cases
- shows theme toggle and animated visuals

## 9. Rate limiting
`SlowAPI` is used to limit `/analyze` to 10 requests/min and `/analyze/deep` to 5 requests/min.

## 10. Docker and Render deployment support
Present in [Dockerfile](Dockerfile) and [render.yaml](render.yaml).

---

# 7. MACHINE LEARNING / AI

## Dataset
The dataset is expected to be in:
- [data/Fake.csv](data/Fake.csv)
- [data/True.csv](data/True.csv)

In [train.py](train.py), the code:
- reads both CSVs
- assigns fake = 0, true = 1
- concatenates them
- shuffles them
- fills missing values
- uses title and text columns

If the dataset is not present, [download_data.py](download_data.py) tries to download it; if it fails, it creates a sample dataset.

Important fact:
There is no evidence in the code of a large custom dataset being tracked or versioned here. It either downloads external data or falls back to sample data.

## Features
The features are the processed article text, not a structured list of metadata fields.

The main feature logic is:
- title and text combined
- repeated title three times for stronger headline weighting
- lowercased and cleaned
- stopwords removed
- lemmatized
- vectorized with TF-IDF

This is in [preprocessor.py](preprocessor.py) and [train.py](train.py).

## Preprocessing
Detailed steps:
- remove HTML tags
- remove URLs
- remove punctuation
- remove numbers
- remove non-letter content
- lowercase
- apply spaCy tokenization and lemmatization
- remove stopwords and words shorter than 3 characters

Then `combined = f"{title} {title} {title} {text}"` is used to weight headlines.

## Models
The six trained models from [train.py](train.py):

- Logistic Regression
- Decision Tree
- Gradient Boosting
- Random Forest
- Multinomial Naive Bayes
- Linear SVC

The model names and exact configuration are hardcoded in `MODELS_CFG`.

## Training process
1. Dataset is loaded
2. Data is balanced by class
3. Missing values are filled
4. Text is cleaned and lemmatized
5. Train/test split is created
6. TF-IDF vectorizer is fitted on training data
7. Each model is trained on vectorized text
8. Predictions are made on test data
9. Accuracy and classification report are computed
10. Model metadata is saved

This is all in [train.py](train.py).

## Evaluation metrics
The code computes:
- accuracy
- weighted precision
- weighted recall
- weighted F1-score

These are saved to [models/model_meta.json](models/model_meta.json) and returned by `/models/info`.

## Exact results present in code
The file [models/model_meta.json](models/model_meta.json) contains:

- Logistic Regression: 97.53% accuracy, 97.53% F1
- Decision Tree: 97.60% accuracy, 97.60% F1
- Gradient Boosting: 98.50% accuracy, 98.51% F1
- Random Forest: 96.91% accuracy, 96.91% F1
- Naive Bayes: 95.17% accuracy, 95.17% F1
- Linear SVC: 98.06% accuracy, 98.06% F1

Those are the exact current verified model metrics in the repository.

## DistilBERT accuracy claim
The README says:
- DistilBERT is a fine-tuned model with 99.97% accuracy
- model is hosted on Hugging Face

But the code in [distilbert_predictor.py](distilbert_predictor.py) does not run training or evaluation on the local project. It only loads a pre-trained model from Hugging Face. So this claim is documented in the README, but not validated by an actual training/evaluation script in this codebase.

Therefore:
- DistilBERT usage: supported
- 99.97% accuracy value: PARTIALLY SUPPORTED or NOT VERIFIED as a local code fact

## Why each model was chosen
From the actual code:
- Logistic Regression: strong linear baselines for text classification
- Decision Tree: simple interpretable rule-based baseline
- Gradient Boosting: high-performing non-linear learner
- Random Forest: ensemble of trees
- Naive Bayes: strong for text and sparse features
- Linear SVC: effective on sparse high-dimensional text data

This is a reasonable set, but the code does not document an ablation study. So “why chosen” is inferred from the actual implementation and common scikit-learn usage, not from an explicit evaluation comparison file.

## Problems or limitations
Actual limitations visible in the code:
- If dataset is missing, it either downloads it or uses a tiny sample dataset
- The project is English-only because of spaCy `en_core_web_sm`
- DistilBERT is optional and can fail if `transformers` is missing
- Startup loads all models, which increases memory usage
- The app has no true database or user tracking
- The project is a binary fake-vs-real classifier; it does not do multi-label misinformation types, source validation, or evidence checking

---

# 8. TECHNICAL DECISIONS

## Why this framework?
FastAPI is used because:
- clean REST API
- built-in validation via Pydantic
- easy HTTP handling
- modern Python support
- easy frontend integration
- good deployment fit

Alternative could have been Flask or Django. Those are valid alternatives, but the code uses FastAPI and its docs/validation fit this project well.

## Why this model stack?
The code uses a classic ML ensemble plus a deep model:
- classic models for speed and explainability
- DistilBERT for second opinion and contextual understanding

Alternative would have been:
- single stronger model only
- pure transformer pipeline only
- LSTM/GRU
- BERT-only

The project purposely uses both because of speed + coverage.

## Why this database?
There is no database.

The actual design choice is file-based persistence:
- vectorizer saved as `.pkl`
- models saved as `.pkl`
- metadata saved as JSON

This is simpler than a database for a small ML service.

Alternative database choices would have been SQLite, PostgreSQL, or cloud storage, but they are not used here.

## Why this algorithm?
TF-IDF with bigrams was chosen because:
- text classification is sparse and high-dimensional
- bigrams capture some phrase-level patterns
- it is simple and effective
- it fits the project’s lightweight runtime

Alternative approaches include:
- word embeddings
- BOW only
- transformers only
- custom handcrafted features

## Why this preprocessing?
The project uses spaCy because:
- lemmatization reduces word-form noise
- stopword removal helps focus on meaningful terms
- title weighting improves detection because headlines often carry signal

This is a clear design choice in [preprocessor.py](preprocessor.py).

---

# 9. CHALLENGES

## Challenge 1: missing model files at startup
Problem:
The app may start without model artifacts.

Cause:
The code expects `models/` files to exist.

Solution:
In [app.py](app.py), the startup lifecycle checks for models and runs `python train.py` if they are missing.

Trade-off:
- startup is more robust
- but training may add delay if artifacts are absent

## Challenge 2: missing or broken dataset
Problem:
No dataset file may be available.

Cause:
[download_data.py](download_data.py) handles external download failures and sample fallback.

Solution:
It tries to download from a public URL and then falls back to a small embedded dataset.

Trade-off:
- more portability
- but accuracy is reduced when sample data is used

## Challenge 3: first-request latency from spaCy and transformer models
Problem:
The first call can be slow because large models are loaded on first use.

Cause:
spaCy model and DistilBERT are large.

Solution:
The project pre-warms spaCy in [app.py](app.py) and logs that it is loaded at startup. DistilBERT load is also attempted early.

Trade-off:
- startup is slower
- runtime is faster after warm-up

## Challenge 4: rate limiting
Problem:
The API could be abused by repeated calls.

Cause:
Large inference endpoints can be expensive.

Solution:
SlowAPI is used in [routers/api.py](routers/api.py) and [app.py](app.py) to limit requests.

Trade-off:
- protects resources
- but reduces free usage for legitimate clients

## Challenge 5: model confidence and voting logic
Problem:
Different models may disagree.

Cause:
Each classifier has different strengths and probabilities.

Solution:
The project computes weighted accuracy voting and confidence is based on winner share of total model weights.

Trade-off:
- better robustness than simple majority
- more complexity than plain voting

---

# 10. TESTING AND DEPLOYMENT

## Tests
The project includes tests in:
- [tests/test_api.py](tests/test_api.py)
- [tests/test_nasa.py](tests/test_nasa.py)

Framework:
- `pytest`
- `fastapi.testclient`

These tests validate:
- health endpoint
- model metadata endpoint
- fake news / real news API response
- frontend HTML serving
- a NASA real news sample

## Test framework
`pytest` is in [requirements.txt](requirements.txt), and the CI pipeline in [.github/workflows/ci.yml](.github/workflows/ci.yml) runs:
`python -m pytest -v tests/test_api.py`

## Important edge cases
From the tests and app code:
- text must be at least 20 characters
- model metadata endpoint fails if models are not loaded
- frontend must serve HTML
- a real-world article like NASA launch must be classified as real news
- fake sample article must be classified as fake
- health check must return status

## Docker
The project includes [Dockerfile](Dockerfile), which:
- uses `python:3.11-slim`
- installs requirements
- downloads `en_core_web_sm`
- exposes port 8000
- runs the app via Gunicorn + Uvicorn

## CI/CD
The GitHub workflow in [.github/workflows/ci.yml](.github/workflows/ci.yml) does:
- checkout code
- set up Python 3.11
- install dependencies
- install spaCy model
- run tests

## Deployment
Deployment config is in [render.yaml](render.yaml):
- Python service
- install dependencies
- install spaCy model
- download models
- start Gunicorn

The README also claims this app is deployed on Render, and the code config matches that setup.

## Verification status
The environment here could not run current tests because `pytest` is missing in the local `.venv`.

This is not a code failure; it is a local environment issue.

---

# 11. RESUME VERIFICATION

I do not have the actual resume text in the workspace, so I am verifying the project against the project’s own claims in [README.md](README.md), as well as common resume claims that match the implemented code.

## Common resume claims

### “Fake News Detection API”
Status: Fully supported

Evidence:
- [app.py](app.py)
- [routers/api.py](routers/api.py)
- [README.md](README.md)

### “FastAPI backend”
Status: Fully supported

Evidence:
- [app.py](app.py)
- [routers/api.py](routers/api.py)

### “Machine learning ensemble”
Status: Fully supported

Evidence:
- [train.py](train.py)
- [predictor.py](predictor.py)
- [models/model_meta.json](models/model_meta.json)

### “6-model ensemble”
Status: Fully supported

Evidence:
- `MODEL_KEYS = ["lr", "dt", "gbc", "rfc", "nb", "svc"]` in [predictor.py](predictor.py)

### “spaCy NLP preprocessing”
Status: Fully supported

Evidence:
- [preprocessor.py](preprocessor.py)

### “Rate limiting”
Status: Fully supported

Evidence:
- `@limiter.limit` in [routers/api.py](routers/api.py)
- `SlowAPIMiddleware` in [app.py](app.py)

### “Docker support”
Status: Fully supported

Evidence:
- [Dockerfile](Dockerfile)

### “Deployment on Render”
Status: Fully supported

Evidence:
- [render.yaml](render.yaml)

### “DistilBERT deep analysis”
Status: Partially supported

Evidence:
- [distilbert_predictor.py](distilbert_predictor.py) clearly implements this
- but it depends on `transformers` being installed and the model being reachable
- the README’s specific accuracy number is not verifiable in this workspace as a computed local metric

### “99.97% accuracy”
Status: Partially supported / NOT VERIFIED locally

Evidence:
- README claims it
- no local evaluation script proves this in the project
- the actual saved model metrics in [models/model_meta.json](models/model_meta.json) are lower and are the verified numbers

### “Production-grade”
Status: Partially supported

Evidence:
- rate limiting, logging, startup load, Docker, CI, deployment config exist
- but no full production observability stack or DB-based user system is in the code

### “Live deployment”
Status: Supported by config, but not verified from a running app in this environment

Evidence:
- [render.yaml](render.yaml)
- [README.md](README.md)
- not directly tested in this session

### “Database-backed system”
Status: Not supported

Evidence:
- no database usage anywhere in code

### “5-model frontend description”
Status: Partially supported, but misleading

Evidence:
- front-end copy says “5 ML Models” in [frontend/index.html](frontend/index.html)
- code actually trains 6 models in [train.py](train.py) and [predictor.py](predictor.py)

This is a documentation mismatch.

---

# 12. INTERVIEW PREPARATION

Below are project-specific questions and answers.

1. What problem does this project solve?
Simple answer: It decides if a news article is fake or real.
Technical answer: It preprocesses news text, vectorizes it, runs six model classifiers, and combines their weighted outputs.
Follow-up: What happens if the input is very short?

2. Why is fake news detection a text classification problem?
Simple answer: The input is text, and the output is a class label.
Technical answer: The app converts cleaned text into TF-IDF features and predicts binary labels 0/1.
Follow-up: Why not use raw text directly?

3. What is the main entry point?
Simple answer: The app starts in [app.py](app.py).
Technical answer: It creates the FastAPI app, loads models at startup, serves frontend, and includes the router.
Follow-up: What runs on startup?

4. What does `lifespan` do?
Simple answer: It loads models before serving requests.
Technical answer: It triggers `predictor.load()`, prewarms spaCy, and tries to load DistilBERT.
Follow-up: Why warm the model at startup?

5. What is `preprocess()` doing?
Simple answer: It cleans and normalizes article text.
Technical answer: It lowercases text, strips punctuation, removes URLs and numbers, and lemmatizes with spaCy.
Follow-up: Why use title weighting?

6. Why is the title repeated three times?
Simple answer: To give headlines stronger weight because they often signal the story’s meaning.
Technical answer: In [preprocessor.py](preprocessor.py), the title is repeated three times before cleaning.
Follow-up: Does this create bias?

7. What is the role of TF-IDF?
Simple answer: It turns words into numbers the model can understand.
Technical answer: `TfidfVectorizer` fits on the processed training text and creates sparse numeric features.
Follow-up: Why not use bag-of-words?

8. Why use a six-model ensemble?
Simple answer: Different models see the data differently.
Technical answer: Each classifier votes and the final result is weighted by its historical accuracy.
Follow-up: What if one model is much weaker?

9. Why use weighted voting rather than simple majority?
Simple answer: More accurate models should count more.
Technical answer: `FakeNewsPredictor.predict()` uses `self.meta[key]["accuracy"]` as the weight.
Follow-up: Is there any tie risk?

10. What are the model weights based on?
Simple answer: Each model’s stored accuracy from `model_meta.json`.
Technical answer: The app loads metadata and uses it to compute `fake_weight_sum` and `real_weight_sum`.
Follow-up: What if metadata is missing?

11. What files store the trained models?
Simple answer: They live in [models](models).
Technical answer: The vectorizer and each classifier are saved via `joblib.dump(...)`.
Follow-up: Why not use a database?

12. What is the role of `download_data.py`?
Simple answer: It prepares the dataset.
Technical answer: It downloads or builds a fallback dataset if the expected CSV files are missing.
Follow-up: What happens if download fails?

13. What is the role of `download_models.py`?
Simple answer: It ensures model artifacts are present.
Technical answer: It checks the vectorizer size and downloads model files from GitHub Releases if the local files are invalid.
Follow-up: Why validate by file size?

14. Why does the app rate-limit `/analyze`?
Simple answer: To prevent abuse and resource overload.
Technical answer: `SlowAPI` applies a limit of 10 per minute on the route.
Follow-up: What is the trade-off?

15. Why is `AnalyzeRequest` validating text length?
Simple answer: To reject weak inputs and keep the API consistent.
Technical answer: It requires text length >= 20 and strips whitespace.
Follow-up: Why not accept empty input?

16. What happens when a request is invalid?
Simple answer: FastAPI returns validation errors.
Technical answer: Pydantic raises a `ValueError` before the model is called.
Follow-up: Which field is enforced?

17. What happens on `/health`?
Simple answer: It returns status and uptime.
Technical answer: It reads `predictor.loaded` and the process start time.
Follow-up: Why is that useful in deployment?

18. What is `/models/info`?
Simple answer: It exposes trained model metrics.
Technical answer: It returns JSON from `predictor.get_model_info()`.
Follow-up: What does this help with in production?

19. What is `/analyze/deep`?
Simple answer: It runs DistilBERT for deeper classification.
Technical answer: It calls `distilbert_predictor.predict_distilbert(...)` with the same article input.
Follow-up: What if `transformers` is not installed?

20. Why is DistilBERT optional?
Simple answer: The code checks if the transformer library is available.
Technical answer: In [distilbert_predictor.py](distilbert_predictor.py), `TRANSFORMERS_AVAILABLE` is set on import and the model is skipped otherwise.
Follow-up: Does this make the app less reliable?

21. Why use `joblib` instead of pickle?
Simple answer: It is common for scikit-learn objects.
Technical answer: The project saves vectorizers and models using `joblib.dump`.
Follow-up: Why choose file persistence instead of DB?

22. What is the biggest ML decision in this project?
Simple answer: It uses an accuracy-weighted ensemble.
Technical answer: The final label is a weighted combination of six model votes.
Follow-up: Why is this better than a single model?

23. Which model is likely strongest in this project?
Simple answer: Based on the saved metadata, Gradient Boosting is highest at 98.50% accuracy.
Technical answer: [models/model_meta.json](models/model_meta.json) confirms it.
Follow-up: But does the app actually choose it automatically?

24. Why use spaCy instead of pure regex preprocessing?
Simple answer: It gives better language-aware normalization.
Technical answer: It lemmatizes and removes stopwords correctly with a production NLP pipeline.
Follow-up: Why not build custom NLP rules only?

25. What is the main limitation of the current dataset?
Simple answer: It may fallback to a small sample dataset if the full dataset is unavailable.
Technical answer: [download_data.py](download_data.py) creates sample data if download fails.
Follow-up: How does this affect accuracy?

26. Why does the app include a frontend at all?
Simple answer: To make the system usable to non-developers.
Technical answer: It serves static files from [frontend/index.html](frontend/index.html) and [frontend/app.js](frontend/app.js).
Follow-up: Does the frontend call the API directly?

27. How does the frontend show confidence?
Simple answer: It animates the gauge and vote counts.
Technical answer: `renderResults()` updates the progress bar and text.
Follow-up: Where is the backend output used?

28. Why do tests mock the predictor?
Simple answer: The tests focus on API behavior, not model internals.
Technical answer: In [tests/test_api.py](tests/test_api.py), the predictor is patched to simulate results.
Follow-up: Is this a real end-to-end test?

29. What are the real runtime dependencies?
Simple answer: FastAPI, scikit-learn, spaCy, pydantic, loguru, slowapi, joblib, and optionally transformers.
Technical answer: They are listed in [requirements.txt](requirements.txt).
Follow-up: Is there a database dependency?

30. What would you improve next?
Simple answer: I would add better model validation, stronger data quality controls, and more transparent explanations.
Technical answer: The project currently does not provide per-token explanations or source verification.
Follow-up: Which improvement would produce the biggest gain?

31. Why is this a good interview project?
Simple answer: It shows end-to-end ML engineering.
Technical answer: It combines data prep, model training, deployment, API design, full-stack frontend, testing, and infrastructure config.
Follow-up: Which part demonstrates the strongest engineering ability?

32. What is the biggest risk in the current design?
Simple answer: The project relies heavily on external data availability and model files.
Technical answer: If datasets or model artifacts are missing, it falls back to sample data or downloads them.
Follow-up: How would you harden it for production?

---

# 13. FINAL FACT SHEET

## Project problem
Fake news detection using article text classification to decide whether a story is fake or real.

## Input
- article title (optional, but used)
- article text
- minimum text length: 20 characters
- request format from the API: JSON with `title` and `text`

## Processing
- strip whitespace
- clean punctuation and noise
- remove URLs, numbers, special characters
- lemmatize with spaCy
- combine title and text
- TF-IDF vectorization with bigrams
- six-model ensemble inference
- weighted voting by model accuracy
- optional DistilBERT deep analysis

## Output
- `ensemble_label`: “FAKE NEWS” or “REAL NEWS”
- `ensemble_is_fake`: boolean
- `overall_confidence`: percentage
- `fake_votes` and `real_votes`
- per-model breakdown
- `processing_time_ms`
- `processed_length`

## Technologies
- FastAPI
- Uvicorn/Gunicorn
- scikit-learn
- spaCy
- pandas
- numpy
- joblib
- Pydantic
- SlowAPI
- Loguru
- pytest
- Hugging Face Transformers / DistilBERT
- Docker
- Render

## Architecture
- frontend sends API requests
- FastAPI validates and routes
- ensemble predictor loads models
- text is preprocessed and vectorized
- six classifiers vote
- weighted result returned to UI
- DistilBERT route offers an alternate deeper analysis

## Best technical decision
The strongest design choice is the accuracy-weighted ensemble. It is simple, explainable, and gives better robustness than a single model.

## Biggest challenge
The project must reliably handle missing datasets and missing model artifacts, then recover by downloading or falling back to sample data.

## Biggest limitation
The code is clearly aimed at English-language text and depends on external download availability and model artifact existence. There is no database and no true source-verification pipeline.

## Future improvement
I would add:
- better dataset quality control
- model explainability
- stronger monitoring
- a database for usage analytics
- more robust offline fallback and retraining pipeline

## Exact results/metrics
Verified from [models/model_meta.json](models/model_meta.json):
- Logistic Regression: 97.53%
- Decision Tree: 97.60%
- Gradient Boosting: 98.50%
- Random Forest: 96.91%
- Naive Bayes: 95.17%
- Linear SVC: 98.06%

The DistilBERT “99.97%” value is in [README.md](README.md), but not verified by a training/evaluation script in this workspace.

## 10 things I must remember for the interview
1. The app is a fake-news classifier for article text.
2. It uses a six-model ensemble, not a single model.
3. Preprocessing is done with spaCy and title weighting.
4. TF-IDF bigram features are central to the classic pipeline.
5. Model accuracy is used as the voting weight.
6. It exposes a REST API and a browser UI.
7. There is no database in the actual codebase.
8. DistilBERT is an optional second model path.
9. The project includes Docker and Render deployment config.
10. The local environment here failed to run pytest because `pytest` is not installed, so the code exists and tests are written, but the environment is not currently set up to execute them.

---

# Quick oral interview summary

If I had to explain this project in one sentence, it is:

A FastAPI fake-news detection app that cleans article text, builds TF-IDF features, runs an accuracy-weighted ensemble of six models, and returns a fake/real verdict with confidence via a web UI and API.
