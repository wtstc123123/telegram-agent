import uuid

from app.schemas.agent import AgentResult
from app.services.data_broker import DataBroker
from app.services.openai_client import OpenAIResponseService
from app.services.session_store import SessionStore
from app.renderers.mermaid import MermaidRenderer


class AgentService:
    def __init__(self) -> None:
        self.broker = DataBroker()
        self.openai = OpenAIResponseService()
        self.sessions = SessionStore()
        self.renderer = MermaidRenderer()

    async def run(self, user_id: str, user_message: str, session_id: str | None = None) -> AgentResult:
        session_id = session_id or str(uuid.uuid4())
        session_key = f"session:{session_id}"
        existing = self.sessions.get(session_key) or {}

        raw_context = await self.broker.fetch_context(user_id=user_id, user_message=user_message)
        result = self.openai.analyze(
            user_message=user_message,
            raw_context=raw_context,
            previous_response_id=existing.get("last_response_id"),
        )

        if result.mermaid_diagram:
            self.renderer.save_source(session_id=session_id, mermaid_text=result.mermaid_diagram)

        self.sessions.set(
            session_key,
            {
                "user_id": user_id,
                "last_response_id": result.response_id,
            },
        )
        return result
