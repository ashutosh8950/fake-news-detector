import os
import sys
import requests
from loguru import logger

GITHUB_RELEASE_URL = "https://github.com/ashutosh8950/fake-news-detector/releases/download/v2.0-calibrated-models"

MODEL_FILES = [
    "lr_calibrated.pkl",
    "dt_calibrated.pkl",
    "gbc_calibrated.pkl",
    "nb_calibrated.pkl",
    "svc_calibrated.pkl",
    "vectorizer.pkl"
]
CALIBRATION_REPORT_FILE = "phase2_calibration_report.json"

def models_are_valid(models_dir, metadata_dir):
    vectorizer_path = os.path.join(models_dir, "vectorizer.pkl")
    report_path = os.path.join(metadata_dir, CALIBRATION_REPORT_FILE)
    if not os.path.exists(vectorizer_path) or not os.path.exists(report_path):
        return False
    size = os.path.getsize(vectorizer_path)
    logger.info(f"vectorizer.pkl size: {size} bytes")
    missing = [
        filename
        for filename in MODEL_FILES
        if not os.path.exists(os.path.join(models_dir, filename))
    ]
    if missing:
        logger.warning(f"Missing calibrated artifacts: {', '.join(missing)}")
        return False
    return size > 1_000_000

def download_models(models_dir="models/calibrated", metadata_dir="evaluation_results"):
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(metadata_dir, exist_ok=True)
    
    # Use lock file to prevent concurrent downloads from multiple workers
    lock_file = os.path.join(models_dir, ".download_lock")
    
    if models_are_valid(models_dir, metadata_dir):
        logger.info("Valid pre-trained models already exist. Skipping download.")
        return True
    
    # If another worker is already downloading wait for it
    if os.path.exists(lock_file):
        logger.info("Another worker is downloading models. Waiting...")
        import time
        for _ in range(60):  # Wait up to 60 seconds
            time.sleep(2)
            if models_are_valid(models_dir, metadata_dir):
                logger.info("Models downloaded by another worker. Proceeding.")
                return True
        logger.warning("Timeout waiting for models. Proceeding anyway.")
        return models_are_valid(models_dir, metadata_dir)
    
    # Create lock file
    with open(lock_file, "w") as f:
        f.write("downloading")
    
    try:
        logger.info("Models missing or invalid — cleaning up and downloading from GitHub Releases...")
        
        # Delete invalid calibrated model files before downloading replacements.
        for filename in MODEL_FILES:
            dest = os.path.join(models_dir, filename)
            if os.path.exists(dest):
                os.remove(dest)
                logger.info(f"  Removed invalid {filename}")
        
        # Download calibrated models and vectorizer from GitHub Releases.
        for filename in MODEL_FILES:
            dest = os.path.join(models_dir, filename)
            url = f"{GITHUB_RELEASE_URL}/{filename}"
            logger.info(f"  Downloading {filename}...")
            try:
                response = requests.get(url, stream=True, timeout=300)
                response.raise_for_status()
                with open(dest, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                size = os.path.getsize(dest)
                logger.info(f"  {filename} downloaded successfully ({size} bytes)")
            except Exception as e:
                logger.error(f"  Failed to download {filename}: {e}")
                return False

        # predictor.py reads this report from evaluation_results/ rather than
        # from the model directory, so it must be distributed as a release asset.
        report_dest = os.path.join(metadata_dir, CALIBRATION_REPORT_FILE)
        report_url = f"{GITHUB_RELEASE_URL}/{CALIBRATION_REPORT_FILE}"
        logger.info(f"  Downloading {CALIBRATION_REPORT_FILE}...")
        try:
            response = requests.get(report_url, stream=True, timeout=300)
            response.raise_for_status()
            with open(report_dest, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            size = os.path.getsize(report_dest)
            logger.info(f"  {CALIBRATION_REPORT_FILE} downloaded successfully ({size} bytes)")
        except Exception as e:
            logger.error(f"  Failed to download {CALIBRATION_REPORT_FILE}: {e}")
            return False
        
        logger.info("All models downloaded successfully!")
        return True
    finally:
        # Always remove lock file
        if os.path.exists(lock_file):
            os.remove(lock_file)

if __name__ == "__main__":
    success = download_models()
    sys.exit(0 if success else 1)
