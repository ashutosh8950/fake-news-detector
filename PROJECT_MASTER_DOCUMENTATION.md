# PROJECT_MASTER_DOCUMENTATION

## 1. Project Overview
The Fake News Detector is a production-grade web application and REST API designed to identify whether a news article is real or fake. It relies on a machine learning ensemble of 6 traditional ML algorithms combined with an independent deep learning transformer model (DistilBERT). The project features a backend built in FastAPI, Natural Language Processing (NLP) with spaCy, an interactive frontend, and a complete training pipeline.

## 2. Problem Solved
Misinformation and fake news are pervasive on the internet. This project solves the problem of automated fake news detection by analyzing the text and title of an article to determine its authenticity. It provides two layers of analysis:
- A high-speed, traditional ML ensemble approach.
- A highly accurate, transformer-based deep learning approach.

## 3. Features
- **6 ML Model Ensemble:** Utilizes Logistic Regression, Decision Tree, Gradient Boosting, Random Forest, Naive Bayes, and Linear SVC for voting-based prediction.
- **Deep Analysis:** A standalone `/analyze/deep` endpoint powered by a fine-tuned Hugging Face DistilBERT transformer.
- **spaCy NLP Pipeline:** Fast, production-ready lemmatization and stopword removal (`en_core_web_sm`).
- **Rate Limiting:** Protected with SlowAPI (10 requests/min for ensemble, 5 requests/min for deep analysis).
- **Input Validation:** Strict sanitization using Pydantic V2 validators.
- **Structured Logging:** Asynchronous logs using Loguru.
- **Web UI:** A dynamic frontend UI featuring animated particle backgrounds, real-time gauges, and history tracking.
- **CI/CD & Docker:** Automated testing via GitHub Actions and fully containerized deployment.

## 4. Technologies Used
- **Backend:** Python 3.11, FastAPI, Uvicorn, Gunicorn
- **Machine Learning (Ensemble):** scikit-learn, joblib, pandas, numpy
- **Machine Learning (Deep):** Hugging Face `transformers`, PyTorch
- **NLP:** spaCy (`en_core_web_sm`), `re`
- **Frontend:** Vanilla JavaScript, HTML5, CSS3
- **Validation & Settings:** Pydantic
- **Rate Limiting:** SlowAPI
- **Testing:** pytest, httpx

## 5. High-Level Architecture
The system consists of three main architectural components:
1. **The Model Training Pipeline:** Standalone scripts (`download_data.py`, `train.py`) that fetch data, preprocess it using spaCy, train 6 scikit-learn models (along with a TF-IDF vectorizer), and persist them to disk. (The DistilBERT model was fine-tuned externally and is loaded from the Hugging Face hub).
2. **The FastAPI Backend:** A web server that loads the serialized models into memory at startup. It exposes REST API endpoints for health checks, model metadata, and text analysis.
3. **The Static Frontend:** HTML, CSS, and JS files served directly by FastAPI. It makes asynchronous fetch requests to the REST API and dynamically renders the prediction results.

## 6. Repository Structure
```text
.
├── .github/              # GitHub Actions workflows (CI/CD)
├── data/                 # Raw datasets (Fake.csv, True.csv) (Ignored in git)
├── frontend/             # Static web assets (HTML, CSS, JS)
├── models/               # Serialized scikit-learn models and metadata
├── routers/              # FastAPI router modules
├── tests/                # Pytest test suites
├── app.py                # Main FastAPI application entry point
├── config.py             # Pydantic configuration settings
├── distilbert_predictor.py # DistilBERT model wrapper and logic
├── download_data.py      # Dataset downloader script
├── predictor.py          # TF-IDF + Ensemble models wrapper and logic
├── preprocessor.py       # spaCy text cleaning and lemmatization pipeline
├── train.py              # ML ensemble training script
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker image definition
└── README.md             # Project documentation
```

## 7. Folder-by-Folder Explanation
- **`.github/workflows/`**: Contains `ci.yml` which runs the pytest suite automatically on push/pull requests.
- **`data/`**: Stores the raw `Fake.csv` and `True.csv` data used for local training.
- **`frontend/`**: Contains the client-side user interface (`index.html`, `style.css`, `app.js`).
- **`models/`**: Directory where `train.py` saves the trained `.pkl` models, vectorizer, and `model_meta.json`.
- **`routers/`**: Contains API route definitions to keep `app.py` clean.
- **`tests/`**: Contains unit and integration tests using `pytest` and `httpx` to verify API functionality.

