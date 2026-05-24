"""Load settings from environment variables (no hardcoded secrets)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    llm_model: str = Field(default="gpt-4o-mini", alias="LLM_MODEL")
    llm_enabled: bool = Field(default=True, alias="LLM_ENABLED")
    llm_timeout_seconds: int = Field(default=60, alias="LLM_TIMEOUT_SECONDS")

    hf_dataset_name: str = Field(
        default="ManikaSaini/zomato-restaurant-recommendation",
        alias="HF_DATASET_NAME",
    )
    data_cache_dir: Path = Field(default=PROJECT_ROOT / "data" / "cache", alias="DATA_CACHE_DIR")

    top_k: int = Field(default=5, alias="TOP_K")
    shortlist_max: int = Field(default=20, alias="SHORTLIST_MAX")
    min_rating_default: float = Field(default=0.0, alias="MIN_RATING_DEFAULT")

    @field_validator("data_cache_dir", mode="before")
    @classmethod
    def resolve_cache_dir(cls, value: str | Path) -> Path:
        path = Path(value)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        return path

    @field_validator("top_k", "shortlist_max", "llm_timeout_seconds")
    @classmethod
    def must_be_positive(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Numeric settings must be greater than zero.")
        return value

    @field_validator("min_rating_default")
    @classmethod
    def rating_in_range(cls, value: float) -> float:
        if not 0.0 <= value <= 5.0:
            raise ValueError("MIN_RATING_DEFAULT must be between 0 and 5.")
        return value

    def ensure_llm_configured(self) -> None:
        """Raise if LLM is enabled but no API key is set."""
        if self.llm_enabled and not self.openai_api_key:
            raise ValueError(
                "LLM is enabled but OPENAI_API_KEY is not set. "
                "Add it to .env or set LLM_ENABLED=false."
            )

    @property
    def project_root(self) -> Path:
        return PROJECT_ROOT


@lru_cache
def get_settings() -> Settings:
    return Settings()
