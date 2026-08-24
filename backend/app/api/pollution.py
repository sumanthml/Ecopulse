"""
EcoPulse API - Pollution
Pollution reading endpoints: current, history, ingestion.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.core.database import get_db
from app.schemas.pollution import PollutionReadingCreate
from app.services.pollution_service import (
    ingest_reading,
    get_current_pollution,
    get_pollution_history,
)

router = APIRouter(prefix="/api/pollution", tags=["Pollution"])


@router.get("/current")
async def get_current(
    location_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get current pollution state for all or a specific location."""
    data = await get_current_pollution(db, location_id)
    return {"success": True, "data": data, "message": "Current pollution data retrieved"}


@router.get("/history")
async def get_history(
    location_id: Optional[UUID] = None,
    sensor_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Get historical pollution readings with filters."""
    data = await get_pollution_history(
        db, location_id, sensor_id, start_date, end_date, limit, offset
    )
    return {"success": True, "data": data, "message": f"{len(data)} readings retrieved"}


@router.post("/readings")
async def create_reading(
    reading: PollutionReadingCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Ingest a new pollution reading.
    
    Pipeline: validate → store → calculate AQI → check alerts → return
    """
    try:
        result = await ingest_reading(
            db=db,
            sensor_id=reading.sensor_id,
            location_id=reading.location_id,
            data=reading.model_dump(),
        )
        return {"success": True, "data": result, "message": "Reading ingested successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
