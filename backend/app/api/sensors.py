"""
EcoPulse API - Locations & Sensors
Optimized with single JOIN queries.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from typing import Optional
from uuid import UUID

from app.core.database import get_db
from app.models.location import Location
from app.models.sensor import Sensor
from app.schemas.location import LocationCreate
from app.schemas.sensor import SensorCreate, SensorUpdate

locations_router = APIRouter(prefix="/api/locations", tags=["Locations"])
sensors_router = APIRouter(prefix="/api/sensors", tags=["Sensors"])


# ── Location Routes ──

@locations_router.get("")
async def list_locations(db: AsyncSession = Depends(get_db)):
    """Get all monitoring locations with single query."""
    sql = text("""
        WITH latest_aqi AS (
            SELECT DISTINCT ON (location_id) location_id, aqi, category
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
            l.id, l.name, l.city, l.state, l.country,
            l.latitude, l.longitude, l.description, l.created_at,
            a.aqi as current_aqi, a.category as aqi_category,
            COALESCE(s.sensor_count, 0) as sensor_count,
            COALESCE(s.online_sensors, 0) as online_sensors
        FROM locations l
        LEFT JOIN latest_aqi a ON l.id = a.location_id
        LEFT JOIN sensor_stats s ON l.id = s.location_id
        ORDER BY l.name
    """)

    result = await db.execute(sql)
    rows = result.mappings().all()

    return {"success": True, "data": [
        {
            "id": str(r["id"]),
            "name": r["name"],
            "city": r["city"],
            "state": r["state"],
            "country": r["country"],
            "latitude": float(r["latitude"]),
            "longitude": float(r["longitude"]),
            "description": r["description"],
            "created_at": r["created_at"].isoformat(),
            "sensor_count": r["sensor_count"],
            "online_sensors": r["online_sensors"],
            "current_aqi": r["current_aqi"],
            "aqi_category": r["aqi_category"],
        }
        for r in rows
    ]}


@locations_router.get("/{location_id}")
async def get_location(location_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a specific location with details."""
    result = await db.execute(select(Location).where(Location.id == location_id))
    loc = result.scalar_one_or_none()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")

    return {"success": True, "data": {
        "id": str(loc.id), "name": loc.name, "city": loc.city,
        "state": loc.state, "country": loc.country,
        "latitude": float(loc.latitude), "longitude": float(loc.longitude),
        "description": loc.description, "created_at": loc.created_at.isoformat(),
    }}


@locations_router.post("")
async def create_location(location: LocationCreate, db: AsyncSession = Depends(get_db)):
    """Create a new monitoring location."""
    import uuid
    new_loc = Location(id=uuid.uuid4(), **location.model_dump())
    db.add(new_loc)
    await db.flush()
    return {"success": True, "data": {"id": str(new_loc.id)}, "message": "Location created"}


# ── Sensor Routes ──

@sensors_router.get("")
async def list_sensors(
    location_id: Optional[UUID] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get all sensors with single SQL JOIN query."""
    where_clauses = []
    params = {}
    if location_id:
        where_clauses.append("s.location_id = :location_id")
        params["location_id"] = str(location_id)
    if status:
        where_clauses.append("s.status = :status")
        params["status"] = status

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    sql = text(f"""
        WITH latest_aqi AS (
            SELECT DISTINCT ON (location_id) location_id, aqi
            FROM aqi_records
            ORDER BY location_id, calculated_at DESC
        )
        SELECT 
            s.id, s.location_id, s.sensor_code, s.sensor_name,
            s.source, s.sensor_type, s.status, s.last_seen,
            s.installation_date, s.created_at,
            l.name as location_name, l.city,
            a.aqi as current_aqi
        FROM sensors s
        LEFT JOIN locations l ON s.location_id = l.id
        LEFT JOIN latest_aqi a ON s.location_id = a.location_id
        {where_sql}
        ORDER BY s.sensor_name
    """)

    result = await db.execute(sql, params)
    rows = result.mappings().all()

    data = []
    for r in rows:
        health = 100.0 if r["status"] == "ONLINE" else (80.0 if r["status"] == "WARNING" else 50.0)

        data.append({
            "id": str(r["id"]),
            "location_id": str(r["location_id"]),
            "sensor_code": r["sensor_code"],
            "sensor_name": r["sensor_name"],
            "source": r["source"],
            "sensor_type": r["sensor_type"],
            "status": r["status"],
            "last_seen": r["last_seen"].isoformat() if r["last_seen"] else None,
            "installation_date": r["installation_date"].isoformat() if r["installation_date"] else None,
            "created_at": r["created_at"].isoformat(),
            "location_name": r["location_name"],
            "city": r["city"],
            "current_aqi": r["current_aqi"],
            "health_score": health,
        })

    return {"success": True, "data": data}


@sensors_router.get("/{sensor_id}")
async def get_sensor(sensor_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a specific sensor with details."""
    result = await db.execute(select(Sensor).where(Sensor.id == sensor_id))
    sensor = result.scalar_one_or_none()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")

    loc_result = await db.execute(
        select(Location).where(Location.id == sensor.location_id)
    )
    location = loc_result.scalar_one_or_none()

    return {"success": True, "data": {
        "id": str(sensor.id),
        "location_id": str(sensor.location_id),
        "sensor_code": sensor.sensor_code,
        "sensor_name": sensor.sensor_name,
        "source": sensor.source,
        "sensor_type": sensor.sensor_type,
        "status": sensor.status,
        "last_seen": sensor.last_seen.isoformat() if sensor.last_seen else None,
        "installation_date": sensor.installation_date.isoformat() if sensor.installation_date else None,
        "location_name": location.name if location else None,
        "city": location.city if location else None,
        "health_score": 100.0 if sensor.status == "ONLINE" else 50.0,
    }}


@sensors_router.post("")
async def create_sensor(sensor: SensorCreate, db: AsyncSession = Depends(get_db)):
    """Create a new sensor."""
    import uuid
    new_sensor = Sensor(id=uuid.uuid4(), **sensor.model_dump())
    db.add(new_sensor)
    await db.flush()
    return {"success": True, "data": {"id": str(new_sensor.id)}, "message": "Sensor created"}


@sensors_router.put("/{sensor_id}")
async def update_sensor(sensor_id: UUID, update: SensorUpdate, db: AsyncSession = Depends(get_db)):
    """Update sensor properties."""
    result = await db.execute(select(Sensor).where(Sensor.id == sensor_id))
    sensor = result.scalar_one_or_none()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")

    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(sensor, key, value)
    await db.flush()

    return {"success": True, "message": "Sensor updated"}
