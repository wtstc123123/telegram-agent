import json
import logging
from typing import Any

import redis

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class SessionStore:
    def __init__(self) -> None:
        settings = get_settings()
        self.client = redis.from_url(settings.redis_url, decode_responses=True)
        self.ttl = settings.session_ttl_seconds

    def get(self, key: str) -> dict[str, Any] | None:
        try:
            data = self.client.get(key)
            return json.loads(data) if data else None
        except Exception:
            logger.warning("Redis GET failed for key '%s'; continuing without session.", key, exc_info=True)
            return None

    def set(self, key: str, value: dict[str, Any]) -> None:
        try:
            self.client.set(key, json.dumps(value), ex=self.ttl)
        except Exception:
            logger.warning("Redis SET failed for key '%s'; session will not be persisted.", key, exc_info=True)