## 8. File-by-File Explanation
- **`app.py`**: The FastAPI application instance. Handles startup (lifespan) model loading, CORS, exception handling, rate limiting middleware, mounts the API router, and serves the static frontend.
- **`config.py`**: Defines the `Settings` class using Pydantic, loading environment variables (e.g., from `.env`).
- **`distilbert_predictor.py`**: Wraps the Hugging Face `pipeline` for the DistilBERT model, handling loading from the hub and executing predictions with a 512 token truncation limit.
- **`download_data.py`**: Script to download the fake news dataset from a public Hugging Face URL. Includes a fallback small embedded dataset if the download fails.
- **`predictor.py`**: Wraps the 6 scikit-learn models and the TF-IDF vectorizer. Handles ensemble voting logic, probability extraction, and confidence weighting.
- **`preprocessor.py`**: Text cleaning pipeline. Uses regex to strip HTML, URLs, and punctuation, then applies spaCy to lemmatize tokens and remove stopwords.
- **`train.py`**: Executes the training workflow. Loads data, applies `preprocessor.py`, trains a bigram TF-IDF vectorizer and 6 classification algorithms, evaluates them, and serializes the artifacts to the `models/` directory.
- **`routers/api.py`**: Defines the FastAPI endpoints: `/health`, `/models/info`, `/analyze`, and `/analyze/deep`.
- **`frontend/app.js`**: Client-side logic for the UI. Handles DOM manipulation, form submission, particle canvas background, and localStorage history.

## 9. Entry Points
- **Web Server:** `python app.py` (Starts Uvicorn server).
- **Training Pipeline:** `python train.py` (Trains the ML ensemble).
- **Data Download:** `python download_data.py` (Fetches dataset).
- **Tests:** `python -m pytest -v tests/` (Runs test suite).

## 10. Startup Sequence
When `app.py` is executed (Application Start):
1. **Config Load:** `config.py` initializes Pydantic `Settings`.
2. **FastAPI Initialization:** The `app` object is created with a `lifespan` context manager.
3. **Middleware:** CORS and SlowAPI (rate limiting) middleware are attached.
4. **Lifespan Trigger (Pre-flight):** 
   - `predictor.load()` is called to load TF-IDF models from disk into memory. (If missing, it automatically triggers `train.py`).
   - `preprocess("warmup", "warmup text")` is called to pre-load the spaCy model into memory, preventing first-request latency.
   - `distilbert_predictor.load()` is called, which downloads/loads the DistilBERT model via Hugging Face `pipeline`.
   - Start-up logs output the accuracy of the loaded models.
5. **Ready:** The Uvicorn server begins listening on the configured port.

## 11. Module Documentation
### `routers/api.py`
**Purpose:** Handles all incoming HTTP requests for the application's REST API.
**Main Components:**
- `AnalyzeRequest` / `HealthResponse`: Pydantic schemas validating request/response bodies.
- `health()`: Returns system status and uptime.
- `models_info()`: Returns accuracy metadata for the ensemble models.
- `analyze()`: The primary endpoint. Preprocesses the text and queries the `predictor` ensemble.
- `analyze_deep()`: The secondary endpoint. Queries the `distilbert_predictor`.

### `preprocessor.py`
**Purpose:** Sanitizes and standardizes natural language text before vectorization.
**Main Components:**
- `clean_text(text)`: Regex-based stripping of URLs, brackets, HTML, punctuation, and standalone numbers.
- `lemmatize_text(text)`: spaCy-based lemmatization and stopword removal.
- `preprocess(title, text)`: Combines title (weighted 3x) and text, passing it through cleaning and lemmatization.

## 12. Function Documentation

### `FakeNewsPredictor.predict(self, title, text)`
- **Purpose:** Produces an ensemble prediction from 6 underlying ML models.
- **Parameters:** `title` (str), `text` (str).
- **Logic:**
  1. Calls `preprocess(title, text)`.
  2. Vectorizes the text using the loaded TF-IDF vectorizer.
  3. Iterates through the 6 loaded models, obtaining the prediction (0 or 1) and a confidence score (`predict_proba` or sigmoid-scaled `decision_function`).
  4. Accumulates weighted scores based on each model's historical accuracy (retrieved from metadata).
  5. Determines the winner (Fake or Real) based on the highest accumulated weight.
  6. Calculates overall confidence as the winner's weight percentage of the total weight.
- **Return Value:** A dictionary containing the ensemble label, confidence, per-model predictions, and vote counts.

