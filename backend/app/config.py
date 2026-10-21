from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gemini_api_key: str | None = Field(
        default=None, alias="GEMINI_API_KEY"
    )
    gemini_model: str = Field(
        default="gemini-3.8-flash", alias="GEMINI_MODEL"
    )

    groq_api_key: str | None = Field(
        default=None, alias="GROQ_API_KEY"
    )
    groq_model: str = Field(
        default="openai/gpt-oss-120b", alias="GROQ_MODEL"
    )
    groq_base_url: str = Field(
        default="https://api.groq.com/openai/v1",
        alias="GROQ_BASE_URL",
    )

    gemini_http_timeout_seconds: float = Field(
        default=55, gt=0, le=180,
        alias="GEMINI_HTTP_TIMEOUT_SECONDS",
    )
    gemini_timeout_seconds: float = Field(
        default=60, gt=0, le=180,
        alias="GEMINI_TIMEOUT_SECONDS",
    )
    frontend_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        alias="FRONTEND_ORIGINS",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def allowed_origins(self) -> list[str]:
        return [
            origin.strip().rstrip("/")
            for origin in self.frontend_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
