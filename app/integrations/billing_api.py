from typing import Any

import httpx

from app.core.config import get_settings
from app.integrations.base import BaseRawApiClient

import logging

logger = logging.getLogger(__name__)


class BillingApiClient(BaseRawApiClient):
    def __init__(self) -> None:
        settings = get_settings()
        self.name = settings.billing_api_name
        self.base_url = settings.billing_api_base_url.rstrip("/")
        self.api_key = settings.billing_api_key
        self.timeout = settings.billing_api_timeout_seconds

    async def fetch_relevant_data(self, user_id: str, user_message: str) -> dict[str, Any]:
        if not self.base_url:
            return {
                "source": self.name,
                "warning": "BILLING_API_BASE_URL is not configured yet.",
                "sample_payload": {
                    "user_id": user_id,
                    "query": user_message,
                    "invoices": [],
                },
            }

        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {"user_id": user_id, "query": user_message}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/v1/billing/summary", headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            logger.error("BillingApiClient request failed: %s", exc)
            return {
                "source": self.name,
                "error": {"type": "http_error", "detail": str(exc)},
            }

        return {
            "source": self.name,
            "data": data,
        }