### `DistilBertPredictor.predict_distilbert(self, title, text)`
- **Purpose:** Produces a prediction using the fine-tuned DistilBERT transformer.
- **Parameters:** `title` (str), `text` (str).
- **Logic:**
  1. Combines the title (weighted 3x) and text (without spaCy lemmatization, as transformers prefer raw natural language).
  2. Passes the string to the Hugging Face `pipeline` with `truncation=True` and `max_length=512`.
  3. Maps the resulting label ("LABEL_0" -> FAKE, "LABEL_1" -> REAL).
- **Return Value:** A dictionary containing the label and confidence percentage.

### `download_full_dataset()`
- **Purpose:** Attempts to download the WELFake dataset from a Hugging Face URL.
- **Logic:** Streams the CSV using `requests`, parses it with `pandas`, filters columns, assigns 'FAKE'/'REAL' based on labels, and writes `Fake.csv` and `True.csv` to the `data/` folder. Returns boolean indicating success.

## 13. Class Documentation
### `FakeNewsPredictor` (in `predictor.py`)
- **Purpose:** Singleton wrapper for managing the scikit-learn ensemble.
- **Attributes:** `vectorizer`, `models` (Dict), `meta` (Dict), `loaded` (bool).
- **Methods:** `load()` (Reads `.pkl` files using `joblib`), `predict()` (Executes the ensemble logic), `get_model_info()` (Returns metadata).
- **Lifecycle:** Instantiated once globally. Models are loaded during the FastAPI lifespan.

### `DistilBertPredictor` (in `distilbert_predictor.py`)
- **Purpose:** Singleton wrapper for managing the Hugging Face transformer pipeline.
- **Attributes:** `classifier`, `loaded` (bool).
- **Methods:** `load()` (Initializes the pipeline), `predict_distilbert()`.
- **Lifecycle:** Instantiated once globally. Models are loaded during the FastAPI lifespan.

## 14. Complete Execution Flow (Prediction)
1. **Client:** User pastes an article into `frontend/index.html` and clicks Analyze.
2. **Frontend:** `app.js` intercepts the submit event, validates text length (>20 chars), and sends a `POST /analyze` request.
3. **Backend Route:** `api.py` receives the request. The Pydantic schema `AnalyzeRequest` sanitizes whitespace and validates constraints.
4. **Rate Limiting:** SlowAPI middleware verifies the IP hasn't exceeded 10 req/min.
5. **Business Logic:** `predictor.predict(title, text)` is invoked.
6. **NLP Preprocessing:** Text is sent to `preprocessor.py` to be regex-cleaned and lemmatized by spaCy.
7. **Vectorization:** Text is transformed into a sparse matrix by the TF-IDF vectorizer.
8. **Inference:** All 6 scikit-learn models predict on the vector.
9. **Ensemble:** The accuracy-weighted voting algorithm determines the final label.
10. **Response:** Route formats the result, appends `processing_time_ms`, and returns JSON.
11. **Frontend Render:** `app.js` parses the JSON, animates the gauge, updates the per-model progress bars, and saves the result to `localStorage`.

## 15. Complete Data Flow
`Raw Text` -> `app.js` -> `HTTP POST` -> `FastAPI/Pydantic (String Validation)` -> `preprocessor.py (Regex/spaCy)` -> `Cleaned Tokens` -> `TfidfVectorizer` -> `Sparse Array / Float Matrix` -> `Scikit-learn Models` -> `Predictions/Probabilities` -> `Ensemble Aggregation` -> `JSON Response` -> `app.js (DOM Update)`.

## 16. Business Logic
- **Headline Weighting:** The title is concatenated 3 times to the body text during preprocessing to artificially inflate the TF-IDF importance of headline words, as fake news often features highly sensationalized headlines.
- **Weighted Ensemble:** Instead of a simple majority vote (which can result in ties), the ensemble utilizes a weighted voting system. Each model's vote is multiplied by its overall accuracy on the test set (e.g., a 98% accurate model has more say than a 95% accurate model).
- **Transformer NLP Context:** The DistilBERT model explicitly *avoids* the spaCy lemmatization pipeline, as transformer models rely on natural sentence structure and positional encoding, which lemmatization destroys.

## 17. APIs
### `GET /health`
Returns system status.
Response: `{"status": "ok", "models_loaded": true, "uptime_seconds": 12.3}`

### `GET /models/info`
Returns accuracy statistics for the 6 ML models.

