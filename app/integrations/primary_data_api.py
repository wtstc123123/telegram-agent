from typing import Any

import httpx

from app.core.config import get_settings
from app.integrations.base import BaseRawApiClient

import logging

logger = logging.getLogger(__name__)


class PrimaryDataApiClient(BaseRawApiClient):
    """Primary raw data API.

    CLEAR LABEL: Replace the request path and auth format below with your actual
    upstream service details.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self.name = settings.primary_data_api_name
        self.base_url = settings.primary_data_api_base_url.rstrip("/")
        self.api_key = settings.primary_data_api_key
        self.timeout = settings.primary_data_api_timeout_seconds

    async def fetch_relevant_data(self, user_id: str, user_message: str) -> dict[str, Any]:
        if not self.base_url:
            return {
                "source": self.name,
                "warning": "PRIMARY_DATA_API_BASE_URL is not configured yet.",
                "sample_payload": {
                    "user_id": user_id,
                    "message": user_message,
                    "events": [
                        {"date": "2026-03-01", "requests": 1200, "errors": 21},
                        {"date": "2026-03-02", "requests": 1350, "errors": 18},
                    ],
                },
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "user_id": user_id,
            "query": user_message,
            "scope": "small",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/v1/raw-data/query", headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            logger.error("PrimaryDataApiClient request failed: %s", exc)
            return {
                "source": self.name,
                "error": {"type": "http_error", "detail": str(exc)},
            }

        return {
            "source": self.name,
            "data": data,
        }
