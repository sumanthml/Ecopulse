"""
EcoPulse Data Provider - Realistic Sensor Simulator

Generates realistic environmental data using time-series models:
- Diurnal patterns (morning rush, afternoon heat, evening peaks, night calm)
- Gaussian noise with gradual drift
- Correlated pollutants (PM2.5 ↔ PM10, NO2 ↔ CO)
- Configurable scenarios: Normal, Rush Hour, High Pollution, Spike, Sensor Failure
"""
import math
import random
import logging
from datetime import datetime, timezone
from typing import Optional

from app.providers.base import EnvironmentalDataProvider, EnvironmentalReading

logger = logging.getLogger(__name__)


class SimulatorScenario:
    """Simulation scenario configuration."""
    NORMAL = "normal"
    RUSH_HOUR = "rush_hour"
    HIGH_POLLUTION = "high_pollution"
    POLLUTION_SPIKE = "pollution_spike"
    SENSOR_FAILURE = "sensor_failure"


class SimulatorProvider(EnvironmentalDataProvider):
    """
    Realistic environmental sensor simulator.
    """

    def __init__(self, scenario: str = SimulatorScenario.NORMAL):
        self.scenario = scenario
        self._state = {}
        self._failure_counter = 0

    @property
    def name(self) -> str:
        return "Demo Sensor Simulator"

    @property
    def source_type(self) -> str:
        return "SIMULATED"

    def set_scenario(self, scenario: str):
        self.scenario = scenario
        logger.info(f"Simulator scenario changed to: {scenario}")

    async def fetch_latest(
        self,
        latitude: float,
        longitude: float,
    ) -> Optional[EnvironmentalReading]:

        if self.scenario == SimulatorScenario.SENSOR_FAILURE:
            self._failure_counter += 1
            if self._failure_counter < 5:
                return None
            else:
                self._failure_counter = 0
                self.scenario = SimulatorScenario.NORMAL

        now = datetime.now(timezone.utc)
        hour = now.hour
        minute = now.minute
        weekday = now.weekday()

        baseline = self._get_city_baseline(latitude, longitude)
        hour_factor = self._diurnal_factor(hour, minute)
        dow_factor = 0.8 if weekday >= 5 else 1.0 + random.gauss(0, 0.05)
        scenario_mult = self._scenario_multiplier()

        state_key = f"{latitude:.2f}_{longitude:.2f}"
        prev = self._state.get(state_key, {})

        # Active dynamic noise (noise_std=12 for PM2.5 to guarantee live AQI fluctuations)
        pm25_base = baseline["pm25"] * hour_factor * dow_factor * scenario_mult
        pm25 = self._smooth_value(prev.get("pm25", pm25_base), pm25_base, noise_std=12.0)

        pm10 = pm25 * (1.5 + random.gauss(0, 0.2)) + random.gauss(0, 15)
        pm10 = max(10, pm10)

        no2_base = baseline["no2"] * hour_factor * dow_factor * scenario_mult
        no2 = self._smooth_value(prev.get("no2", no2_base), no2_base, noise_std=8.0)

        co_base = baseline["co"] * hour_factor * dow_factor * scenario_mult * 0.8
        co = self._smooth_value(prev.get("co", co_base), co_base, noise_std=0.25)

        so2_base = baseline["so2"] * (0.8 + random.gauss(0, 0.1)) * scenario_mult
        so2 = self._smooth_value(prev.get("so2", so2_base), so2_base, noise_std=3.0)

        o3_time_factor = 1.8 if 12 <= hour <= 16 else 0.6
        o3_base = baseline["o3"] * o3_time_factor * scenario_mult
        o3 = self._smooth_value(prev.get("o3", o3_base), o3_base, noise_std=6.0)

        temp_base = baseline["temperature"]
        temp_diurnal = temp_base + self._temperature_variation(hour)
        temperature = self._smooth_value(prev.get("temperature", temp_diurnal), temp_diurnal, noise_std=1.2)

        humidity_base = baseline["humidity"] - (temperature - temp_base) * 2
        humidity = self._smooth_value(prev.get("humidity", humidity_base), humidity_base, noise_std=3.0)
        humidity = max(30, min(95, humidity))

        pressure = self._smooth_value(prev.get("pressure", 1013), 1013, noise_std=1.5)
        wind_speed = max(0.5, self._smooth_value(prev.get("wind_speed", 3), 3, noise_std=1.0))
        wind_direction = (prev.get("wind_direction", random.uniform(0, 360)) + random.gauss(0, 10)) % 360

        self._state[state_key] = {
            "pm25": pm25, "pm10": pm10, "no2": no2, "co": co, "so2": so2, "o3": o3,
            "temperature": temperature, "humidity": humidity,
            "pressure": pressure, "wind_speed": wind_speed, "wind_direction": wind_direction,
        }

        return EnvironmentalReading(
            pm25=round(max(5, pm25), 1),
            pm10=round(max(10, pm10), 1),
            co=round(max(0.1, co), 2),
            no2=round(max(3, no2), 1),
            so2=round(max(2, so2), 1),
            o3=round(max(5, o3), 1),
            temperature=round(temperature, 1),
            humidity=round(humidity, 1),
            pressure=round(pressure, 1),
            wind_speed=round(wind_speed, 1),
            wind_direction=round(wind_direction, 0),
            source="SIMULATED",
            provider_name=self.name,
        )

    def _diurnal_factor(self, hour: int, minute: int) -> float:
        t = hour + minute / 60.0
        morning_peak = 1.4 * math.exp(-0.5 * ((t - 8.5) / 1.5) ** 2)
        evening_peak = 1.5 * math.exp(-0.5 * ((t - 20.0) / 2.0) ** 2)
        baseline = 0.65
        return max(0.5, baseline + morning_peak + evening_peak + random.gauss(0, 0.08))

    def _temperature_variation(self, hour: int) -> float:
        return 4 * math.sin(math.pi * (hour - 5) / 12) if 5 <= hour <= 17 else -2

    def _scenario_multiplier(self) -> float:
        multipliers = {
            SimulatorScenario.NORMAL: 1.0,
            SimulatorScenario.RUSH_HOUR: 1.6,
            SimulatorScenario.HIGH_POLLUTION: 2.2,
            SimulatorScenario.POLLUTION_SPIKE: 3.5,
            SimulatorScenario.SENSOR_FAILURE: 1.0,
        }
        return multipliers.get(self.scenario, 1.0)

    def _smooth_value(self, previous: float, target: float, noise_std: float = 1.0) -> float:
        alpha = 0.4
        smoothed = alpha * target + (1 - alpha) * previous
        return smoothed + random.gauss(0, noise_std)

    def _get_city_baseline(self, lat: float, lng: float) -> dict:
        cities = {
            "delhi": {"lat": 28.6, "lng": 77.2, "pm25": 85, "no2": 55, "co": 1.8, "so2": 18, "o3": 45, "temperature": 35, "humidity": 55},
            "mumbai": {"lat": 19.1, "lng": 72.9, "pm25": 55, "no2": 38, "co": 1.2, "so2": 14, "o3": 38, "temperature": 32, "humidity": 75},
            "chennai": {"lat": 13.1, "lng": 80.3, "pm25": 48, "no2": 32, "co": 1.0, "so2": 12, "o3": 42, "temperature": 33, "humidity": 72},
            "hyderabad": {"lat": 17.4, "lng": 78.4, "pm25": 52, "no2": 35, "co": 1.1, "so2": 13, "o3": 40, "temperature": 34, "humidity": 60},
            "bengaluru": {"lat": 12.9, "lng": 77.6, "pm25": 38, "no2": 28, "co": 0.8, "so2": 10, "o3": 35, "temperature": 28, "humidity": 65},
        }
        best_city = "chennai"
        best_dist = float("inf")
        for name, info in cities.items():
            dist = (lat - info["lat"]) ** 2 + (lng - info["lng"]) ** 2
            if dist < best_dist:
                best_dist = dist
                best_city = name
        return cities[best_city]
