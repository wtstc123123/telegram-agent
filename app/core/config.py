import os
from functools import lru_cache
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.aws_secrets import load_secrets_manager_json


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="telegram-ai-agent-starter", alias="APP_NAME")
    app_env: str = Field(default="dev", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    base_url: str = Field(default="https://example.com", alias="BASE_URL")

    # AWS Secrets Manager (optional).
    # Set LOAD_SECRETS_MANAGER=true and AWS_SECRETS_MANAGER_SECRET_ID to load
    # all API keys from a single Secrets Manager JSON secret at startup.
    # IAM role credentials are used automatically on AWS (no static keys needed).
    load_secrets_manager: bool = Field(default=False, alias="LOAD_SECRETS_MANAGER")
    aws_region: str = Field(default="us-east-1", alias="AWS_REGION")
    aws_secrets_manager_secret_id: str = Field(default="", alias="AWS_SECRETS_MANAGER_SECRET_ID")

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


def _apply_secrets_manager_overrides(s: Settings) -> Settings:
    """Reload Settings after injecting Secrets Manager values into os.environ."""
    result = load_secrets_manager_json(
        secret_id=s.aws_secrets_manager_secret_id,
        region_name=s.aws_region,
    )
    overrides: dict[str, Any] = result.data
    if not overrides:
        return s
    # Inject into os.environ so the second Settings() load picks them up.
    # Existing env vars are NOT overwritten (Secrets Manager acts as a fallback
    # for values not already in the environment).
    for k, v in overrides.items():
        os.environ.setdefault(k, str(v))
    return Settings()


@lru_cache
def get_settings() -> Settings:
    """Return application settings.

    When ``LOAD_SECRETS_MANAGER=true`` the function fetches a JSON secret from
    AWS Secrets Manager and merges its values into the settings before
    returning.  Local ``.env`` files still work without any AWS credentials.
    """
    s = Settings()
    if s.load_secrets_manager:
        s = _apply_secrets_manager_overrides(s)
    return s
