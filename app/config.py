"""Application configuration using Pydantic Settings."""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized application settings loaded from environment variables / .env file.
    All fields have sensible defaults for local development.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ────────────────────────────────────────────────────────────
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    base_url: str = "http://localhost:8000"
    app_version: str = "0.1.0"

    # ── Database ───────────────────────────────────────────────────────────────
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres123@localhost:5432/urlshortener"
    )

    # ── Redis ──────────────────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"
    redis_ttl_seconds: int = 86400          # 24 giờ — TTL mặc định cho cache URL
    redis_negative_ttl_seconds: int = 300   # 5 phút — TTL cho cache NOT_FOUND

    # ── Security ───────────────────────────────────────────────────────────────
    secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    domain_blacklist: str = ""

    # ── Logging ────────────────────────────────────────────────────────────────
    log_level: str = "DEBUG"

    # ── Short Code ─────────────────────────────────────────────────────────────
    short_code_length: int = 7
    short_code_max_retries: int = 5

    # ── Properties ─────────────────────────────────────────────────────────────
    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def blacklisted_domains(self) -> list[str]:
        return [d.strip().lower() for d in self.domain_blacklist.split(",") if d.strip()]

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return upper


@lru_cache
def get_settings() -> Settings:
    """
    Return cached Settings instance.
    Use lru_cache to avoid re-reading .env file on every call.
    """
    return Settings()
