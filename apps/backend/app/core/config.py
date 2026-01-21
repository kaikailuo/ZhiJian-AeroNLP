from __future__ import annotations

from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "ZhiJian-AeroNLP API"
    env: str = "development"
    api_prefix: str = "/api/v1"

    database_url: str = "sqlite:///./aeronlp.db"

    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 30
    refresh_token_days: int = 7

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60

    log_level: str = "INFO"
    request_id_header: str = "X-Request-ID"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
