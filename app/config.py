from functools import lru_cache

from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Controle de Licenças Ambientais"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60 * 24
    algorithm: str = "HS256"

    db_host: str = "185.239.210.103"
    db_name: str = "u625101450_Controle_LO"
    db_user: str = "u625101450_ekozen"
    db_password: str = "Asr$340522$Roxo"
    db_port: int = 3306

    sendgrid_api_key: str | None = None
    sendgrid_sender_email: str | None = None

    file_storage_dir: str = "uploads"

    frontend_base_url: AnyUrl | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
