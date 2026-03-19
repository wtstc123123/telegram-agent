"""Tests for hardened behaviors added in bug-fix pass."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.renderers.mermaid import MermaidRenderer
from app.schemas.agent import AgentResult
from app.services.openai_client import OpenAIResponseService


# ---------------------------------------------------------------------------
# Telegram webhook – unsupported update types
# ---------------------------------------------------------------------------

client = TestClient(app)


def _webhook_post(payload: dict[str, Any], secret: str | None = None) -> Any:
    headers = {}
    if secret:
        headers["X-Telegram-Bot-Api-Secret-Token"] = secret
    return client.post("/telegram/webhook", json=payload)


class TestTelegramWebhookIgnoredUpdates:
    """Non-message updates must return 200 {"status": "ignored"}."""

    def test_callback_query_update_ignored(self) -> None:
        """An update containing only callback_query (no message) is ignored."""
        payload = {
            "update_id": 1,
            "callback_query": {
                "id": "abc",
                "from": {"id": 99, "is_bot": False, "first_name": "Test"},
                "data": "some_button",
            },
        }
        response = _webhook_post(payload)
        assert response.status_code == 200
        assert response.json() == {"status": "ignored"}

    def test_channel_post_without_text_ignored(self) -> None:
        """A message update that has a chat but no text is ignored."""
        payload = {
            "update_id": 2,
            "message": {
                "message_id": 10,
                "chat": {"id": 100, "type": "private"},
                "sticker": {},
            },
        }
        response = _webhook_post(payload)
        assert response.status_code == 200
        assert response.json() == {"status": "ignored"}

    def test_message_without_chat_ignored(self) -> None:
        """A message update lacking a chat object is ignored without error."""
        payload = {
            "update_id": 3,
            "message": {
                "message_id": 11,
                "text": "hello",
            },
        }
        response = _webhook_post(payload)
        assert response.status_code == 200
        assert response.json() == {"status": "ignored"}


# ---------------------------------------------------------------------------
# Mermaid renderer – session_id sanitization
# ---------------------------------------------------------------------------


class TestMermaidRendererSanitization:
    def _make_renderer(self) -> tuple[MermaidRenderer, Path]:
        tmp = tempfile.mkdtemp()
        return MermaidRenderer(base_dir=tmp), Path(tmp)

    def test_safe_filename_plain(self) -> None:
        assert MermaidRenderer._safe_filename("abc123") == "abc123"

    def test_safe_filename_colon_allowed(self) -> None:
        """telegram:<chat_id> style IDs must be preserved."""
        assert MermaidRenderer._safe_filename("telegram:12345") == "telegram:12345"

    def test_safe_filename_strips_path_separators(self) -> None:
        sanitized = MermaidRenderer._safe_filename("../../etc/passwd")
        assert "/" not in sanitized
        assert "\\" not in sanitized
        assert ".." not in sanitized

    def test_save_source_stays_inside_base_dir(self) -> None:
        renderer, base = self._make_renderer()
        renderer.save_source(session_id="../../evil", mermaid_text="graph TD; A-->B")
        # The only .mmd file must reside directly in base_path
        files = list(base.iterdir())
        assert len(files) == 1
        assert files[0].parent == base

    def test_save_source_empty_session_id_fallback(self) -> None:
        """An empty session_id after sanitization uses '_' as the filename."""
        renderer, base = self._make_renderer()
        renderer.save_source(session_id="", mermaid_text="graph TD;")
        files = list(base.iterdir())
        assert len(files) == 1
        assert files[0].name == "_.mmd"


# ---------------------------------------------------------------------------
# OpenAI client – robust JSON parsing
# ---------------------------------------------------------------------------


def _make_mock_response(output_text: str, response_id: str = "resp_123") -> MagicMock:
    mock_resp = MagicMock()
    mock_resp.output_text = output_text
    mock_resp.id = response_id
    return mock_resp


class TestOpenAIResponseServiceParsing:
    def _make_service(self) -> OpenAIResponseService:
        with patch("app.services.openai_client.OpenAI"):
            svc = OpenAIResponseService.__new__(OpenAIResponseService)
            svc.model = "test-model"
            svc.reasoning_effort = "low"
            svc.text_verbosity = "low"
            svc.client = MagicMock()
        return svc

    def test_valid_json_parsed_correctly(self) -> None:
        svc = self._make_service()
        payload = {"answer_text": "Hello!", "mermaid_diagram": None, "raw_data_preview": None}
        mock_resp = _make_mock_response(json.dumps(payload))
        svc.client.responses.create.return_value = mock_resp

        result = svc.analyze("hi", {})

        assert isinstance(result, AgentResult)
        assert result.answer_text == "Hello!"

    def test_invalid_json_returns_fallback(self) -> None:
        svc = self._make_service()
        mock_resp = _make_mock_response("this is not json at all")
        svc.client.responses.create.return_value = mock_resp

        result = svc.analyze("hi", {})

        assert isinstance(result, AgentResult)
        assert result.answer_text != ""
        assert result.response_id == "resp_123"

    def test_non_object_json_returns_fallback(self) -> None:
        svc = self._make_service()
        mock_resp = _make_mock_response(json.dumps(["list", "not", "dict"]))
        svc.client.responses.create.return_value = mock_resp

        result = svc.analyze("hi", {})

        assert isinstance(result, AgentResult)
        assert result.answer_text != ""

    def test_empty_output_text_returns_fallback(self) -> None:
        svc = self._make_service()
        mock_resp = _make_mock_response("")
        svc.client.responses.create.return_value = mock_resp

        result = svc.analyze("hi", {})

        assert isinstance(result, AgentResult)
        assert result.answer_text != ""

    def test_missing_output_text_attr_returns_fallback(self) -> None:
        svc = self._make_service()
        mock_resp = MagicMock(spec=[])  # no attributes at all
        mock_resp.id = "resp_999"
        svc.client.responses.create.return_value = mock_resp

        result = svc.analyze("hi", {})

        assert isinstance(result, AgentResult)
        assert result.answer_text != ""
