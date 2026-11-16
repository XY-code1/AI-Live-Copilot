from fastapi import APIRouter

from app.api.products import router as products_router
from app.api.sources import router as sources_router

api_router = APIRouter()

api_router.include_router(products_router, prefix="/products", tags=["products"])
api_router.include_router(sources_router, tags=["sources"])


@api_router.get("/status", tags=["system"])
def status() -> dict[str, str]:
    return {"service": "ai-live-copilot-api", "status": "ready"}
