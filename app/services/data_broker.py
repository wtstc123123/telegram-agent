from typing import Any

from app.integrations.billing_api import BillingApiClient
from app.integrations.primary_data_api import PrimaryDataApiClient


class DataBroker:
    """Single place that decides which raw API payloads are passed to the model.

    This keeps your architecture flexible without forcing a heavy tool layer.
    Add more upstream API clients here as you expand coverage.
    """

    def __init__(self) -> None:
        self.primary = PrimaryDataApiClient()
        self.billing = BillingApiClient()

    async def fetch_context(self, user_id: str, user_message: str) -> dict[str, Any]:
        bundles: list[dict[str, Any]] = []

        bundles.append(await self.primary.fetch_relevant_data(user_id=user_id, user_message=user_message))

        keywords = {"billing", "invoice", "payment", "cost", "subscription"}
        if any(word in user_message.lower() for word in keywords):
            bundles.append(await self.billing.fetch_relevant_data(user_id=user_id, user_message=user_message))

        return {
            "user_id": user_id,
            "message": user_message,
            "sources": bundles,
        }
