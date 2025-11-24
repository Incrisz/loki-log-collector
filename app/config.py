from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="LOKI_",
        case_sensitive=False,
        env_file=(".env",),
        env_file_encoding="utf-8",
    )

    url: str = "http://localhost:3100"
    tenant_id: Optional[str] = None
    basic_auth_user: Optional[str] = None
    basic_auth_password: Optional[str] = None

    # Whether to log payloads at info level (may be noisy)
    log_payloads: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
