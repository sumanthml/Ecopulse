"""
EcoPulse SQLAlchemy Models - Pollution Reading
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class PollutionReading(Base):
    __tablename__ = "pollution_readings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    sensor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sensors.id"), nullable=False)
    location_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("locations.id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Air pollutants (all nullable — provider may not supply all)
    pm25: Mapped[float | None] = mapped_column(Float, nullable=True)     # µg/m³
    pm10: Mapped[float | None] = mapped_column(Float, nullable=True)     # µg/m³
    co: Mapped[float | None] = mapped_column(Float, nullable=True)       # mg/m³
    co2: Mapped[float | None] = mapped_column(Float, nullable=True)      # ppm
    no2: Mapped[float | None] = mapped_column(Float, nullable=True)      # µg/m³
    so2: Mapped[float | None] = mapped_column(Float, nullable=True)      # µg/m³
    o3: Mapped[float | None] = mapped_column(Float, nullable=True)       # µg/m³

    # Meteorological
    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)     # °C
    humidity: Mapped[float | None] = mapped_column(Float, nullable=True)        # %
    pressure: Mapped[float | None] = mapped_column(Float, nullable=True)        # hPa
    wind_speed: Mapped[float | None] = mapped_column(Float, nullable=True)      # m/s
    wind_direction: Mapped[float | None] = mapped_column(Float, nullable=True)  # degrees
    noise_level: Mapped[float | None] = mapped_column(Float, nullable=True)     # dB

    # Metadata
    source: Mapped[str] = mapped_column(String, nullable=False, default="SIMULATED")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    sensor = relationship("Sensor", back_populates="readings")
    location = relationship("Location", back_populates="readings")
    aqi_record = relationship("AQIRecord", back_populates="reading", uselist=False, lazy="joined")
