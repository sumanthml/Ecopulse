"""
EcoPulse SQLAlchemy Models - Sensor
"""
import uuid
from datetime import datetime, date, timezone
from sqlalchemy import String, ForeignKey, DateTime, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Sensor(Base):
    __tablename__ = "sensors"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    location_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("locations.id"), nullable=False)
    sensor_code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    sensor_name: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False, default="SIMULATED")
    sensor_type: Mapped[str] = mapped_column(String, nullable=False, default="multi-pollutant")
    status: Mapped[str] = mapped_column(String, nullable=False, default="ONLINE")
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    installation_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    location = relationship("Location", back_populates="sensors")
    readings = relationship("PollutionReading", back_populates="sensor", lazy="noload")
    alerts = relationship("Alert", back_populates="sensor", lazy="noload")
