from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APPLYTRACK_", extra="ignore", env_file=".env")

    # Database
    database_url: str = Field(default="sqlite+aiosqlite:///./applytrack.db") # Default to SQLite for local dev
    
    # Security
    jwt_secret: str = Field(default="insecure-default-secret-change-me", min_length=8)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 1 week

    # Redis / Celery
    redis_url: str = Field(default="redis://localhost:6379/0")
    
    # AI
    openrouter_api_key: str = Field(default="sk-mock-key")
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "anthropic/claude-3.5-sonnet"
    openrouter_timeout_seconds: float = 60.0

settings = Settings()
