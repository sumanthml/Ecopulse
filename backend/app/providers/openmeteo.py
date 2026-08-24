"""
EcoPulse Data Provider - Open-Meteo Air Quality API
Free, no API key required.

API: https://air-quality-api.open-meteo.com/v1/air-quality
Provides: PM2.5, PM10, NO2, SO2, O3, CO, temperature, humidity, etc.
"""
import logging
from typing import Optional

import httpx

from app.providers.base import EnvironmentalDataProvider, EnvironmentalReading

logger = logging.getLogger(__name__)


class OpenMeteoProvider(EnvironmentalDataProvider):
    """
    Open-Meteo Air Quality API provider.
    
    Free tier, no API key needed.
    Rate limit: Fair use (avoid > 10,000 requests/day).
    """

    BASE_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
    WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

    @property
    def name(self) -> str:
        return "Open-Meteo Air Quality"

    @property
    def source_type(self) -> str:
        return "API"

    async def fetch_latest(
        self,
        latitude: float,
        longitude: float,
    ) -> Optional[EnvironmentalReading]:
        """Fetch latest air quality data from Open-Meteo."""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Air quality data
                aq_params = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone",
                    "timezone": "auto",
                }
                aq_response = await client.get(self.BASE_URL, params=aq_params)
                aq_response.raise_for_status()
                aq_data = aq_response.json()

                # Weather data (temperature, humidity, etc.)
                weather_params = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": "temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,wind_direction_10m",
                    "timezone": "auto",
                }
                weather_response = await client.get(self.WEATHER_URL, params=weather_params)
                weather_response.raise_for_status()
                weather_data = weather_response.json()

            # Parse air quality
            current_aq = aq_data.get("current", {})
            current_weather = weather_data.get("current", {})

            reading = EnvironmentalReading(
                pm25=current_aq.get("pm2_5"),
                pm10=current_aq.get("pm10"),
                co=self._ug_to_mg(current_aq.get("carbon_monoxide")),  # Open-Meteo gives µg/m³, convert to mg/m³
                no2=current_aq.get("nitrogen_dioxide"),
                so2=current_aq.get("sulphur_dioxide"),
                o3=current_aq.get("ozone"),
                temperature=current_weather.get("temperature_2m"),
                humidity=current_weather.get("relative_humidity_2m"),
                pressure=current_weather.get("surface_pressure"),
                wind_speed=current_weather.get("wind_speed_10m"),
                wind_direction=current_weather.get("wind_direction_10m"),
                source="REAL",
                provider_name=self.name,
                raw_data={"air_quality": aq_data, "weather": weather_data},
            )

            logger.info(f"Open-Meteo fetch successful: PM2.5={reading.pm25}, PM10={reading.pm10}")
            return reading

        except httpx.TimeoutException:
            logger.error("Open-Meteo API timeout")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"Open-Meteo API error: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Open-Meteo fetch failed: {e}")
            return None

    async def health_check(self) -> dict:
        """Check if Open-Meteo API is reachable."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    self.BASE_URL,
                    params={"latitude": 13.08, "longitude": 80.27, "current": "pm2_5"}
                )
                if response.status_code == 200:
                    return {"provider": self.name, "status": "ONLINE"}
                return {"provider": self.name, "status": "DEGRADED", "code": response.status_code}
        except Exception as e:
            return {"provider": self.name, "status": "OFFLINE", "error": str(e)}

    @staticmethod
    def _ug_to_mg(value: Optional[float]) -> Optional[float]:
        """Convert µg/m³ to mg/m³."""
        if value is not None:
            return round(value / 1000, 3)
        return None
