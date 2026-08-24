"""
EcoPulse Pollution Service
Core ingestion pipeline: validate → store → calculate AQI → check alerts → return
Optimized with single-query joins and lightweight response caching.
"""
import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
import time

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc, text

from app.models.pollution_reading import PollutionReading
from app.models.aqi_record import AQIRecord
from app.models.sensor import Sensor
from app.models.location import Location
from app.services.aqi_service import calculate_aqi
from app.services.alert_service import check_and_create_alerts

logger = logging.getLogger(__name__)

# Lightweight in-memory cache for current pollution (TTL 3 seconds)
_current_pollution_cache = {"timestamp": 0, "data": []}


async def ingest_reading(
    db: AsyncSession,
    sensor_id: uuid.UUID,
    location_id: uuid.UUID,
    data: dict,
) -> dict:
    """
    Full ingestion pipeline for a pollution reading.
    """
    now = datetime.now(timezone.utc)

    # 1. Validate sensor
    sensor_result = await db.execute(
        select(Sensor).where(Sensor.id == sensor_id)
    )
    sensor = sensor_result.scalar_one_or_none()
    if not sensor:
        raise ValueError(f"Sensor {sensor_id} not found")
    if sensor.status == "MAINTENANCE":
        raise ValueError(f"Sensor {sensor_id} is in MAINTENANCE mode")

    # 2. Validate timestamp
    timestamp = data.get("timestamp")
    if timestamp:
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        if timestamp > now + timedelta(minutes=5):
            raise ValueError("Timestamp is in the future")
        if timestamp < now - timedelta(hours=24):
            raise ValueError("Timestamp is too old (> 24 hours)")
    else:
        timestamp = now

    # 3. Store reading
    reading = PollutionReading(
        id=uuid.uuid4(),
        sensor_id=sensor_id,
        location_id=location_id,
        timestamp=timestamp,
        pm25=data.get("pm25"),
        pm10=data.get("pm10"),
        co=data.get("co"),
        co2=data.get("co2"),
        no2=data.get("no2"),
        so2=data.get("so2"),
        o3=data.get("o3"),
        temperature=data.get("temperature"),
        humidity=data.get("humidity"),
        pressure=data.get("pressure"),
        wind_speed=data.get("wind_speed"),
        wind_direction=data.get("wind_direction"),
        noise_level=data.get("noise_level"),
        source=data.get("source", "SIMULATED"),
        created_at=now,
    )
    db.add(reading)
    await db.flush()

    # 4. Calculate AQI
    aqi_result = calculate_aqi(
        pm25=data.get("pm25"),
        pm10=data.get("pm10"),
        co=data.get("co"),
        no2=data.get("no2"),
        so2=data.get("so2"),
        o3=data.get("o3"),
    )

    # 5. Store AQI record
    aqi_record = AQIRecord(
        id=uuid.uuid4(),
        reading_id=reading.id,
        location_id=location_id,
        aqi=aqi_result["aqi"],
        category=aqi_result["category"],
        dominant_pollutant=aqi_result["dominant_pollutant"],
        calculated_at=now,
    )
    db.add(aqi_record)
    await db.flush()

    # 6. Check alert conditions
    alerts = await check_and_create_alerts(
        db=db,
        sensor_id=sensor_id,
        location_id=location_id,
        reading_data=data,
        aqi_value=aqi_result["aqi"],
    )

    # 7. Update sensor last_seen
    sensor.last_seen = now
    sensor.status = "ONLINE"
    await db.flush()

    # Invalidate cache
    _current_pollution_cache["timestamp"] = 0

    return {
        "reading_id": str(reading.id),
        "sensor_id": str(sensor_id),
        "location_id": str(location_id),
        "timestamp": timestamp.isoformat(),
        "aqi": aqi_result,
        "alerts": alerts,
        "source": data.get("source", "SIMULATED"),
    }


