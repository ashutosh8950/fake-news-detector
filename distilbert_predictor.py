import os
from loguru import logger

os.environ["TOKENIZERS_PARALLELISM"] = "false"

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("transformers not installed. DistilBERT endpoint unavailable.")

class DistilBertPredictor:
    def __init__(self):
        self.classifier = None
        self.loaded = False

    def load(self):
        if not TRANSFORMERS_AVAILABLE:
            logger.warning("Skipping DistilBERT load — transformers not installed")
            return
        try:
            logger.info("Loading DistilBERT from Hugging Face...")
            self.classifier = pipeline(
                "text-classification",
                model="GuptaAshutosh/truthscan-fake-news-distilbert",
                tokenizer="GuptaAshutosh/truthscan-fake-news-distilbert",
                device=-1
            )
            self.loaded = True
            logger.info("DistilBERT loaded successfully")
        except Exception as e:
            logger.warning(f"DistilBERT failed to load: {e}")
            self.loaded = False

    def predict_distilbert(self, title: str, text: str):
        if not self.loaded:
            raise RuntimeError("DistilBERT model not loaded")
        processed = f"{title} {title} {title} {text}"
        result = self.classifier(processed, truncation=True, max_length=512)[0]
        label_raw = result['label']
        if label_raw in ["LABEL_0", "0"]:
            label = "FAKE"
        elif label_raw in ["LABEL_1", "1"]:
            label = "REAL"
        else:
            label = label_raw
        return {
            "label": label,
            "confidence": round(result['score'] * 100, 1)
        }

distilbert_predictor = DistilBertPredictor()
