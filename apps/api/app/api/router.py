from fastapi import APIRouter

api_router = APIRouter()


@api_router.get("/status", tags=["system"])
def status() -> dict[str, str]:
    return {"service": "ai-live-copilot-api", "status": "ready"}

