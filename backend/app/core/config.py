"""
EcoPulse Core Configuration
Centralized settings loaded from environment variables.
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from .env file or environment variables."""

    # Application
    app_name: str = "EcoPulse"
    app_env: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    # Supabase
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_anon_key: str = ""

    # Database
    database_url: str = ""

    # Groq AI
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # Data Provider
    data_provider: str = "simulator"  # openmeteo | openaq | simulator
    data_provider_api_key: str = ""

    # Demo Mode
    demo_mode: bool = True

    # Data Collection
    data_collection_interval: int = 60  # seconds

    # CORS
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def has_database(self) -> bool:
        return bool(self.database_url)

    @property
    def has_groq(self) -> bool:
        return bool(self.groq_api_key)

    @property
    def has_supabase(self) -> bool:
        return bool(self.supabase_url and self.supabase_service_role_key)

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# Singleton settings instance
settings = Settings()
