"""
EcoPulse Backend Configuration
Uses Pydantic BaseSettings to load and validate environment variables.
"""
from typing import Optional, Union, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings with environment variable auto-loading."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_env: str = Field(default="development", alias="APP_ENV")
    secret_key: str = Field(default="ecopulse_secret_key_change_in_production_2026", alias="SECRET_KEY")

    # Supabase
    supabase_url: Optional[str] = Field(default=None, alias="SUPABASE_URL")
    supabase_anon_key: Optional[str] = Field(default=None, alias="SUPABASE_ANON_KEY")
    supabase_service_role_key: Optional[str] = Field(default=None, alias="SUPABASE_SERVICE_ROLE_KEY")

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/ecopulse",
        alias="DATABASE_URL",
    )

    # Groq AI
    groq_api_key: Optional[str] = Field(default=None, alias="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.3-70b-versatile", alias="GROQ_MODEL")

    # Data Provider
    data_provider: str = Field(default="simulator", alias="DATA_PROVIDER")
    data_provider_api_key: Optional[str] = Field(default=None, alias="DATA_PROVIDER_API_KEY")

    # Demo Mode
    demo_mode: bool = Field(default=True, alias="DEMO_MODE")

    # Data Collection Interval (seconds)
    data_collection_interval: int = Field(default=30, alias="DATA_COLLECTION_INTERVAL")

    # CORS Settings — accepts string '*', comma-separated string, or list
    cors_origins: Union[List[str], str] = Field(
        default=["*"],
        alias="CORS_ORIGINS",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            if v.strip() == "*":
                return ["*"]
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @property
    def has_database(self) -> bool:
        return bool(self.database_url and "localhost" not in self.database_url)

    @property
    def has_groq(self) -> bool:
        return bool(self.groq_api_key)


settings = Settings()
