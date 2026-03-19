from abc import ABC, abstractmethod
from typing import Any


class BaseRawApiClient(ABC):
    """Base class for upstream raw data APIs.

    Add one client per upstream service. Keep each client isolated so you can
    expand API coverage later without rewriting the agent flow.
    """

    name: str

    @abstractmethod
    async def fetch_relevant_data(self, user_id: str, user_message: str) -> dict[str, Any]:
        raise NotImplementedError
