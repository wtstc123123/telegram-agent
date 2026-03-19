import logging

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class TelegramService:
    def __init__(self) -> None:
        settings = get_settings()
        self.token = settings.telegram_bot_token
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    async def send_message(self, chat_id: int | str, text: str) -> dict:
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.post(
                    f"{self.base_url}/sendMessage",
                    json={"chat_id": chat_id, "text": text},
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as exc:
            logger.error("Failed to send Telegram message to chat_id=%s: %s", chat_id, exc)
            return {}
