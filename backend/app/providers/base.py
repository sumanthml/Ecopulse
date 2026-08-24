"""
EcoPulse Data Provider - Abstract Base
All environmental data providers must implement this interface.
"""
from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class EnvironmentalReading:
    """Standardized environmental reading from any provider."""
    pm25: Optional[float] = None
    pm10: Optional[float] = None
    co: Optional[float] = None
    co2: Optional[float] = None
    no2: Optional[float] = None
    so2: Optional[float] = None
    o3: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[float] = None
    noise_level: Optional[float] = None
    source: str = "API"
    provider_name: str = "unknown"
    raw_data: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for ingestion pipeline."""
        return {
            "pm25": self.pm25,
            "pm10": self.pm10,
            "co": self.co,
            "co2": self.co2,
            "no2": self.no2,
            "so2": self.so2,
            "o3": self.o3,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "pressure": self.pressure,
            "wind_speed": self.wind_speed,
            "wind_direction": self.wind_direction,
            "noise_level": self.noise_level,
            "source": self.source,
        }


class EnvironmentalDataProvider(ABC):
    """
    Abstract base class for environmental data providers.
    
    All providers must implement fetch_latest() to return standardized
    EnvironmentalReading objects. The system selects the active provider
    via the DATA_PROVIDER environment variable.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable provider name."""
        ...

    @property
    @abstractmethod
    def source_type(self) -> str:
        """Source type: REAL, SIMULATED, API, HISTORICAL"""
        ...

    @abstractmethod
    async def fetch_latest(
        self,
        latitude: float,
        longitude: float,
    ) -> Optional[EnvironmentalReading]:
        """
        Fetch the latest environmental data for a location.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
        
        Returns:
            EnvironmentalReading or None if unavailable
        """
        raise NotImplementedError

    async def health_check(self) -> dict:
        """Check provider health/availability."""
        return {"provider": self.name, "status": "unknown"}
