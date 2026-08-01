import os
import requests
from loguru import logger

GITHUB_RELEASE_URL = "https://github.com/ashutosh8950/fake-news-detector/releases/download/v1.0-models"

MODEL_FILES = [
    "dt_model.pkl",
    "gbc_model.pkl",
    "lr_model.pkl",
    "model_meta.json",
    "nb_model.pkl",
    "rfc_model.pkl",
    "svc_model.pkl",
    "vectorizer.pkl"
]

def models_are_valid(models_dir):
    # vectorizer.pkl should be at least 5MB for real trained models
    # Sample data produces a tiny vectorizer under 1KB
    vectorizer_path = os.path.join(models_dir, "vectorizer.pkl")
    if not os.path.exists(vectorizer_path):
        return False
    size = os.path.getsize(vectorizer_path)
    logger.info(f"vectorizer.pkl size: {size} bytes")
    return size > 1_000_000  # Must be over 1MB to be real models

def download_models(models_dir="models"):
    os.makedirs(models_dir, exist_ok=True)
    
    if models_are_valid(models_dir):
        logger.info("Valid pre-trained models already exist. Skipping download.")
        return True
    
    logger.info("Models missing or invalid — downloading from GitHub Releases...")
    
    for filename in MODEL_FILES:
        dest = os.path.join(models_dir, filename)
        if os.path.exists(dest):
            logger.info(f"  {filename} already exists, skipping")
            continue
        url = f"{GITHUB_RELEASE_URL}/{filename}"
        logger.info(f"  Downloading {filename}...")
        try:
            response = requests.get(url, stream=True, timeout=120)
            response.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.info(f"  {filename} downloaded successfully")
        except Exception as e:
            logger.error(f"  Failed to download {filename}: {e}")
            return False
    
    logger.info("All models downloaded successfully!")
    return True

if __name__ == "__main__":
    download_models()
