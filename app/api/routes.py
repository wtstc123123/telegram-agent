from fastapi import APIRouter, Header, HTTPException

from app.core.config import get_settings
from app.schemas.agent import AnalyzeRequest
from app.schemas.telegram import TelegramWebhookEnvelope
from app.services.agent_service import AgentService
from app.services.telegram_service import TelegramService

health_router = APIRouter(tags=["health"])
telegram_router = APIRouter(prefix="/telegram", tags=["telegram"])
agent_router = APIRouter(prefix="/agent", tags=["agent"])

settings = get_settings()
agent_service = AgentService()
telegram_service = TelegramService()


@health_router.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@agent_router.post("/analyze")
async def analyze(request: AnalyzeRequest):
    result = await agent_service.run(
        user_id=request.user_id,
        user_message=request.user_message,
        session_id=request.session_id,
    )
    return result.model_dump()


@telegram_router.post("/webhook")
async def telegram_webhook(
    envelope: TelegramWebhookEnvelope,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
):
    if settings.telegram_webhook_secret and x_telegram_bot_api_secret_token != settings.telegram_webhook_secret:
        raise HTTPException(status_code=401, detail="Invalid Telegram secret token")

    message = envelope.message or envelope.edited_message or {}
    chat = message.get("chat", {})
    from_user = message.get("from", {})
    text = message.get("text", "")

    if not chat or not text:
        return {"status": "ignored"}

    chat_id = chat.get("id")
    user_id = str(from_user.get("id", chat_id))
    session_id = f"telegram:{chat_id}"

    result = await agent_service.run(user_id=user_id, user_message=text, session_id=session_id)
    reply_text = result.answer_text
    if result.mermaid_diagram:
        reply_text += "\n\n[Mermaid diagram generated and saved on server]"

    await telegram_service.send_message(chat_id=chat_id, text=reply_text)
    return {"status": "processed"}
