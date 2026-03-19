import json
from typing import Any

from openai import OpenAI

from app.core.config import get_settings
from app.schemas.agent import AgentResult
from app.templates.prompting import SYSTEM_PROMPT, build_user_prompt


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

        payload = json.loads(response.output_text)
        return AgentResult(
            answer_text=payload.get("answer_text", ""),
            mermaid_diagram=payload.get("mermaid_diagram"),
            raw_data_preview=payload.get("raw_data_preview"),
            response_id=response.id,
        )
