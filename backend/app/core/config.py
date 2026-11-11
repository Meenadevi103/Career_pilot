"""Core application configuration and environment settings."""

import json
from typing import Annotated, Any

from pydantic import BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors_origins(v: Any) -> list[str]:
    """Parse CORS origins from list, JSON array, or comma-delimited string."""
    if isinstance(v, str):
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                pass
        return [origin.strip() for origin in v.split(",") if origin.strip()]
    elif isinstance(v, list):
        return v
    return ["http://localhost:5173"]


class Settings(BaseSettings):
    """Application settings read strictly from environment variables or .env."""

    PROJECT_NAME: str = "CareerPilot AI"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str

    # Authentication & Cookies
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    COOKIE_SECURE: bool = False
    COOKIE_NAME: str = "access_token"
    JWT_ALGORITHM: str = "HS256"

    # Database & Cache
    DATABASE_URL: str = "postgresql+psycopg://careerpilot_user:careerpilot_password@localhost:5433/careerpilot"
    TEST_DATABASE_URL: str = "postgresql+psycopg://careerpilot_user:careerpilot_password@localhost:5433/careerpilot_test"
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS & Frontend Origins
    CORS_ORIGINS: Annotated[list[str], BeforeValidator(parse_cors_origins)] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]
    FRONTEND_URL: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
