"""
EcoPulse API - Dashboard
Main dashboard summary endpoint.
Optimized for sub-50ms high performance.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, text
from datetime import datetime, timezone

from app.core.database import get_db
from app.models.alert import Alert
from app.models.insight import EnvironmentalInsight
from app.services.pollution_service import get_current_pollution
from app.workers.data_collector import data_collector

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/summary")
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    """Get complete dashboard summary data with optimized single SQL execution."""
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # 1. Current pollution for all locations (cached/optimized single SQL query)
    current_pollution = await get_current_pollution(db)

    # 2. Combined single SQL query for all system statistics
    stats_sql = text("""
        SELECT
            (SELECT COUNT(*) FROM locations) as total_locations,
            (SELECT COUNT(*) FROM sensors) as total_sensors,
            (SELECT COUNT(*) FROM sensors WHERE status = 'ONLINE') as online_sensors,
            (SELECT COUNT(*) FROM sensors WHERE status = 'OFFLINE') as offline_sensors,
            (SELECT COUNT(*) FROM pollution_readings) as total_readings,
            (SELECT COUNT(*) FROM pollution_readings WHERE created_at >= :today_start) as today_readings,
            (SELECT COUNT(*) FROM alerts WHERE status = 'ACTIVE') as active_alerts,
            (SELECT COUNT(*) FROM alerts WHERE status = 'ACTIVE' AND severity = 'CRITICAL') as critical_alerts
    """)

    stats_res = await db.execute(stats_sql, {"today_start": today_start})
    stats_row = stats_res.mappings().first()

    # 3. Active alerts
    active_alerts_result = await db.execute(
        select(Alert)
        .where(Alert.status == "ACTIVE")
        .order_by(desc(Alert.created_at))
        .limit(10)
    )
    active_alerts = active_alerts_result.scalars().all()

    # 4. Recent insights
    insights_result = await db.execute(
        select(EnvironmentalInsight)
        .where(
            (EnvironmentalInsight.expires_at == None) |
            (EnvironmentalInsight.expires_at > now)
        )
        .order_by(desc(EnvironmentalInsight.created_at))
        .limit(5)
    )
    recent_insights = insights_result.scalars().all()

    # Collector status
    collector_status = data_collector.get_status()

    return {
        "success": True,
        "data": {
            "locations": current_pollution,
            "stats": {
                "total_locations": stats_row["total_locations"],
                "total_sensors": stats_row["total_sensors"],
                "online_sensors": stats_row["online_sensors"],
                "offline_sensors": stats_row["offline_sensors"],
                "total_readings": stats_row["total_readings"],
                "today_readings": stats_row["today_readings"],
                "active_alerts": stats_row["active_alerts"],
                "critical_alerts": stats_row["critical_alerts"],
            },
            "alerts": [
                {
                    "id": str(a.id),
                    "title": a.title,
                    "severity": a.severity,
                    "parameter": a.parameter,
                    "value": a.value,
                    "status": a.status,
                    "created_at": a.created_at.isoformat(),
                }
                for a in active_alerts
            ],
            "insights": [
                {
                    "id": str(i.id),
                    "title": i.title,
                    "content": i.content[:200] + "..." if len(i.content) > 200 else i.content,
                    "severity": i.severity,
                    "insight_type": i.insight_type,
                    "created_at": i.created_at.isoformat(),
                }
                for i in recent_insights
            ],
            "system": {
                "collector": collector_status,
                "timestamp": now.isoformat(),
            },
        },
        "message": "Dashboard summary retrieved",
    }
