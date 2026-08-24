"""
EcoPulse Pydantic Schemas - Insight & User
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


# ── Insight Schemas ──

class InsightCreate(BaseModel):
    location_id: Optional[UUID] = None
    insight_type: str = Field("general", pattern="^(general|anomaly|daily_report|weekly_report|recommendation|trend|alert_explanation)$")
    title: str
    content: str
    severity: str = Field("INFO", pattern="^(INFO|LOW|MODERATE|HIGH|CRITICAL)$")
    generated_by: str = "groq"
    expires_at: Optional[datetime] = None


class InsightResponse(BaseModel):
    id: UUID
    location_id: Optional[UUID] = None
    insight_type: str
    title: str
    content: str
    severity: Optional[str] = None
    generated_by: str
    created_at: datetime
    expires_at: Optional[datetime] = None

    location_name: Optional[str] = None
    city: Optional[str] = None

    model_config = {"from_attributes": True}


class InsightGenerateRequest(BaseModel):
    location_id: UUID
    insight_type: str = "general"
    force: bool = False


# ── User Schemas ──

class UserCreate(BaseModel):
    name: str
    email: str
    password: str = Field(..., min_length=8)
    role: str = Field("viewer", pattern="^(admin|analyst|viewer)$")


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
