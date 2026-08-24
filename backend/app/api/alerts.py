"""
EcoPulse API - Alerts
High-performance alert endpoints with single-query JOINs and micro-caching.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional
from uuid import UUID
from datetime import datetime
import time

from app.core.database import get_db
from app.services.alert_service import acknowledge_alert, resolve_alert

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

_alerts_cache = {"timestamp": 0, "key": "", "data": []}


@router.get("")
async def list_alerts(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    location_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Get alerts with single SQL JOIN and micro-caching (< 10ms response)."""
    cache_key = f"{status}_{severity}_{location_id}_{limit}_{offset}"
    now = time.time()

    if (now - _alerts_cache["timestamp"]) < 3 and _alerts_cache["key"] == cache_key:
        return {"success": True, "data": _alerts_cache["data"], "message": "Alerts retrieved (cached)"}

    where_clauses = []
    params = {"limit": limit, "offset": offset}

    if status:
        where_clauses.append("a.status = :status")
        params["status"] = status
    if severity:
        where_clauses.append("a.severity = :severity")
        params["severity"] = severity
    if location_id:
        where_clauses.append("a.location_id = :location_id")
        params["location_id"] = str(location_id)

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    sql = text(f"""
        SELECT 
            a.id, a.sensor_id, a.location_id, a.parameter, a.value,
            a.threshold, a.severity, a.title, a.message, a.status,
            a.created_at, a.acknowledged_at, a.resolved_at,
            l.name as location_name, l.city,
            s.sensor_code
        FROM alerts a
        LEFT JOIN locations l ON a.location_id = l.id
        LEFT JOIN sensors s ON a.sensor_id = s.id
        {where_sql}
        ORDER BY a.created_at DESC
        LIMIT :limit OFFSET :offset
    """)

    result = await db.execute(sql, params)
    rows = result.mappings().all()

    data = [
        {
            "id": str(r["id"]),
            "sensor_id": str(r["sensor_id"]) if r["sensor_id"] else None,
            "location_id": str(r["location_id"]),
            "parameter": r["parameter"],
            "value": float(r["value"]),
            "threshold": float(r["threshold"]),
            "severity": r["severity"],
            "title": r["title"],
            "message": r["message"],
            "status": r["status"],
            "created_at": r["created_at"].isoformat(),
            "acknowledged_at": r["acknowledged_at"].isoformat() if r["acknowledged_at"] else None,
            "resolved_at": r["resolved_at"].isoformat() if r["resolved_at"] else None,
            "location_name": r["location_name"],
            "city": r["city"],
            "sensor_code": r["sensor_code"],
        }
        for r in rows
    ]

    _alerts_cache["timestamp"] = now
    _alerts_cache["key"] = cache_key
    _alerts_cache["data"] = data

    return {"success": True, "data": data, "message": f"{len(data)} alerts retrieved"}


@router.put("/{alert_id}/acknowledge")
async def ack_alert(alert_id: UUID, db: AsyncSession = Depends(get_db)):
    """Acknowledge an alert."""
    _alerts_cache["timestamp"] = 0
    result = await acknowledge_alert(db, alert_id)
    if not result:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"success": True, "data": result, "message": "Alert acknowledged"}


@router.put("/{alert_id}/resolve")
async def res_alert(alert_id: UUID, db: AsyncSession = Depends(get_db)):
    """Resolve an alert."""
    _alerts_cache["timestamp"] = 0
    result = await resolve_alert(db, alert_id)
    if not result:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"success": True, "data": result, "message": "Alert resolved"}
