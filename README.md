# 🔍 TruthScan — AI Fake News Detector

> Modern ML-powered fake news detection API with an ensemble of 6 models, built for speed and reliability.

---

## 🛠️ Tech Stack

- **FastAPI** — High-performance async web framework for the REST API
- **spaCy** — Industrial-strength NLP for blazing fast text preprocessing
- **scikit-learn** — Machine learning pipeline and ensemble models
- **Loguru** — Clean and structured logging
- **Pydantic Settings** — Robust configuration and environment variable management
- **Pytest** — Comprehensive unit and integration testing

---

## 📁 Project Structure

```
FAKE_NEWS_DETECTION/
├── app.py                 # FastAPI application and lifespan manager
├── config.py              # Pydantic-based configuration (environment variables)
├── download_data.py       # Script to download the Kaggle dataset
├── predictor.py           # Core ML prediction engine with 6-model ensemble
├── preprocessor.py        # NLP pipeline utilizing spaCy (cleaning & lemmatization)
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
├── train.py               # Optimized training pipeline for the ML models
│
├── data/                  # Dataset storage directory
│   ├── Fake.csv
│   └── True.csv
│
├── frontend/              # Vanilla JavaScript & HTML/CSS web interface
│   ├── app.js
│   ├── index.html
│   └── style.css
│
├── models/                # Trained ML artifacts and metadata
│   ├── dt_model.pkl
│   ├── gbc_model.pkl
│   ├── lr_model.pkl
│   ├── model_meta.json
│   ├── nb_model.pkl
│   ├── rfc_model.pkl
│   ├── svc_model.pkl
│   └── vectorizer.pkl
│
├── routers/               # Modularized FastAPI routes
│   └── api.py             # API endpoints (/health, /models/info, /analyze)
│
└── tests/                 # Test suite
    ├── __init__.py
    ├── test_api.py        # API endpoint unit tests
    └── test_nasa.py       # End-to-end integration test (NASA Real News)
```

---

## 🚀 How to Install and Run Locally

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Download the NLP Model
Download the English spaCy model required for preprocessing:
```bash
python -m spacy download en_core_web_sm
```

### 3. Download Data and Train Models
Download the dataset and train the 6 ensemble models:
```bash
python download_data.py
python train.py
```

### 4. Start the Server
Start the FastAPI server (runs on port 8000 by default):
```bash
python app.py
```
Open `http://localhost:8000` in your browser to view the interface.

---

## 🧪 How to Run Tests

The project includes a robust test suite powered by `pytest`. To verify the API and ML pipeline, run:

```bash
python -m pytest -v tests/
```

---

## 📡 API Endpoints

### `POST /analyze`
Analyzes text using the ensemble model and returns a fake/real prediction.
```json
// Request Example
{
  "title": "Optional headline",
  "text": "Article body (required, min 20 chars)"
}

// Response Example
{
  "ensemble_is_fake": true,
  "ensemble_label": "FAKE NEWS",
  "overall_confidence": 87.3,
  "fake_votes": 5,
  "real_votes": 1,
  "total_models": 6,
  "models": {
    "lr":  { "name": "Logistic Regression", "label": "Fake", "confidence": 93.2 },
    "dt":  { "name": "Decision Tree",       "label": "Fake", "confidence": 100.0 }
    // ... (other models)
  },
  "processing_time_ms": 45.2
}
```

### `GET /health`
System health check.
```json
// Response Example
{
  "status": "ok",
  "models_loaded": true,
  "uptime_seconds": 123.4
}
```

### `GET /models/info`
Returns statistics for all trained models.
```json
// Response Example
{
  "lr":  { "name": "Logistic Regression", "accuracy": 97.53, "f1": 97.53 },
  "dt":  { "name": "Decision Tree",       "accuracy": 97.6,  "f1": 97.6 }
  // ...
}
```

---

## 📊 Model Accuracy

*Accuracy statistics generated on the latest training run (from `models/model_meta.json`):*

| Model | Accuracy | F1-Score |
|---|---|---|
| **Logistic Regression** | 97.53% | 97.53% |
| **Decision Tree** | 97.60% | 97.60% |
| **Gradient Boosting** | 98.50% | 98.51% |
| **Random Forest** | 96.91% | 96.91% |
| **Naive Bayes** | 95.17% | 95.17% |
| **Linear SVC** | 98.06% | 98.06% |

---

## 🌐 Deployment

This application is designed to be easily deployed on **Render** (render.com). 
You can link your GitHub repository directly to Render as a Web Service. The startup script should first train the models or ensure they are present, and the start command will typically be `gunicorn app:app -w 2 -k uvicorn.workers.UvicornWorker`.
