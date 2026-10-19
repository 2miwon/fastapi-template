"""Global settings. Domain-specific settings live in each module's `config.py`."""

from typing import Any

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.constants import Environment


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "FastAPI Template"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: Environment = Environment.PRODUCTION

    DATABASE_URL: PostgresDsn | str
    DATABASE_POOL_SIZE: int = 16
    DATABASE_POOL_TTL: int = 60 * 20  # 20 minutes
    DATABASE_POOL_PRE_PING: bool = True

    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    CORS_ORIGINS_REGEX: str | None = None
    CORS_HEADERS: list[str] = ["*"]


settings = Config()

app_configs: dict[str, Any] = {"title": settings.APP_NAME, "version": settings.APP_VERSION}
# Hide interactive docs outside of debug environments.
if not settings.ENVIRONMENT.is_debug:
    app_configs["openapi_url"] = None
