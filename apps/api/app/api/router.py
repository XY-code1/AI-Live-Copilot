from fastapi import APIRouter

from app.api.products import router as products_router

api_router = APIRouter()

api_router.include_router(products_router, prefix="/products", tags=["products"])


@api_router.get("/status", tags=["system"])
def status() -> dict[str, str]:
    return {"service": "ai-live-copilot-api", "status": "ready"}
