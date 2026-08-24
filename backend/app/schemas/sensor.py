"""
EcoPulse Pydantic Schemas - Sensor
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from uuid import UUID


class SensorCreate(BaseModel):
    location_id: UUID
    sensor_code: str
    sensor_name: str
    source: str = Field("SIMULATED", pattern="^(REAL|SIMULATED|API|HISTORICAL)$")
    sensor_type: str = "multi-pollutant"
    status: str = Field("ONLINE", pattern="^(ONLINE|OFFLINE|WARNING|MAINTENANCE)$")
    installation_date: Optional[date] = None


class SensorResponse(BaseModel):
    id: UUID
    location_id: UUID
    sensor_code: str
    sensor_name: str
    source: str
    sensor_type: str
    status: str
    last_seen: Optional[datetime] = None
    installation_date: Optional[date] = None
    created_at: datetime

    # Enriched fields
    location_name: Optional[str] = None
    city: Optional[str] = None
    current_aqi: Optional[int] = None
    health_score: Optional[float] = None

    model_config = {"from_attributes": True}


class SensorUpdate(BaseModel):
    sensor_name: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(ONLINE|OFFLINE|WARNING|MAINTENANCE)$")
    source: Optional[str] = Field(None, pattern="^(REAL|SIMULATED|API|HISTORICAL)$")
    sensor_type: Optional[str] = None
