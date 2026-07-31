import os
from loguru import logger
from transformers import pipeline

# Avoid tokenizers parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

class DistilBertPredictor:
    def __init__(self):
        self.classifier = None
        self.loaded = False

    def load(self):
        logger.info("Loading DistilBERT model from Hugging Face Hub (GuptaAshutosh/truthscan-fake-news-distilbert)...")
        try:
            self.classifier = pipeline(
                "text-classification",
                model="GuptaAshutosh/truthscan-fake-news-distilbert",
                tokenizer="GuptaAshutosh/truthscan-fake-news-distilbert",
                device=-1
            )
            self.loaded = True
            logger.info("✅ DistilBERT model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load DistilBERT model: {e}")
            self.loaded = False

    def predict_distilbert(self, title: str, text: str):
        if not self.loaded:
            raise RuntimeError("DistilBERT model not loaded")

        # Combine title 3x + text
        processed = f"{title} {title} {title} {text}"
        
        # Predict with truncation to 512 tokens
        result = self.classifier(processed, truncation=True, max_length=512)[0]
        
        # Map labels
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
