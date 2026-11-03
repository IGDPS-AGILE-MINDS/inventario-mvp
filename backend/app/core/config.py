from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=Path(__file__).resolve().parents[3] / ".env", extra="ignore")

    database_url: str
    cors_origins: str = "http://localhost,http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [value.strip().rstrip("/") for value in self.cors_origins.split(",") if value.strip().rstrip("/")]


settings = Settings()
