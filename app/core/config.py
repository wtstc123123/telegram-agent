from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="telegram-ai-agent-starter", alias="APP_NAME")
    app_env: str = Field(default="dev", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    base_url: str = Field(default="https://example.com", alias="BASE_URL")

    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")
    telegram_webhook_secret: str = Field(default="", alias="TELEGRAM_WEBHOOK_SECRET")

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-5.2", alias="OPENAI_MODEL")
    openai_reasoning_effort: str = Field(default="low", alias="OPENAI_REASONING_EFFORT")
    openai_text_verbosity: str = Field(default="low", alias="OPENAI_TEXT_VERBOSITY")

    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")
    session_ttl_seconds: int = Field(default=86400, alias="SESSION_TTL_SECONDS")

    primary_data_api_base_url: str = Field(default="", alias="PRIMARY_DATA_API_BASE_URL")
    primary_data_api_key: str = Field(default="", alias="PRIMARY_DATA_API_KEY")
    primary_data_api_timeout_seconds: int = Field(default=20, alias="PRIMARY_DATA_API_TIMEOUT_SECONDS")
    primary_data_api_name: str = Field(default="primary_data_api", alias="PRIMARY_DATA_API_NAME")

    billing_api_base_url: str = Field(default="", alias="BILLING_API_BASE_URL")
    billing_api_key: str = Field(default="", alias="BILLING_API_KEY")
    billing_api_timeout_seconds: int = Field(default=20, alias="BILLING_API_TIMEOUT_SECONDS")
    billing_api_name: str = Field(default="billing_api", alias="BILLING_API_NAME")


@lru_cache
def get_settings() -> Settings:
    return Settings()
