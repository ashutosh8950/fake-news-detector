import time
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, field_validator
from loguru import logger

from predictor import predictor
from distilbert_predictor import distilbert_predictor
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

START_TIME = time.time()

# ── Metrics counters ──────────────────────────────────────────────────────────
_metrics = {"total": 0, "fake": 0, "real": 0, "confidence_sum": 0.0}

# ── Schemas ───────────────────────────────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    text:  str  = Field(..., max_length=10000, description="Article body text")
    title: str  = Field("",  max_length=500, description="Optional article headline")

    @field_validator('text', 'title', mode='before')
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator('text')
    @classmethod
    def check_length(cls, v: str) -> str:
        if len(v) < 20:
            raise ValueError("Article text must be at least 20 characters")
        return v

class HealthResponse(BaseModel):
    status:        str
    models_loaded: bool
    uptime_seconds: float
    api_version:   str = "2.0.0"

class MetricsResponse(BaseModel):
    total_requests: int
    fake_detected:  int
    real_detected:  int
    avg_confidence: float
    uptime_seconds: float
    models_loaded:  bool
    api_version:    str

# ── Routes ────────────────────────────────────────────────────────────────────
@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health():
    return {
        "status":         "ok",
        "models_loaded":  predictor.loaded,
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "api_version":    "2.0.0",
    }

@router.get("/models/info", tags=["System"])
async def models_info():
    """Return accuracy statistics for all trained models."""
    if not predictor.loaded:
        raise HTTPException(503, "Models not loaded yet")
    return predictor.get_model_info()

@router.get("/metrics", response_model=MetricsResponse, tags=["System"])
async def metrics_endpoint():
    """Return API usage statistics and health metrics."""
    total = _metrics["total"]
    avg_conf = round(_metrics["confidence_sum"] / total, 2) if total > 0 else 0.0
    return {
        "total_requests": total,
        "fake_detected":  _metrics["fake"],
        "real_detected":  _metrics["real"],
        "avg_confidence": avg_conf,
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "models_loaded":  predictor.loaded,
        "api_version":    "2.0.0",
    }

@router.post("/analyze", tags=["Detection"])
@limiter.limit("10/minute")
async def analyze(request: Request, req: AnalyzeRequest):
    """
    Analyze a news article and return ensemble fake/real prediction
    with confidence scores from each of the 5 production ML models.
    """
    if not predictor.loaded:
        raise HTTPException(503, "Models are still loading, please try again")

    start = time.time()
    try:
        result = predictor.predict(title=req.title, text=req.text)
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(500, "Analysis failed, please try again")

    result["processing_time_ms"] = round((time.time() - start) * 1000, 1)

    _metrics["total"] += 1
    _metrics["fake" if result["ensemble_is_fake"] else "real"] += 1
    _metrics["confidence_sum"] += result["overall_confidence"]

    logger.info(
        f"Analyzed {len(req.text)}ch -> {result['ensemble_label']} "
        f"({result['overall_confidence']}%) in {result['processing_time_ms']}ms"
    )
    return result

@router.post("/analyze/deep", tags=["Detection"])
@limiter.limit("5/minute")
async def analyze_deep(request: Request, req: AnalyzeRequest):
    """
    Analyze a news article using ONLY the DistilBERT model.
    """
    if not distilbert_predictor.loaded:
        raise HTTPException(503, "DistilBERT model unavailable on this deployment. Use /analyze instead.")

    start = time.time()
    try:
        result = distilbert_predictor.predict_distilbert(title=req.title, text=req.text)
    except Exception as e:
        logger.error(f"DistilBERT prediction failed: {e}")
        raise HTTPException(500, "Analysis failed, please try again")

    processing_time_ms = round((time.time() - start) * 1000, 1)

    logger.info(
        f"Deep Analyzed {len(req.text)}ch -> {result['label']} "
        f"({result['confidence']}%) in {processing_time_ms}ms"
    )

    return {
        "label": result["label"],
        "confidence": result["confidence"],
        "processing_time_ms": processing_time_ms
    }
