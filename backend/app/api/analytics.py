"""
EcoPulse API - Analytics
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.services.analytics_service import (
    get_analytics_summary,
    get_trends,
    get_correlation,
    get_pollution_heatmap,
)

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/summary")
async def analytics_summary(
    location_id: UUID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get comprehensive analytics summary for a location."""
    data = await get_analytics_summary(db, location_id, start_date, end_date)
    return {"success": True, "data": data}


@router.get("/trends")
async def analytics_trends(
    location_id: UUID,
    pollutant: str = Query("pm25"),
    aggregation: str = Query("hourly", pattern="^(hourly|daily|weekly)$"),
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
):
    """Get trend data for a specific pollutant."""
    data = await get_trends(db, location_id, pollutant, aggregation, days)
    return {"success": True, "data": data}


@router.get("/correlation")
async def analytics_correlation(
    location_id: UUID,
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
):
    """Get correlation analysis between pollutants."""
    data = await get_correlation(db, location_id, days)
    return {"success": True, "data": data}


@router.get("/heatmap")
async def analytics_heatmap(
    location_id: UUID,
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
):
    """Get time-based pollution heatmap (days × hours)."""
    data = await get_pollution_heatmap(db, location_id, days)
    return {"success": True, "data": data}
