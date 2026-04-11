# 🔍 TruthScan — AI Fake News Detector

> Advanced ML-powered fake news detection with an ensemble of 5 models, deployed as a beautiful web application.

![Python](https://img.shields.io/badge/Python-3.11-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green) ![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5-orange)

---

## ✨ Features

| Feature | Details |
|---|---|
| **5 ML Models** | Logistic Regression, Decision Tree, Gradient Boosting, Random Forest, Naive Bayes |
| **Ensemble Voting** | Accuracy-weighted ensemble for best prediction |
| **Advanced Preprocessing** | NLTK lemmatization, stopword removal, title+text fusion |
| **Bigram TF-IDF** | 100K feature vectors with unigrams + bigrams |
| **REST API** | FastAPI with `/analyze`, `/health`, `/models/info` |
| **Premium UI** | Cyberpunk dark mode, animated particles, confidence gauges |
| **Deployment** | Free deployment on Render.com |

## 🚀 Quick Start (Local)

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Download dataset & train models
```bash
python download_data.py
python train.py
```
> Training downloads data automatically. For best accuracy (~99%), place `Fake.csv` and `True.csv` from [Kaggle](https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset) in the `data/` folder.

### 3. Run the server
```bash
python app.py
```

Open http://localhost:8000 in your browser. 🎉

---

## 🌐 Deploy to Render.com (Free)

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit — TruthScan"
   git remote add origin https://github.com/<YOUR_USERNAME>/fake-news-detector.git
   git push -u origin main
   ```

2. **Go to [render.com](https://render.com)** → New → Web Service

3. **Connect your GitHub repo**

4. **Settings** (auto-detected from `render.yaml`):
   - Build: `pip install ... && python download_data.py && python train.py`
   - Start: `gunicorn app:app -w 2 -k uvicorn.workers.UvicornWorker`
   - Plan: Free

5. **Deploy!** Render will build, download data, train models, and start the server.

---

## 📡 API Reference

### `POST /analyze`
```json
// Request
{ "title": "Optional headline", "text": "Article body (required, min 20 chars)" }

// Response
{
  "ensemble_is_fake": true,
  "ensemble_label": "FAKE NEWS",
  "overall_confidence": 87.3,
  "fake_votes": 4,
  "real_votes": 1,
  "total_models": 5,
  "models": {
    "lr":  { "name": "Logistic Regression", "label": "Fake", "confidence": 93.2 },
    "dt":  { "name": "Decision Tree",       "label": "Fake", "confidence": 100.0 },
    ...
  }
}
```

### `GET /health`
```json
{ "status": "ok", "models_loaded": true, "uptime_seconds": 123.4 }
```

### `GET /models/info`
```json
{
  "lr":  { "name": "Logistic Regression", "accuracy": 98.73, "f1": 98.72 },
  "rfc": { "name": "Random Forest",       "accuracy": 98.89, "f1": 98.89 },
  ...
}
```

---

## 📁 Project Structure

```
FAKE_NEWS_DETECTION/
├── app.py              # FastAPI server + static file serving
├── train.py            # Advanced training pipeline
├── predictor.py        # Ensemble prediction engine
├── preprocessor.py     # NLTK text preprocessing
├── download_data.py    # Auto dataset downloader
├── requirements.txt    # Python dependencies
├── render.yaml         # Render.com deployment config
├── frontend/
│   ├── index.html      # UI structure
│   ├── style.css       # Cyberpunk dark-mode design
│   └── app.js          # Frontend logic + API calls
├── data/               # CSV files (auto-created)
└── models/             # Trained model artifacts (auto-created)
```

---

## 🧠 How It Works

1. **Preprocessing**: Your article's title (2× weighting) and body are combined, lowercased, cleaned, lemmatized with NLTK, and stopwords removed.
2. **Vectorization**: Text is converted to a 100K-feature TF-IDF vector with bigrams for richer pattern recognition.
3. **5-Model Ensemble**: Five independent classifiers each vote Fake/Real with a confidence score.
4. **Weighted Voting**: The ensemble uses each model's training accuracy as its vote weight.
5. **Result**: Final label + confidence percentage + per-model breakdown returned as JSON.

## 📊 Expected Accuracy

| Model | Accuracy (Full Dataset) |
|---|---|
| Logistic Regression | ~98.7% |
| Decision Tree | ~99.1% |
| Gradient Boosting | ~99.4% |
| Random Forest | ~98.9% |
| Naive Bayes | ~96.2% |
| **Ensemble** | **~99.3%** |

> Note: Accuracy is high on this dataset, but real-world performance depends on article domain. The model was trained on US political news (2015–2018).
