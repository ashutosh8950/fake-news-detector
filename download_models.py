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

def download_models(models_dir="models"):
    os.makedirs(models_dir, exist_ok=True)
    
    all_exist = all(
        os.path.exists(os.path.join(models_dir, f))
        for f in MODEL_FILES
    )
    
    if all_exist:
        logger.info("Models already exist. Skipping download.")
        return True
    
    logger.info("Downloading pre-trained models from GitHub Releases...")
    
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