async def get_current_pollution(db: AsyncSession, location_id: Optional[uuid.UUID] = None) -> list[dict]:
    """
    Get the latest pollution state for locations.
    Optimized with single SQL query and short TTL cache for instant responses (< 20ms).
    """
    now = time.time()
    if not location_id and (now - _current_pollution_cache["timestamp"]) < 3 and _current_pollution_cache["data"]:
        return _current_pollution_cache["data"]

    # Single SQL query joining locations with latest readings and AQI using DISTINCT ON / Window functions
    sql = text("""
        WITH latest_readings AS (
            SELECT DISTINCT ON (location_id) *
            FROM pollution_readings
            ORDER BY location_id, timestamp DESC
        ),
        latest_aqi AS (
            SELECT DISTINCT ON (location_id) *
            FROM aqi_records
            ORDER BY location_id, calculated_at DESC
        ),
        sensor_stats AS (
            SELECT 
                location_id,
                COUNT(id) as sensor_count,
                COUNT(CASE WHEN status = 'ONLINE' THEN 1 END) as online_sensors
            FROM sensors
            GROUP BY location_id
        )
        SELECT 
            l.id as location_id,
            l.name as location_name,
            l.city,
            l.state,
            l.country,
            l.latitude,
            l.longitude,
            a.aqi,
            a.category,
            a.dominant_pollutant,
            r.pm25,
            r.pm10,
            r.co,
            r.no2,
            r.so2,
            r.o3,
            r.temperature,
            r.humidity,
            r.wind_speed,
            r.pressure,
            r.timestamp as last_updated,
            r.source,
            COALESCE(s.sensor_count, 0) as sensor_count,
            COALESCE(s.online_sensors, 0) as online_sensors
        FROM locations l
        LEFT JOIN latest_readings r ON l.id = r.location_id
        LEFT JOIN latest_aqi a ON l.id = a.location_id
        LEFT JOIN sensor_stats s ON l.id = s.location_id
        ORDER BY l.name
    """)

    result = await db.execute(sql)
    rows = result.mappings().all()

    results = []
    for r in rows:
        if location_id and str(r["location_id"]) != str(location_id):
            continue
        results.append({
            "location_id": str(r["location_id"]),
            "location_name": r["location_name"],
            "city": r["city"],
            "state": r["state"],
            "country": r["country"],
            "latitude": float(r["latitude"]),
            "longitude": float(r["longitude"]),
            "aqi": r["aqi"],
            "category": r["category"],
            "dominant_pollutant": r["dominant_pollutant"],
            "pm25": r["pm25"],
            "pm10": r["pm10"],
            "co": r["co"],
            "no2": r["no2"],
            "so2": r["so2"],
            "o3": r["o3"],
            "temperature": r["temperature"],
            "humidity": r["humidity"],
            "wind_speed": r["wind_speed"],
            "pressure": r["pressure"],
            "last_updated": r["last_updated"].isoformat() if r["last_updated"] else None,
            "source": r["source"] or "SIMULATED",
            "sensor_count": r["sensor_count"],
            "online_sensors": r["online_sensors"],
        })

    if not location_id:
        _current_pollution_cache["timestamp"] = now
        _current_pollution_cache["data"] = results

    return results


async def get_pollution_history(
    db: AsyncSession,
    location_id: Optional[uuid.UUID] = None,
    sensor_id: Optional[uuid.UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict]:
    """Get historical pollution readings with single query."""
    query = select(PollutionReading).order_by(desc(PollutionReading.timestamp))

    if location_id:
        query = query.where(PollutionReading.location_id == location_id)
    if sensor_id:
        query = query.where(PollutionReading.sensor_id == sensor_id)
    if start_date:
        query = query.where(PollutionReading.timestamp >= start_date)
    if end_date:
        query = query.where(PollutionReading.timestamp <= end_date)

    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    readings = result.scalars().all()

    return [
        {
            "id": str(r.id),
            "sensor_id": str(r.sensor_id),
            "location_id": str(r.location_id),
            "timestamp": r.timestamp.isoformat(),
            "pm25": r.pm25,
            "pm10": r.pm10,
            "co": r.co,
            "co2": r.co2,
            "no2": r.no2,
            "so2": r.so2,
            "o3": r.o3,
            "temperature": r.temperature,
            "humidity": r.humidity,
            "pressure": r.pressure,
            "wind_speed": r.wind_speed,
            "wind_direction": r.wind_direction,
            "noise_level": r.noise_level,
            "source": r.source,
            "created_at": r.created_at.isoformat(),
        }
        for r in readings
    ]
