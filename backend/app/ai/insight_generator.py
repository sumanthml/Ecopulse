"""
EcoPulse AI Insight Generator
Orchestrates Groq AI calls for environmental intelligence.
"""
import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func

from app.ai.groq_client import generate_completion
from app.ai.prompts import (
    SYSTEM_PROMPT,
    environmental_summary_prompt,
    daily_report_prompt,
    anomaly_explanation_prompt,
    recommendation_prompt,
)
from app.models.pollution_reading import PollutionReading
from app.models.aqi_record import AQIRecord
from app.models.alert import Alert
from app.models.location import Location
from app.services.insight_service import store_insight, check_recent_insight

logger = logging.getLogger(__name__)


async def generate_environmental_insight(
    db: AsyncSession,
    location_id: uuid.UUID,
    insight_type: str = "general",
    force: bool = False,
) -> Optional[dict]:
    """
    Generate an AI environmental insight for a location.
    
    Only generates if:
        - No recent insight of same type exists (unless force=True)
        - There is sufficient data to analyze
        - Groq API is available
    """
    # Check for recent duplicate (avoid spam)
    if not force:
        has_recent = await check_recent_insight(db, location_id, insight_type)
        if has_recent:
            return {"skipped": True, "reason": "Recent insight already exists"}

    # Get location info
    loc_result = await db.execute(select(Location).where(Location.id == location_id))
    location = loc_result.scalar_one_or_none()
    if not location:
        return {"error": "Location not found"}

    # Build compact analytical summary
    summary_data = await _build_analytical_summary(db, location)

    if not summary_data:
        return {"error": "Insufficient data for analysis"}

    # Select prompt based on type
    if insight_type == "daily_report":
        prompt = daily_report_prompt(summary_data)
    elif insight_type == "recommendation":
        prompt = recommendation_prompt(summary_data)
    elif insight_type == "anomaly":
        prompt = anomaly_explanation_prompt(summary_data)
    else:
        prompt = environmental_summary_prompt(summary_data)

    # Generate AI insight
    content = await generate_completion(prompt, system_prompt=SYSTEM_PROMPT)

    if content is None:
        return {"error": "AI service temporarily unavailable"}

    # Determine severity based on AQI
    aqi = summary_data.get("current_aqi", 0) or 0
    severity = "INFO"
    if aqi > 200:
        severity = "CRITICAL"
    elif aqi > 150:
        severity = "HIGH"
    elif aqi > 100:
        severity = "MODERATE"

    # Store insight
    title = _generate_title(insight_type, location.name, summary_data)
    stored = await store_insight(
        db=db,
        location_id=location_id,
        insight_type=insight_type,
        title=title,
        content=content,
        severity=severity,
        generated_by="groq",
        expires_hours=24 if insight_type == "daily_report" else 12,
    )

    return {
        **stored,
        "content": content,
        "severity": severity,
        "data_summary": summary_data,
    }


async def _build_analytical_summary(db: AsyncSession, location: Location) -> Optional[dict]:
    """
    Build a compact analytical summary for AI consumption.
    
    Instead of sending thousands of readings, calculates key statistics.
    """
    now = datetime.now(timezone.utc)
    two_hours_ago = now - timedelta(hours=2)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Current reading
    current_result = await db.execute(
        select(PollutionReading)
        .where(PollutionReading.location_id == location.id)
        .order_by(desc(PollutionReading.timestamp))
        .limit(1)
    )
    current = current_result.scalar_one_or_none()

    if not current:
        return None

    # Current AQI
    aqi_result = await db.execute(
        select(AQIRecord)
        .where(AQIRecord.location_id == location.id)
        .order_by(desc(AQIRecord.calculated_at))
        .limit(1)
    )
    current_aqi = aqi_result.scalar_one_or_none()

    # 2-hour average PM2.5
    avg_result = await db.execute(
        select(func.avg(PollutionReading.pm25))
        .where(
            and_(
                PollutionReading.location_id == location.id,
                PollutionReading.timestamp >= two_hours_ago,
            )
        )
    )
    pm25_2h_avg = avg_result.scalar()

    # Previous AQI (2 hours ago)
    prev_aqi_result = await db.execute(
        select(AQIRecord)
        .where(
            and_(
                AQIRecord.location_id == location.id,
                AQIRecord.calculated_at <= two_hours_ago,
            )
        )
        .order_by(desc(AQIRecord.calculated_at))
        .limit(1)
    )
    prev_aqi = prev_aqi_result.scalar_one_or_none()

    # Today's stats
    today_readings = await db.execute(
        select(PollutionReading)
        .where(
            and_(
                PollutionReading.location_id == location.id,
                PollutionReading.timestamp >= today_start,
            )
        )
    )
    today_data = today_readings.scalars().all()

    # Alerts count
    alerts_result = await db.execute(
        select(func.count(Alert.id))
        .where(
            and_(
                Alert.location_id == location.id,
                Alert.created_at >= today_start,
            )
        )
    )
    alerts_count = alerts_result.scalar() or 0

    # Build summary
    current_aqi_val = current_aqi.aqi if current_aqi else None
    prev_aqi_val = prev_aqi.aqi if prev_aqi else None

    aqi_change = None
    if current_aqi_val and prev_aqi_val and prev_aqi_val > 0:
        aqi_change = round(((current_aqi_val - prev_aqi_val) / prev_aqi_val) * 100, 1)

    # Calculate daily stats
    pm25_values = [r.pm25 for r in today_data if r.pm25 is not None]
    aqi_values = []

    return {
        "location": f"{location.name}, {location.city}",
        "current_aqi": current_aqi_val,
        "aqi_category": current_aqi.category if current_aqi else None,
        "previous_aqi": prev_aqi_val,
        "aqi_change_percent": aqi_change,
        "dominant_pollutant": current_aqi.dominant_pollutant if current_aqi else None,
        "pm25_current": current.pm25,
        "pm25_average_2h": round(pm25_2h_avg, 1) if pm25_2h_avg else None,
        "pm10_current": current.pm10,
        "no2_current": current.no2,
        "so2_current": current.so2,
        "o3_current": current.o3,
        "co_current": current.co,
        "temperature": current.temperature,
        "humidity": current.humidity,
        "wind_speed": current.wind_speed,
        "avg_pm25": round(np.mean(pm25_values), 1) if pm25_values else None,
        "max_pm25": round(max(pm25_values), 1) if pm25_values else None,
        "total_readings": len(today_data),
        "alerts_count": alerts_count,
        "date": now.strftime("%Y-%m-%d"),
    }


def _generate_title(insight_type: str, location_name: str, data: dict) -> str:
    """Generate a descriptive title for the insight."""
    titles = {
        "general": f"Environmental Analysis — {location_name}",
        "daily_report": f"Daily Air Quality Report — {location_name}",
        "recommendation": f"Activity Recommendations — {location_name}",
        "anomaly": f"Anomaly Analysis — {location_name}",
        "trend": f"Pollution Trend Analysis — {location_name}",
        "alert_explanation": f"Alert Analysis — {location_name}",
    }
    return titles.get(insight_type, f"Environmental Insight — {location_name}")
