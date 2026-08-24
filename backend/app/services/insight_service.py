"""
EcoPulse Insight Service
Manages AI-generated environmental insights storage and retrieval.
"""
import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from app.models.insight import EnvironmentalInsight

logger = logging.getLogger(__name__)


async def get_insights(
    db: AsyncSession,
    location_id: Optional[uuid.UUID] = None,
    insight_type: Optional[str] = None,
    limit: int = 20,
) -> list[dict]:
    """Get environmental insights, optionally filtered."""
    query = select(EnvironmentalInsight).order_by(desc(EnvironmentalInsight.created_at))

    if location_id:
        query = query.where(EnvironmentalInsight.location_id == location_id)
    if insight_type:
        query = query.where(EnvironmentalInsight.insight_type == insight_type)

    # Only return non-expired insights
    query = query.where(
        (EnvironmentalInsight.expires_at == None) |
        (EnvironmentalInsight.expires_at > datetime.now(timezone.utc))
    )

    query = query.limit(limit)
    result = await db.execute(query)
    insights = result.scalars().all()

    return [
        {
            "id": str(i.id),
            "location_id": str(i.location_id) if i.location_id else None,
            "insight_type": i.insight_type,
            "title": i.title,
            "content": i.content,
            "severity": i.severity,
            "generated_by": i.generated_by,
            "created_at": i.created_at.isoformat(),
            "expires_at": i.expires_at.isoformat() if i.expires_at else None,
        }
        for i in insights
    ]


async def store_insight(
    db: AsyncSession,
    location_id: Optional[uuid.UUID],
    insight_type: str,
    title: str,
    content: str,
    severity: str = "INFO",
    generated_by: str = "groq",
    expires_hours: int = 24,
) -> dict:
    """Store a new environmental insight."""
    insight = EnvironmentalInsight(
        id=uuid.uuid4(),
        location_id=location_id,
        insight_type=insight_type,
        title=title,
        content=content,
        severity=severity,
        generated_by=generated_by,
        created_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=expires_hours),
    )
    db.add(insight)
    await db.flush()

    return {
        "id": str(insight.id),
        "title": insight.title,
        "insight_type": insight.insight_type,
        "created_at": insight.created_at.isoformat(),
    }


async def check_recent_insight(
    db: AsyncSession,
    location_id: uuid.UUID,
    insight_type: str,
    hours: int = 6,
) -> bool:
    """Check if a recent insight of this type already exists (avoid duplicates)."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    result = await db.execute(
        select(EnvironmentalInsight.id).where(
            and_(
                EnvironmentalInsight.location_id == location_id,
                EnvironmentalInsight.insight_type == insight_type,
                EnvironmentalInsight.created_at >= cutoff,
            )
        ).limit(1)
    )
    return result.first() is not None
