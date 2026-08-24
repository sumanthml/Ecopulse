"""
EcoPulse Pydantic Schemas - Location
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class LocationCreate(BaseModel):
    name: str
    city: str
    state: Optional[str] = None
    country: str = "India"
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    description: Optional[str] = None


class LocationResponse(BaseModel):
    id: UUID
    name: str
    city: str
    state: Optional[str] = None
    country: str
    latitude: float
    longitude: float
    description: Optional[str] = None
    created_at: datetime

    # Optional enriched data
    sensor_count: Optional[int] = None
    online_sensors: Optional[int] = None
    current_aqi: Optional[int] = None
    aqi_category: Optional[str] = None

    model_config = {"from_attributes": True}


class LocationUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    description: Optional[str] = None
