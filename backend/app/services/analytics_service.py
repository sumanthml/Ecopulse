"""
EcoPulse Analytics Service
High-performance statistical analysis & trend computation executed directly in PostgreSQL.
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from uuid import UUID
import time

import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

logger = logging.getLogger(__name__)

# Lightweight in-memory cache for analytics
_analytics_cache = {}


async def get_analytics_summary(
    db: AsyncSession,
    location_id: UUID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> dict:
    """
    Calculate statistical summary using optimized PostgreSQL aggregation.
    """
    if not start_date:
        start_date = datetime.now(timezone.utc) - timedelta(days=7)
    if not end_date:
        end_date = datetime.now(timezone.utc)

    cache_key = f"summary_{location_id}_{start_date.date()}_{end_date.date()}"
    now_ts = time.time()
    if cache_key in _analytics_cache and (now_ts - _analytics_cache[cache_key]["ts"]) < 5:
        return _analytics_cache[cache_key]["data"]

    sql = text("""
        SELECT
            ROUND(AVG(pm25)::numeric, 2) as pm25_mean,
            ROUND(MIN(pm25)::numeric, 2) as pm25_min,
            ROUND(MAX(pm25)::numeric, 2) as pm25_max,
            ROUND(STDDEV(pm25)::numeric, 2) as pm25_std,
            ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY pm25)::numeric, 2) as pm25_p95,
            
            ROUND(AVG(pm10)::numeric, 2) as pm10_mean,
            ROUND(MIN(pm10)::numeric, 2) as pm10_min,
            ROUND(MAX(pm10)::numeric, 2) as pm10_max,
            ROUND(STDDEV(pm10)::numeric, 2) as pm10_std,

            ROUND(AVG(no2)::numeric, 2) as no2_mean,
            ROUND(MIN(no2)::numeric, 2) as no2_min,
            ROUND(MAX(no2)::numeric, 2) as no2_max,

            ROUND(AVG(temperature)::numeric, 2) as temp_mean,
            ROUND(AVG(humidity)::numeric, 2) as humidity_mean,
            COUNT(*) as total_readings
        FROM pollution_readings
        WHERE location_id = :location_id
          AND timestamp >= :start_date
          AND timestamp <= :end_date
    """)

    result = await db.execute(sql, {
        "location_id": str(location_id),
        "start_date": start_date,
        "end_date": end_date,
    })
    row = result.mappings().first()

    if not row or not row["total_readings"]:
        return {"error": "No data available for the selected period"}

    # AQI summary
    aqi_sql = text("""
        SELECT 
            ROUND(AVG(aqi)::numeric, 2) as mean,
            MIN(aqi) as min,
            MAX(aqi) as max,
            ROUND(STDDEV(aqi)::numeric, 2) as std_dev,
            COUNT(*) as count
        FROM aqi_records
        WHERE location_id = :location_id
          AND calculated_at >= :start_date
          AND calculated_at <= :end_date
    """)
    aqi_res = await db.execute(aqi_sql, {
        "location_id": str(location_id),
        "start_date": start_date,
        "end_date": end_date,
    })
    aqi_row = aqi_res.mappings().first()

    stats = {
        "pm25": {
            "mean": float(row["pm25_mean"] or 0),
            "min": float(row["pm25_min"] or 0),
            "max": float(row["pm25_max"] or 0),
            "std_dev": float(row["pm25_std"] or 0),
            "p95": float(row["pm25_p95"] or 0),
            "count": row["total_readings"],
        },
        "pm10": {
            "mean": float(row["pm10_mean"] or 0),
            "min": float(row["pm10_min"] or 0),
            "max": float(row["pm10_max"] or 0),
            "std_dev": float(row["pm10_std"] or 0),
            "count": row["total_readings"],
        },
        "no2": {
            "mean": float(row["no2_mean"] or 0),
            "min": float(row["no2_min"] or 0),
            "max": float(row["no2_max"] or 0),
            "std_dev": 0,
            "count": row["total_readings"],
        },
        "temperature": {
            "mean": float(row["temp_mean"] or 0),
            "count": row["total_readings"],
        },
        "humidity": {
            "mean": float(row["humidity_mean"] or 0),
            "count": row["total_readings"],
        },
        "total_readings": row["total_readings"],
    }

    if aqi_row and aqi_row["count"]:
        stats["aqi"] = {
            "mean": float(aqi_row["mean"] or 0),
            "min": int(aqi_row["min"] or 0),
            "max": int(aqi_row["max"] or 0),
            "std_dev": float(aqi_row["std_dev"] or 0),
            "count": aqi_row["count"],
        }

    _analytics_cache[cache_key] = {"ts": now_ts, "data": stats}
    return stats


async def get_trends(
    db: AsyncSession,
    location_id: UUID,
    pollutant: str = "pm25",
    aggregation: str = "hourly",
    days: int = 7,
) -> list[dict]:
    """Get aggregated trend data directly using SQL date_trunc."""
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    date_format = "YYYY-MM-DD HH24:00"
    if aggregation == "daily":
        date_format = "YYYY-MM-DD"
    elif aggregation == "weekly":
        date_format = "IYYY-IW"

    # Validate column name against SQL injection
    valid_pollutants = {"pm25", "pm10", "no2", "so2", "co", "o3", "temperature", "humidity"}
    if pollutant not in valid_pollutants:
        pollutant = "pm25"

    sql = text(f"""
        SELECT 
            TO_CHAR(timestamp, '{date_format}') as period,
            ROUND(AVG({pollutant})::numeric, 2) as mean,
            ROUND(MIN({pollutant})::numeric, 2) as min,
            ROUND(MAX({pollutant})::numeric, 2) as max,
            COUNT(*) as count
        FROM pollution_readings
        WHERE location_id = :location_id
          AND timestamp >= :start_date
          AND {pollutant} IS NOT NULL
        GROUP BY period
        ORDER BY period ASC
    """)

    result = await db.execute(sql, {"location_id": str(location_id), "start_date": start_date})
    rows = result.mappings().all()

    return [
        {
            "period": r["period"],
            "mean": float(r["mean"] or 0),
            "min": float(r["min"] or 0),
            "max": float(r["max"] or 0),
            "count": r["count"],
        }
        for r in rows
    ]


async def get_correlation(
    db: AsyncSession,
    location_id: UUID,
    days: int = 7,
) -> dict:
    """Calculate Pearson correlation using PostgreSQL corr() function directly in SQL."""
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    sql = text("""
        SELECT 
            ROUND(corr(pm25, pm10)::numeric, 4) as pm25_pm10,
            ROUND(corr(pm25, no2)::numeric, 4) as pm25_no2,
            ROUND(corr(pm25, temperature)::numeric, 4) as pm25_temp,
            ROUND(corr(pm25, humidity)::numeric, 4) as pm25_humidity,
            ROUND(corr(no2, co)::numeric, 4) as no2_co,
            ROUND(corr(so2, pm10)::numeric, 4) as so2_pm10,
            COUNT(*) as samples
        FROM pollution_readings
        WHERE location_id = :location_id
          AND timestamp >= :start_date
    """)

    result = await db.execute(sql, {"location_id": str(location_id), "start_date": start_date})
    row = result.mappings().first()

    if not row or row["samples"] < 5:
        return {"correlations": [], "note": "Insufficient data for correlation analysis"}

    pairs = [
        ("pm25", "pm10", row["pm25_pm10"]),
        ("pm25", "no2", row["pm25_no2"]),
        ("pm25", "temperature", row["pm25_temp"]),
        ("pm25", "humidity", row["pm25_humidity"]),
        ("no2", "co", row["no2_co"]),
        ("so2", "pm10", row["so2_pm10"]),
    ]

    correlations = []
    for p1, p2, val in pairs:
        if val is not None:
            c = float(val)
            correlations.append({
                "param1": p1,
                "param2": p2,
                "correlation": c,
                "strength": _correlation_strength(c),
                "samples": row["samples"],
            })

    return {
        "correlations": sorted(correlations, key=lambda x: abs(x["correlation"]), reverse=True),
        "note": "Pearson correlation computed directly in PostgreSQL.",
        "period_days": days,
    }


async def get_pollution_heatmap(
    db: AsyncSession,
    location_id: UUID,
    days: int = 7,
) -> dict:
    """Generate pollution heatmap directly using SQL date_trunc and AVG."""
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    sql = text("""
        SELECT 
            TO_CHAR(calculated_at, 'YYYY-MM-DD') as day,
            EXTRACT(HOUR FROM calculated_at)::int as hour,
            ROUND(AVG(aqi)::numeric, 0) as avg_aqi
        FROM aqi_records
        WHERE location_id = :location_id
          AND calculated_at >= :start_date
        GROUP BY day, hour
        ORDER BY day, hour
    """)

    result = await db.execute(sql, {"location_id": str(location_id), "start_date": start_date})
    rows = result.mappings().all()

    heatmap_map = {}
    for r in rows:
        day = r["day"]
        if day not in heatmap_map:
            heatmap_map[day] = {}
        heatmap_map[day][str(r["hour"])] = float(r["avg_aqi"])

    heatmap = [
        {"day": day, "hours": hours}
        for day, hours in heatmap_map.items()
    ]

    return {
        "heatmap": heatmap,
        "days": list(heatmap_map.keys()),
        "hours": list(range(24)),
    }


def _correlation_strength(r: float) -> str:
    abs_r = abs(r)
    if abs_r >= 0.8: return "Very Strong"
    elif abs_r >= 0.6: return "Strong"
    elif abs_r >= 0.4: return "Moderate"
    elif abs_r >= 0.2: return "Weak"
    else: return "Very Weak"
