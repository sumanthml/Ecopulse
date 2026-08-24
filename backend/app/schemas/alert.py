"""
EcoPulse Pydantic Schemas - Alert
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class AlertCreate(BaseModel):
    sensor_id: Optional[UUID] = None
    location_id: UUID
    parameter: str
    value: float
    threshold: float
    severity: str = Field("LOW", pattern="^(INFO|LOW|MODERATE|HIGH|CRITICAL)$")
    title: str
    message: Optional[str] = None


class AlertResponse(BaseModel):
    id: UUID
    sensor_id: Optional[UUID] = None
    location_id: UUID
    parameter: str
    value: float
    threshold: float
    severity: str
    title: str
    message: Optional[str] = None
    status: str
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    # Enriched
    location_name: Optional[str] = None
    city: Optional[str] = None
    sensor_code: Optional[str] = None

    model_config = {"from_attributes": True}


class AlertUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(ACTIVE|ACKNOWLEDGED|RESOLVED)$")
