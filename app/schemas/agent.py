from typing import Any

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    user_id: str = Field(..., description="Internal user identifier")
    chat_id: str | None = Field(default=None, description="Telegram chat ID if available")
    user_message: str
    use_case: str = Field(default="general_analysis")
    session_id: str | None = None


class AgentResult(BaseModel):
    answer_text: str
    mermaid_diagram: str | None = None
    raw_data_preview: dict[str, Any] | None = None
    response_id: str | None = None
