from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "AI Live Copilot API"
    api_v1_prefix: str = "/api/v1"
    database_url: str = (
        "postgresql+psycopg://ai_live_copilot:change-me@localhost:5432/ai_live_copilot"
    )
    ai_provider: str = "deepseek"
    environment: str = "development"
    auth_mode: str = "dev"
    clerk_issuer: str = ""
    clerk_audience: str = ""
    clerk_jwt_key: str = ""
    clerk_jwks_url: str = ""
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    storage_dir: str = "storage"
    max_upload_bytes: int = 15 * 1024 * 1024
    max_url_response_bytes: int = 2 * 1024 * 1024
    max_pdf_pages: int = 100
    sentry_dsn: str = ""
    sentry_traces_sample_rate: float = 0.1
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg://", 1)
        if value.startswith("postgresql://") and "+" not in value.split(":", 1)[0]:
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
