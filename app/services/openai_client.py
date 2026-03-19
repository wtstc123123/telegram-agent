import json
import logging
from typing import Any

from openai import OpenAI

from app.core.config import get_settings
from app.schemas.agent import AgentResult
from app.templates.prompting import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)


class OpenAIResponseService:
    def __init__(self) -> None:
        settings = get_settings()
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.reasoning_effort = settings.openai_reasoning_effort
        self.text_verbosity = settings.openai_text_verbosity

    def analyze(self, user_message: str, raw_context: dict[str, Any], previous_response_id: str | None = None) -> AgentResult:
        response = self.client.responses.create(
            model=self.model,
            previous_response_id=previous_response_id,
            reasoning={"effort": self.reasoning_effort},
            text={"verbosity": self.text_verbosity},
            input=[
                {"role": "system", "content": [{"type": "input_text", "text": SYSTEM_PROMPT}]},
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": build_user_prompt(user_message, raw_context)}],
                },
            ],
        )

        output_text = getattr(response, "output_text", None) or ""
        try:
            payload = json.loads(output_text)
        except (json.JSONDecodeError, ValueError):
            logger.warning(
                "OpenAI response could not be parsed as JSON (response_id=%s). Raw output: %.500s",
                getattr(response, "id", "unknown"),
                output_text,
            )
            return AgentResult(
                answer_text="I received a response but could not format it correctly. Please try again.",
                response_id=getattr(response, "id", None),
            )

        if not isinstance(payload, dict):
            logger.warning(
                "OpenAI response JSON is not an object (response_id=%s).",
                getattr(response, "id", "unknown"),
            )
            return AgentResult(
                answer_text="I received an unexpected response format. Please try again.",
                response_id=getattr(response, "id", None),
            )

        return AgentResult(
            answer_text=payload.get("answer_text", ""),
            mermaid_diagram=payload.get("mermaid_diagram"),
            raw_data_preview=payload.get("raw_data_preview"),
            response_id=getattr(response, "id", None),
        )