### `POST /analyze`
Rate-limited (10/min). Accepts title/text. Returns ensemble result.
Request: `{"title": "...", "text": "..."}`
Response: `{"ensemble_label": "FAKE", "overall_confidence": 98.4, "models": {...}, ...}`

### `POST /analyze/deep`
Rate-limited (5/min). Uses DistilBERT.
Request: `{"title": "...", "text": "..."}`
Response: `{"label": "FAKE", "confidence": 99.9, "processing_time_ms": 250}`

## 18. Database & Storage
- **INFERRED:** There is no SQL/NoSQL database used in this project.
- **Storage:** Client-side prediction history is stored in the browser's `localStorage`. Model weights are stored on the local filesystem as `.pkl` files and `model_meta.json`. 

## 19. Configuration
Managed by `config.py` (Pydantic `BaseSettings`):
- `app_name`: "Fake News Detection API"
- `environment`: (default: "development")
- `models_dir`: "models"
- `data_dir`: "data"
Additionally, CORS is configurable via the `ALLOWED_ORIGINS` environment variable (parsed in `app.py`). `PORT` configures the Uvicorn listening port.

## 20. Dependencies
**Core:**
- `fastapi`, `uvicorn[standard]`, `gunicorn`, `python-multipart` (Web server setup)
- `scikit-learn`, `pandas`, `numpy`, `joblib` (Traditional ML stack)
- `spacy` (NLP preprocessing)
- `transformers`, `torch` (Deep learning stack)
**Utilities:**
- `loguru` (Logging)
- `slowapi` (Rate limiting)
- `pydantic-settings` (Config)
- `pytest`, `httpx` (Testing)

## 21. Security
- **Rate Limiting:** Protects the analysis endpoints from DDoS and spam.
- **Input Validation:** Pydantic strictly enforces string lengths, preventing memory exhaustion from massive payload injections.
- **CORS:** Controlled via environment variables to restrict origins in production.

## 22. Performance
- **Pre-warming:** The spaCy model is executed once during application startup. Loading spaCy lazy on the first request historically caused a 4+ second latency spike. Pre-warming ensures the first user request is instantaneous.
- **Model Loading:** Models are loaded into memory globally at startup, meaning inference times are extremely fast (~10-20ms for the ensemble).
- **DistilBERT Truncation:** The Deep Analysis route truncates input strictly to 512 tokens to prevent out-of-memory errors and bound processing time.

## 23. Error Handling
- **Global Exception Handler:** Catches unhandled exceptions in `app.py` and returns a formatted JSON 500 error instead of leaking raw stack traces.
- **Not Loaded States:** If the prediction endpoints are hit before models are fully loaded, an HTTP 503 Service Unavailable error is raised.
- **Rate Limit Handlers:** Standard HTTP 429 Too Many Requests responses provided by SlowAPI.

## 24. Testing
- `tests/test_api.py`: Validates the health, models info, and API endpoints using `httpx.AsyncClient`. Includes specific tests for mocking fake and real news inputs.
- `tests/test_nasa.py`: An integration test verifying edge case handling (ensuring a factual NASA article isn't falsely flagged as fake).

## 25. Design Decisions
- **Separation of Preprocessing:** `preprocessor.py` was separated out to ensure that the exact same cleaning pipeline applied to the dataset during `train.py` is applied to user input during `predictor.py` inference. Mismatched preprocessing is a major cause of model degradation in production.
- **Avoiding Sentence-Transformers:** The DistilBERT model was implemented directly via the Hugging Face `transformers` pipeline rather than `sentence-transformers`, as mixing `sentence-transformers` (which uses heavy PyTorch/OpenMP threading) with `scikit-learn` on Windows causes severe segmentation faults/access violations.

## 26. Project Relationships
- `app.py` depends on `routers/api.py`.
- `routers/api.py` depends on `predictor.py` and `distilbert_predictor.py`.
- `predictor.py` and `train.py` depend on `preprocessor.py`.
- `train.py` depends on `download_data.py`.

## 27. Glossary
- **spaCy:** An open-source software library for advanced NLP.
- **Lemmatization:** The process of grouping together the inflected forms of a word (e.g., "running" -> "run").
- **TF-IDF:** Term Frequency-Inverse Document Frequency. A numerical statistic intended to reflect how important a word is to a document in a collection or corpus.
- **DistilBERT:** A smaller, faster, cheaper, and lighter version of BERT (Bidirectional Encoder Representations from Transformers) used for deep NLP tasks.
