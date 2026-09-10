from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "WarrantyVault"
    database_url: str = "sqlite+pysqlite:///./warrantyvault.db"
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    upload_dir: Path = Path("uploads")
    max_upload_mb: int = 10
    gemini_api_key: str | None = Field(default=None, repr=False)
    chat_model: str = "gemini-3.5-flash"
    chat_fallback_model: str = "gemini-3.1-flash-lite"
    reminder_hour: int = 9
    reminder_timezone: str = "Asia/Kolkata"
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = Field(default=None, repr=False)
    smtp_from_email: str | None = None
    smtp_use_tls: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
