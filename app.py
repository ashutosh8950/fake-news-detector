"""
FastAPI REST API for Fake News Detection.
Serves both the REST API and the frontend static files.
"""

import os
import time
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from predictor import predictor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Lifespan (load models once at startup) ────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        predictor.load()
        logger.info("✅ Models loaded successfully")
    except FileNotFoundError:
        logger.warning("⚠️  Models not found — running train.py first...")
        import subprocess, sys
        subprocess.run([sys.executable, "train.py"], check=True)
        predictor.load()
    yield  # app runs here
    logger.info("🛑 Shutting down")

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Fake News Detector API",
    description="ML-powered fake news detection with ensemble voting across 5 models",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Schemas ───────────────────────────────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    text:  str  = Field(..., min_length=20,  description="Article body text")
    title: str  = Field("",  description="Optional article headline")

class HealthResponse(BaseModel):
    status:       str
    models_loaded: bool
    uptime_seconds: float

START_TIME = time.time()

# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health():
    return {
        "status":         "ok",
        "models_loaded":  predictor.loaded,
        "uptime_seconds": round(time.time() - START_TIME, 1),
    }

@app.get("/models/info", tags=["System"])
async def models_info():
    """Return accuracy statistics for all trained models."""
    if not predictor.loaded:
        raise HTTPException(503, "Models not loaded yet")
    return predictor.get_model_info()

@app.post("/analyze", tags=["Detection"])
async def analyze(req: AnalyzeRequest, request: Request):
    """
    Analyze a news article and return ensemble fake/real prediction
    with confidence scores from each of the 5 ML models.
    """
    if not predictor.loaded:
        raise HTTPException(503, "Models are loading, please try again in a moment")

    start = time.time()
    result = predictor.predict(title=req.title, text=req.text)
    result["processing_time_ms"] = round((time.time() - start) * 1000, 1)

    logger.info(
        f"Analyzed {'%.0f' % len(req.text)}ch → {result['ensemble_label']} "
        f"({result['overall_confidence']}%) in {result['processing_time_ms']}ms"
    )
    return result

# ── Serve Frontend ────────────────────────────────────────────────────────────
FRONTEND_DIR = "frontend"

if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def serve_frontend():
        index = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.exists(index):
            with open(index, encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        return HTMLResponse("<h1>Frontend not found</h1>", status_code=404)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
