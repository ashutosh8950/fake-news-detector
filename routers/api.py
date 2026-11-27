import os
import secrets
import time
from typing import Any

from fastapi import APIRouter, HTTPException, Request, Response
from loguru import logger
from pydantic import BaseModel, Field, RootModel, field_validator
from slowapi import Limiter
from slowapi.util import get_remote_address

from distilbert_predictor import distilbert_predictor
from predictor import predictor

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

START_TIME = time.time()

# ── Metrics counters ──────────────────────────────────────────────────────────
_metrics = {"total": 0, "fake": 0, "real": 0, "confidence_sum": 0.0}
METRICS_ACCESS_TOKEN = os.environ.get("METRICS_ACCESS_TOKEN")

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


class ErrorResponse(BaseModel):
    detail: str | None = None
    error: str | None = None
    message: str | None = None
    request_id: str | None = None


class ModelPrediction(BaseModel):
    name: str
    label: str
    is_fake: bool
    confidence: float


class AnalyzeResponse(BaseModel):
    ensemble_is_fake: bool
    ensemble_label: str
    overall_confidence: float
    fake_votes: int
    real_votes: int
    total_models: int
    models: dict[str, ModelPrediction]
    processed_length: int
    processing_time_ms: float


class DeepAnalyzeResponse(BaseModel):
    label: str
    confidence: float
    processing_time_ms: float


class ModelInfo(BaseModel):
    name: str
    accuracy: float
    brier_score: float | None = None
    calibration_method: str | None = None


class ModelsInfoResponse(RootModel[dict[str, ModelInfo]]):
    """Named root model so the existing dynamic model-key JSON is preserved."""


ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    401: {"model": ErrorResponse},
    404: {"model": ErrorResponse},
    422: {"model": ErrorResponse},
    429: {"model": ErrorResponse},
    500: {"model": ErrorResponse},
    503: {"model": ErrorResponse},
}

# ── Routes ────────────────────────────────────────────────────────────────────
@router.get(
    "/health",
    response_model=HealthResponse,
    responses={503: {"description": "Application is available but trusted model artifacts are not ready."}},
    tags=["System"],
)
async def health(response: Response):
    ready = bool(predictor.loaded)
    response.status_code = 200 if ready else 503
    return {
        "status":         "ok" if ready else "not_ready",
        "models_loaded":  ready,
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "api_version":    "2.0.0",
    }

@router.get(
    "/models/info",
    response_model=ModelsInfoResponse,
    responses=ERROR_RESPONSES,
    tags=["System"],
)
async def models_info():
    """Return accuracy statistics for all trained models."""
    if not predictor.loaded:
        raise HTTPException(
            503,
            "Model information unavailable: trusted model artifacts are not ready.",
        )
    return predictor.get_model_info()

@router.get("/metrics", response_model=MetricsResponse, tags=["System"])
async def metrics_endpoint(request: Request):
    """Return metrics only when deployment config supplies a bearer token."""
    if not METRICS_ACCESS_TOKEN:
        raise HTTPException(status_code=404, detail="Not found")

    scheme, _, supplied_token = request.headers.get("Authorization", "").partition(" ")
    if scheme.lower() != "bearer" or not supplied_token or not secrets.compare_digest(
        supplied_token, METRICS_ACCESS_TOKEN
    ):
        raise HTTPException(
            status_code=401,
            detail="Metrics authorization required",
            headers={"WWW-Authenticate": "Bearer"},
        )

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

@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    responses={
        **ERROR_RESPONSES,
        503: {"model": ErrorResponse, "description": "Inference is unavailable until trusted model artifacts are ready."},
    },
    tags=["Detection"],
)
@limiter.limit("10/minute")
async def analyze(request: Request, req: AnalyzeRequest):
    """
    Analyze a news article and return ensemble fake/real prediction
    with confidence scores from each of the 5 production ML models.
    """
    if not predictor.loaded:
        raise HTTPException(
            503,
            "Inference unavailable: trusted model artifacts are not ready.",
        )

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

@router.post(
    "/analyze/deep",
    response_model=DeepAnalyzeResponse,
    responses=ERROR_RESPONSES,
    tags=["Detection"],
)
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
