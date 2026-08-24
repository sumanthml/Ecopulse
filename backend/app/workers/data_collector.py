"""
EcoPulse Data Collector Worker
Background worker that periodically fetches data from the configured provider
and sends it through the full ingestion pipeline.

Pipeline: Provider → FastAPI validation → Database → AQI calculation → Alerts → Realtime
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import async_session_factory
from app.models.location import Location
from app.models.sensor import Sensor
from app.providers.base import EnvironmentalDataProvider
from app.providers.simulator import SimulatorProvider, SimulatorScenario
from app.providers.openmeteo import OpenMeteoProvider
from app.services.pollution_service import ingest_reading

logger = logging.getLogger(__name__)


class DataCollector:
    """Background data collection worker."""

    def __init__(self):
        self.provider: Optional[EnvironmentalDataProvider] = None
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self.last_fetch: Optional[datetime] = None
        self.last_error: Optional[str] = None
        self.fetch_count: int = 0
        self.error_count: int = 0

    def initialize_provider(self):
        """Initialize the configured data provider."""
        provider_name = settings.data_provider.lower()

        if provider_name == "simulator":
            self.provider = SimulatorProvider()
            logger.info("Data provider: Simulator")
        elif provider_name == "openmeteo":
            self.provider = OpenMeteoProvider()
            logger.info("Data provider: Open-Meteo")
        else:
            logger.warning(f"Unknown provider '{provider_name}', defaulting to simulator")
            self.provider = SimulatorProvider()

    async def start(self):
        """Start the background data collection loop."""
        if self._running:
            logger.warning("Data collector already running")
            return

        self.initialize_provider()
        self._running = True
        self._task = asyncio.create_task(self._collection_loop())
        logger.info(f"Data collector started (interval: {settings.data_collection_interval}s)")

    async def stop(self):
        """Stop the data collection loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Data collector stopped")

    async def _collection_loop(self):
        """Main collection loop — runs periodically."""
        while self._running:
            try:
                await self._collect_all_locations()
            except Exception as e:
                logger.error(f"Collection cycle error: {e}")
                self.last_error = str(e)
                self.error_count += 1

            await asyncio.sleep(settings.data_collection_interval)

    async def _collect_all_locations(self):
        """Fetch data for all active locations."""
        if async_session_factory is None:
            logger.warning("Database not configured — skipping collection")
            return

        async with async_session_factory() as db:
            # Get all locations
            result = await db.execute(select(Location))
            locations = result.scalars().all()

            for location in locations:
                try:
                    await self._collect_for_location(db, location)
                except Exception as e:
                    logger.error(f"Failed to collect for {location.name}: {e}")

            await db.commit()

    async def _collect_for_location(self, db: AsyncSession, location: Location):
        """Fetch and ingest data for a single location."""
        if self.provider is None:
            return

        # Fetch from provider
        reading = await self.provider.fetch_latest(location.latitude, location.longitude)

        if reading is None:
            logger.warning(f"No data from provider for {location.name}")
            return

        # Find active sensor for this location
        sensor_result = await db.execute(
            select(Sensor)
            .where(Sensor.location_id == location.id, Sensor.status != "MAINTENANCE")
            .order_by(Sensor.created_at)
            .limit(1)
        )
        sensor = sensor_result.scalar_one_or_none()

        if not sensor:
            logger.warning(f"No active sensor for {location.name}")
            return

        # Send through ingestion pipeline
        result = await ingest_reading(
            db=db,
            sensor_id=sensor.id,
            location_id=location.id,
            data=reading.to_dict(),
        )

        self.last_fetch = datetime.now(timezone.utc)
        self.fetch_count += 1

        logger.info(
            f"Collected: {location.name} → AQI {result['aqi']['aqi']} "
            f"({result['aqi']['category']})"
        )

    def set_scenario(self, scenario: str):
        """Change simulator scenario (only works with SimulatorProvider)."""
        if isinstance(self.provider, SimulatorProvider):
            self.provider.set_scenario(scenario)
            return True
        return False

    def get_status(self) -> dict:
        """Get collector status."""
        return {
            "running": self._running,
            "provider": self.provider.name if self.provider else None,
            "source_type": self.provider.source_type if self.provider else None,
            "last_fetch": self.last_fetch.isoformat() if self.last_fetch else None,
            "last_error": self.last_error,
            "fetch_count": self.fetch_count,
            "error_count": self.error_count,
            "interval_seconds": settings.data_collection_interval,
        }


# Singleton
data_collector = DataCollector()
