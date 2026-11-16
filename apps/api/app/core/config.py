from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "AI Live Copilot API"
    api_v1_prefix: str = "/api/v1"
    database_url: str = (
        "postgresql+psycopg://ai_live_copilot:change-me@localhost:5432/ai_live_copilot"
    )
    ai_provider: str = "deepseek"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
