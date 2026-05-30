from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuracoes da aplicacao carregadas a partir de variaveis de ambiente."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "PUCPR Auth Server"
    environment: Literal["development", "test", "production"] = "development"
    api_prefix: str = "/api"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/pucbr_backend"
    database_schema: str = "public"
    database_echo: bool = False
    auto_create_schema: bool = True
    seed_data: bool = True

    jwt_secret: str = Field(
        default="replace-this-secret-in-production-with-at-least-32-characters",
        min_length=32,
    )
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "PUCPR AuthServer"
    jwt_user_claim: str = "user"
    admin_token_expire_hours: int = 1
    user_token_expire_hours: int = 24
    media_root: str = "storage"

    bootstrap_admin_email: str = "admin@admin.com"
    bootstrap_admin_password: str = "admin"
    bootstrap_admin_name: str = "Auth Server Administrator"

    cors_allowed_origins: tuple[str, ...] = ("*",)
    cors_allowed_methods: tuple[str, ...] = ("*",)
    cors_allowed_headers: tuple[str, ...] = ("*",)

    avatar_storage_backend: Literal["local", "s3"] = "local"
    avatar_max_size_bytes: int = 5 * 1024 * 1024
    avatar_local_root: str = "avatars"
    avatar_s3_bucket: str = ""
    avatar_s3_region: str = "us-east-1"
    avatar_s3_endpoint_url: str | None = None
    avatar_s3_access_key_id: str | None = None
    avatar_s3_secret_access_key: str | None = None
    avatar_s3_url_expire_seconds: int = 900


@lru_cache
def get_settings() -> Settings:
    """Retorna uma instancia em cache das configuracoes do processo."""
    return Settings()
