from typing import Any

from pydantic import BaseModel


class TelegramWebhookEnvelope(BaseModel):
    update_id: int | None = None
    message: dict[str, Any] | None = None
    edited_message: dict[str, Any] | None = None
