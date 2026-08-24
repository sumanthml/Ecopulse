"""
EcoPulse API - Predictions & AI Insights
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from app.core.database import get_db
from app.services.prediction_service import prediction_service
from app.ml.anomaly_detection import anomaly_detector
from app.ai.insight_generator import generate_environmental_insight
from app.services.insight_service import get_insights
from app.schemas.insight import InsightGenerateRequest

predictions_router = APIRouter(prefix="/api/predictions", tags=["Predictions"])
insights_router = APIRouter(prefix="/api/ai-insights", tags=["AI Insights"])


# ── Prediction Routes ──

@predictions_router.get("")
async def get_predictions(
    location_id: UUID,
    target: str = Query("pm25", pattern="^(pm25|aqi)$"),
    db: AsyncSession = Depends(get_db),
):
    """Get predictions for a location."""
    data = await prediction_service.predict(db, location_id, target)
    return {"success": True, "data": data}


@predictions_router.post("/train")
async def train_model(
    location_id: UUID,
    target: str = Query("pm25", pattern="^(pm25|aqi)$"),
    days: int = Query(30, ge=7, le=90),
    db: AsyncSession = Depends(get_db),
):
    """Train a prediction model for a location."""
    data = await prediction_service.train_model(db, location_id, target, days)
    return {"success": True, "data": data}


@predictions_router.get("/anomalies")
async def detect_anomalies(
    location_id: UUID,
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
):
    """Detect anomalies in recent pollution data."""
    data = await anomaly_detector.detect_anomalies(db, location_id, lookback_hours=hours)
    return {"success": True, "data": data, "message": f"{len(data)} anomalies detected"}


# ── AI Insight Routes ──

@insights_router.get("")
async def list_insights(
    location_id: Optional[UUID] = None,
    insight_type: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get environmental insights."""
    data = await get_insights(db, location_id, insight_type, limit)
    return {"success": True, "data": data}


@insights_router.post("/generate")
async def generate_insight(
    request: InsightGenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Generate a new AI environmental insight."""
    data = await generate_environmental_insight(
        db, request.location_id, request.insight_type, request.force
    )
    if data and "error" in data:
        return {"success": False, "error": {"code": "AI_ERROR", "message": data["error"]}}
    return {"success": True, "data": data, "message": "Insight generated"}
