"""
EcoPulse SQLAlchemy Models - AQI Record
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class AQIRecord(Base):
    __tablename__ = "aqi_records"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    reading_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("pollution_readings.id"), nullable=True)
    location_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("locations.id"), nullable=False)
    aqi: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    dominant_pollutant: Mapped[str | None] = mapped_column(String, nullable=True)
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    reading = relationship("PollutionReading", back_populates="aqi_record")
    location = relationship("Location", back_populates="aqi_records")
