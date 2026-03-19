import json
from typing import Any

import redis

from app.core.config import get_settings


class SessionStore:
    def __init__(self) -> None:
        settings = get_settings()
        self.client = redis.from_url(settings.redis_url, decode_responses=True)
        self.ttl = settings.session_ttl_seconds

    def get(self, key: str) -> dict[str, Any] | None:
        data = self.client.get(key)
        return json.loads(data) if data else None

    def set(self, key: str, value: dict[str, Any]) -> None:
        self.client.set(key, json.dumps(value), ex=self.ttl)
