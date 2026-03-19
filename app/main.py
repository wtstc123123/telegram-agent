from fastapi import FastAPI

from app.api.routes import health_router, telegram_router, agent_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name)
app.include_router(health_router)
app.include_router(telegram_router)
app.include_router(agent_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "environment": settings.app_env,
        "docs": "/docs",
    }
