from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:  # pragma: no cover
    boto3 = None  # type: ignore[assignment]
    BotoCoreError = Exception  # type: ignore[misc,assignment]
    ClientError = Exception  # type: ignore[misc,assignment]


@dataclass(frozen=True)
class AwsSecretLoadResult:
    data: dict[str, Any]
    source: str


def load_secrets_manager_json(secret_id: str, region_name: str | None = None) -> AwsSecretLoadResult:
    """Load a JSON blob from AWS Secrets Manager.

    The secret value must be a JSON object whose keys match the environment
    variable names used by :class:`~app.core.config.Settings` (e.g.
    ``OPENAI_API_KEY``, ``TELEGRAM_BOT_TOKEN``).

    Set ``LOAD_SECRETS_MANAGER=true`` and ``AWS_SECRETS_MANAGER_SECRET_ID``
    in your environment to enable this at startup.  IAM role credentials
    (instance profile / ECS task role) are used automatically when running on
    AWS; no static keys are required.

    Example secret value::

        {
          "OPENAI_API_KEY": "sk-...",
          "TELEGRAM_BOT_TOKEN": "123456:ABC...",
          "PRIMARY_DATA_API_KEY": "...",
          "BILLING_API_KEY": "..."
        }
    """
    if not secret_id:
        return AwsSecretLoadResult(data={}, source="secrets_manager:disabled")

    if boto3 is None:
        raise RuntimeError(
            "boto3 is not installed. Add boto3 to requirements.txt to use AWS Secrets Manager."
        )

    client = boto3.client("secretsmanager", region_name=region_name)
    try:
        resp = client.get_secret_value(SecretId=secret_id)
    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(
            f"Failed to load secret '{secret_id}' from AWS Secrets Manager: {exc}"
        ) from exc

    secret_string = resp.get("SecretString")
    if not secret_string:
        raise RuntimeError(
            "SecretString was empty; the secret must be stored as a JSON string."
        )

    try:
        data = json.loads(secret_string)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Secret '{secret_id}' is not valid JSON: {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise RuntimeError(
            f"Secret '{secret_id}' must be a JSON object (key/value pairs)."
        )

    return AwsSecretLoadResult(
        data={str(k): v for k, v in data.items()},
        source=f"secrets_manager:{secret_id}",
    )
