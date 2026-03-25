from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    sql_connection_string: str | None = None
    sql_server: str | None = None
    sql_database: str | None = None
    sql_port: int = 1433
    azure_client_id: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
