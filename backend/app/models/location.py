"""
EcoPulse SQLAlchemy Models - Location
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    city: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str | None] = mapped_column(String, nullable=True)
    country: Mapped[str] = mapped_column(String, nullable=False, default="India")
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    sensors = relationship("Sensor", back_populates="location", lazy="selectin")
    readings = relationship("PollutionReading", back_populates="location", lazy="noload")
    aqi_records = relationship("AQIRecord", back_populates="location", lazy="noload")
    alerts = relationship("Alert", back_populates="location", lazy="noload")
    insights = relationship("EnvironmentalInsight", back_populates="location", lazy="noload")
