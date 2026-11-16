from fastapi import APIRouter

from app.api.attributes import router as attributes_router
from app.api.comparisons import router as comparisons_router
from app.api.competitors import router as competitors_router
from app.api.extraction import router as extraction_router
from app.api.products import router as products_router
from app.api.sources import router as sources_router

api_router = APIRouter()

api_router.include_router(products_router, prefix="/products", tags=["products"])
api_router.include_router(sources_router, tags=["sources"])
api_router.include_router(extraction_router, tags=["extraction"])
api_router.include_router(attributes_router, tags=["attributes"])
api_router.include_router(competitors_router, prefix="/competitors", tags=["competitors"])
api_router.include_router(comparisons_router, prefix="/comparisons", tags=["comparisons"])


@api_router.get("/status", tags=["system"])
def status() -> dict[str, str]:
    return {"service": "ai-live-copilot-api", "status": "ready"}
