import time
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, field_validator
from loguru import logger

from predictor import predictor
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

START_TIME = time.time()

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
    status:       str
    models_loaded: bool
    uptime_seconds: float

# ── Routes ────────────────────────────────────────────────────────────────────
@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health():
    return {
        "status":         "ok",
        "models_loaded":  predictor.loaded,
        "uptime_seconds": round(time.time() - START_TIME, 1),
    }

@router.get("/models/info", tags=["System"])
async def models_info():
    """Return accuracy statistics for all trained models."""
    if not predictor.loaded:
        raise HTTPException(503, "Models not loaded yet")
    return predictor.get_model_info()

@router.post("/analyze", tags=["Detection"])
@limiter.limit("10/minute")
async def analyze(request: Request, req: AnalyzeRequest):
    """
    Analyze a news article and return ensemble fake/real prediction
    with confidence scores from each of the 6 ML models.
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

    logger.info(
        f"Analyzed {len(req.text)}ch -> {result['ensemble_label']} "
        f"({result['overall_confidence']}%) in {result['processing_time_ms']}ms"
    )
    return result
