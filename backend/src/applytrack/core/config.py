import logging
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

log = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Central configuration pulled from environment variables.

    Every setting has a safe default so the app starts without a .env file.
    For production, override via env vars or a .env file in the project root.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- database ---
    database_url: str = "sqlite+aiosqlite:///./applytrack.db"

    # --- auth ---
    jwt_secret: str = Field(
        default="local-dev-jwt-secret-change-in-production",
        min_length=16,
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    allow_registration: bool = True

    # --- cors ---
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # --- redis / celery ---
    redis_url: str = "redis://localhost:6379/0"
    celery_always_eager: bool = False  # set True for local dev without Redis

    # --- ai ---
    ai_mode: Literal["mock", "real"] = "mock"
    ai_provider: str = "openrouter"
    ai_api_key: str = ""
    ai_base_url: str = "https://openrouter.ai/api/v1"
    ai_model: str = "anthropic/claude-3.5-sonnet"
    ai_timeout_seconds: float = 60.0

    # --- logging ---
    log_level: str = "INFO"


settings = Settings()

# Wire up root logger based on config
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
