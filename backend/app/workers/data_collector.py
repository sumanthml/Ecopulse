"""
EcoPulse Data Collector Worker
Background worker that periodically fetches data from the configured provider
and sends it through the full ingestion pipeline. Also keeps free tier servers alive.
"""
import asyncio
import logging
import urllib.request
import ssl
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
    """Background data collection worker with self keep-alive."""

    def __init__(self):
        self.provider: Optional[EnvironmentalDataProvider] = None
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._keepalive_task: Optional[asyncio.Task] = None
        self.last_fetch: Optional[datetime] = None
        self.last_error: Optional[str] = None
        self.fetch_count: int = 0
        self.error_count: int = 0

    def initialize_provider(self):
        provider_name = settings.data_provider.lower()
        if provider_name == "simulator":
            self.provider = SimulatorProvider()
            logger.info("Data provider: Simulator")
        elif provider_name == "openmeteo":
            self.provider = OpenMeteoProvider()
            logger.info("Data provider: Open-Meteo")
        else:
            self.provider = SimulatorProvider()

    async def start(self):
        if self._running:
            return

        self.initialize_provider()
        self._running = True
        self._task = asyncio.create_task(self._collection_loop())
        self._keepalive_task = asyncio.create_task(self._keepalive_loop())
        logger.info(f"Data collector & keepalive started (interval: {settings.data_collection_interval}s)")

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
        if self._keepalive_task:
            self._keepalive_task.cancel()
        logger.info("Data collector stopped")

    async def _keepalive_loop(self):
        """Self-ping loop to prevent free-tier hosts like Render from sleeping."""
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        while self._running:
            await asyncio.sleep(120)  # Ping every 2 minutes
            try:
                url = "https://ecopulse-backend-46fv.onrender.com/health"
                req = urllib.request.Request(url, headers={"User-Agent": "EcoPulseKeepAlive/1.0"})
                urllib.request.urlopen(req, context=ctx, timeout=10)
                logger.info("Keep-alive self ping successful")
            except Exception as e:
                logger.warning(f"Keep-alive ping error (ignoring): {e}")

    async def _collection_loop(self):
        while self._running:
            try:
                await self._collect_all_locations()
            except Exception as e:
                logger.error(f"Collection cycle error: {e}")
                self.last_error = str(e)
                self.error_count += 1

            await asyncio.sleep(settings.data_collection_interval)

    async def _collect_all_locations(self):
        if async_session_factory is None:
            return

        async with async_session_factory() as db:
            result = await db.execute(select(Location))
            locations = result.scalars().all()

            for location in locations:
                try:
                    await self._collect_for_location(db, location)
                except Exception as e:
                    logger.error(f"Failed to collect for {location.name}: {e}")

            await db.commit()

    async def _collect_for_location(self, db: AsyncSession, location: Location):
        if self.provider is None:
            return

        reading = await self.provider.fetch_latest(location.latitude, location.longitude)
        if reading is None:
            return

        sensor_result = await db.execute(
            select(Sensor)
            .where(Sensor.location_id == location.id, Sensor.status != "MAINTENANCE")
            .order_by(Sensor.created_at)
            .limit(1)
        )
        sensor = sensor_result.scalar_one_or_none()
        if not sensor:
            return

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
        if isinstance(self.provider, SimulatorProvider):
            self.provider.set_scenario(scenario)
            return True
        return False

    def get_status(self) -> dict:
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


data_collector = DataCollector()
