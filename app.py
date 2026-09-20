"""
FastAPI REST API for Fake News Detection.
Serves both the REST API and the frontend static files.
Fixes applied:
  - spaCy pre-warm at startup (eliminates 4s first-request latency)
  - Configurable CORS via ALLOWED_ORIGINS env var
  - Startup log showing all model accuracies + server URL
"""

import os
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from predictor import predictor
from preprocessor import preprocess
from distilbert_predictor import distilbert_predictor
from routers.api import router as api_router, limiter
from config import settings
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

# ── Lifespan (load models once at startup) ────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Download models from GitHub Releases if not present ──────
    logger.info("Checking for pre-trained models...")

    # ── Load calibrated models; fail fast if deployment artifacts are absent ──
    try:
        predictor.load()
        logger.info("Models loaded successfully")
    except FileNotFoundError as exc:
        raise RuntimeError(
            "Calibrated models not found. Run: python download_models.py"
        ) from exc

    # ── spaCy pre-warm (loads model into memory) ──
    try:
        preprocess("warmup", "warmup text for spacy pre-warming")
        logger.info("spaCy pre-warmed successfully")
    except Exception as e:
        logger.warning(f"spaCy pre-warm failed (non-fatal): {e}")

    # ── Load DistilBERT ──────────────────────────────────────────
    try:
        distilbert_predictor.load()
    except Exception as e:
        logger.warning(f"DistilBERT failed to load (non-fatal): {e}")

    # ── Startup summary log ──────────────────────────────────────
    logger.info("--- Model Accuracies at Startup ---")
    for key, info in predictor.meta.items():
        logger.info(f"  {info.get('name', key):<22} accuracy={info.get('accuracy', 0):.2f}%  f1={info.get('f1', 0):.2f}%")
        
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Server ready at http://localhost:{port}")
    logger.info(f"API docs at   http://localhost:{port}/docs")

    yield  # app runs here
    logger.info("Shutting down")

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    description="ML-powered fake news detection with ensemble voting across 5 models",
    version="2.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter


def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    """Return a friendly structured 429 while preserving limiter headers."""
    limiter_response = _rate_limit_exceeded_handler(request, exc)
    retry_after_header = limiter_response.headers.get("Retry-After")
    retry_after_seconds = None
    if retry_after_header:
        try:
            retry_after_seconds = max(0, int(retry_after_header))
        except ValueError:
            pass

    headers = {
        key: value
        for key, value in limiter_response.headers.items()
        if key.lower() not in {"content-length", "content-type"}
    }
    return JSONResponse(
        status_code=429,
        headers=headers,
        content={
            "error": "rate_limited",
            "message": (
                "You're sending requests too quickly. "
                "Please wait a moment and try again."
            ),
            "retry_after_seconds": retry_after_seconds,
        },
    )


app.add_exception_handler(RateLimitExceeded, rate_limit_exception_handler)
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = uuid.uuid4().hex
    logger.exception(f"Unhandled exception request_id={request_id}: {exc}")
    return JSONResponse(
        status_code=500,
        headers={"X-Request-ID": request_id},
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred. Please try again.",
            "request_id": request_id,
        },
    )


# ── CORS — configurable via ALLOWED_ORIGINS env var ──────────────────────────
PRODUCTION_ORIGIN = "https://truthscan-fake-news-detector.onrender.com"
runtime_environment = os.environ.get("ENVIRONMENT", "production").lower()
default_origins = [PRODUCTION_ORIGIN]
if runtime_environment in {"development", "local", "test"}:
    default_origins.extend([
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ])

_raw_origins = os.environ.get("ALLOWED_ORIGINS")
ALLOWED_ORIGINS = (
    [origin.strip() for origin in _raw_origins.split(",") if origin.strip()]
    if _raw_origins
    else default_origins
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include Routers ───────────────────────────────────────────────────────────
app.include_router(api_router)

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
