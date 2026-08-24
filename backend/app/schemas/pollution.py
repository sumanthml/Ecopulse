"""
EcoPulse Pydantic Schemas - Pollution & Readings
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class PollutionReadingCreate(BaseModel):
    """Schema for creating a new pollution reading."""
    sensor_id: UUID
    location_id: UUID
    timestamp: Optional[datetime] = None

    pm25: Optional[float] = Field(None, ge=0, le=1000, description="PM2.5 in µg/m³")
    pm10: Optional[float] = Field(None, ge=0, le=2000, description="PM10 in µg/m³")
    co: Optional[float] = Field(None, ge=0, le=100, description="CO in mg/m³")
    co2: Optional[float] = Field(None, ge=0, le=5000, description="CO2 in ppm")
    no2: Optional[float] = Field(None, ge=0, le=1000, description="NO2 in µg/m³")
    so2: Optional[float] = Field(None, ge=0, le=1000, description="SO2 in µg/m³")
    o3: Optional[float] = Field(None, ge=0, le=600, description="O3 in µg/m³")

    temperature: Optional[float] = Field(None, ge=-50, le=60, description="Temperature in °C")
    humidity: Optional[float] = Field(None, ge=0, le=100, description="Humidity in %")
    pressure: Optional[float] = Field(None, ge=900, le=1100, description="Pressure in hPa")
    wind_speed: Optional[float] = Field(None, ge=0, le=100, description="Wind speed in m/s")
    wind_direction: Optional[float] = Field(None, ge=0, le=360, description="Wind direction in degrees")
    noise_level: Optional[float] = Field(None, ge=0, le=200, description="Noise in dB")

    source: str = Field("SIMULATED", pattern="^(REAL|SIMULATED|API|HISTORICAL)$")

    model_config = {"json_schema_extra": {
        "example": {
            "sensor_id": "b1b2c3d4-e5f6-7890-abcd-ef1234567801",
            "location_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567801",
            "pm25": 78.2, "pm10": 124.5, "co": 1.2, "no2": 45.3, "so2": 12.1, "o3": 38.7,
            "temperature": 33.1, "humidity": 71.0, "pressure": 1013.2, "wind_speed": 2.4,
            "source": "SIMULATED"
        }
    }}


class PollutionReadingResponse(BaseModel):
    """Schema for a pollution reading response."""
    id: UUID
    sensor_id: UUID
    location_id: UUID
    timestamp: datetime

    pm25: Optional[float] = None
    pm10: Optional[float] = None
    co: Optional[float] = None
    co2: Optional[float] = None
    no2: Optional[float] = None
    so2: Optional[float] = None
    o3: Optional[float] = None

    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[float] = None
    noise_level: Optional[float] = None

    source: str
    created_at: datetime

    # AQI (joined)
    aqi: Optional[int] = None
    aqi_category: Optional[str] = None
    dominant_pollutant: Optional[str] = None

    model_config = {"from_attributes": True}


class AQIResponse(BaseModel):
    """AQI calculation result."""
    aqi: int
    category: str
    dominant_pollutant: Optional[str] = None
    sub_indices: Optional[dict] = None


class PollutionHistoryQuery(BaseModel):
    """Query params for pollution history."""
    location_id: Optional[UUID] = None
    sensor_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    pollutant: Optional[str] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)


class CurrentPollutionResponse(BaseModel):
    """Current pollution state for a location."""
    location_id: UUID
    location_name: str
    city: str
    latitude: float
    longitude: float
    aqi: Optional[int] = None
    category: Optional[str] = None
    dominant_pollutant: Optional[str] = None
    pm25: Optional[float] = None
    pm10: Optional[float] = None
    co: Optional[float] = None
    no2: Optional[float] = None
    so2: Optional[float] = None
    o3: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    last_updated: Optional[datetime] = None
    source: Optional[str] = None
    sensor_status: Optional[str] = None

    model_config = {"from_attributes": True}
