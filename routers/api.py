import time
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from loguru import logger

from predictor import predictor

router = APIRouter()

START_TIME = time.time()

# ── Schemas ───────────────────────────────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    text:  str  = Field(..., min_length=20,  description="Article body text")
    title: str  = Field("",  description="Optional article headline")

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
async def analyze(req: AnalyzeRequest, request: Request):
    """
    Analyze a news article and return ensemble fake/real prediction
    with confidence scores from each of the 6 ML models.
    """
    if not predictor.loaded:
        raise HTTPException(503, "Models are loading, please try again in a moment")

    start = time.time()
    result = predictor.predict(title=req.title, text=req.text)
    result["processing_time_ms"] = round((time.time() - start) * 1000, 1)

    logger.info(
        f"Analyzed {len(req.text)}ch -> {result['ensemble_label']} "
        f"({result['overall_confidence']}%) in {result['processing_time_ms']}ms"
    )
    return result
