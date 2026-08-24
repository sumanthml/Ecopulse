"""
EcoPulse Alert Service
Configurable threshold-based alert generation.
"""
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.alert import Alert
from app.models.sensor import Sensor
from app.models.location import Location
from app.services.aqi_breakpoints import ALERT_THRESHOLDS

logger = logging.getLogger(__name__)


async def check_and_create_alerts(
    db: AsyncSession,
    sensor_id: uuid.UUID,
    location_id: uuid.UUID,
    reading_data: dict,
    aqi_value: Optional[int] = None,
) -> list[dict]:
    """
    Check reading values against configured thresholds and create alerts.
    
    Args:
        db: Database session
        sensor_id: UUID of the sensor
        location_id: UUID of the location
        reading_data: Dict of pollutant values (pm25, pm10, etc.)
        aqi_value: Calculated AQI value
    
    Returns:
        List of created alert dicts
    """
    created_alerts = []

    # Check pollutant thresholds
    for param, thresholds in ALERT_THRESHOLDS.items():
        if param == "aqi":
            value = aqi_value
        else:
            value = reading_data.get(param)

        if value is None:
            continue

        for threshold_config in thresholds:
            threshold = threshold_config["threshold"]
            if value >= threshold:
                # Check for recent duplicate alert (avoid spam)
                existing = await _check_recent_alert(
                    db, location_id, param, threshold
                )
                if existing:
                    continue

                # Get location name for message
                loc_result = await db.execute(
                    select(Location.name, Location.city).where(Location.id == location_id)
                )
                loc_row = loc_result.first()
                loc_name = f"{loc_row.name}" if loc_row else "Unknown"

                unit = _get_unit(param)
                alert = Alert(
                    id=uuid.uuid4(),
                    sensor_id=sensor_id,
                    location_id=location_id,
                    parameter=param.upper(),
                    value=round(value, 2),
                    threshold=threshold,
                    severity=threshold_config["severity"],
                    title=f"{threshold_config['label']}",
                    message=f"{param.upper()} at {loc_name} has reached {value:.1f}{unit}. "
                            f"Threshold: {threshold}{unit}. Severity: {threshold_config['severity']}.",
                    status="ACTIVE",
                    created_at=datetime.now(timezone.utc),
                )
                db.add(alert)
                created_alerts.append({
                    "id": str(alert.id),
                    "parameter": param.upper(),
                    "value": value,
                    "threshold": threshold,
                    "severity": threshold_config["severity"],
                    "title": alert.title,
                    "message": alert.message,
                })
                logger.info(f"Alert created: {alert.title} ({alert.severity})")
                break  # Only create alert for highest threshold exceeded

    if created_alerts:
        await db.flush()

    return created_alerts


async def _check_recent_alert(
    db: AsyncSession,
    location_id: uuid.UUID,
    parameter: str,
    threshold: float,
) -> bool:
    """Check if there's already an active alert for this parameter/threshold in the last 30 minutes."""
    from datetime import timedelta
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=30)

    result = await db.execute(
        select(Alert.id).where(
            and_(
                Alert.location_id == location_id,
                Alert.parameter == parameter.upper(),
                Alert.threshold == threshold,
                Alert.status == "ACTIVE",
                Alert.created_at >= cutoff,
            )
        ).limit(1)
    )
    return result.first() is not None


async def acknowledge_alert(db: AsyncSession, alert_id: uuid.UUID) -> Optional[dict]:
    """Acknowledge an alert."""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        return None

    alert.status = "ACKNOWLEDGED"
    alert.acknowledged_at = datetime.now(timezone.utc)
    await db.flush()

    return {"id": str(alert.id), "status": "ACKNOWLEDGED"}


async def resolve_alert(db: AsyncSession, alert_id: uuid.UUID) -> Optional[dict]:
    """Resolve an alert."""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        return None

    alert.status = "RESOLVED"
    alert.resolved_at = datetime.now(timezone.utc)
    await db.flush()

    return {"id": str(alert.id), "status": "RESOLVED"}


def _get_unit(param: str) -> str:
    """Get the unit string for a parameter."""
    units = {
        "pm25": " µg/m³",
        "pm10": " µg/m³",
        "co": " mg/m³",
        "no2": " µg/m³",
        "so2": " µg/m³",
        "o3": " µg/m³",
        "aqi": "",
    }
    return units.get(param, "")
