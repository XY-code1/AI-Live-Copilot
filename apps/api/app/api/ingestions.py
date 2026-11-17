from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import AuthContext, get_auth_context
from app.db.session import get_db
from app.models.ingestion import IngestionRun
from app.models.product import Product
from app.schemas.ingestion import IngestionRunOut

router = APIRouter()


@router.get("/products/{product_id}/ingestion-runs", response_model=list[IngestionRunOut])
def list_runs(
    product_id: UUID,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(get_auth_context),
) -> list[IngestionRunOut]:
    statement = (
        select(IngestionRun)
        .where(IngestionRun.product_id == product_id)
        .order_by(IngestionRun.started_at.desc())
    )
    runs = list(db.scalars(statement).all())
    # Workspace isolation: only runs that belong to the caller's workspace or
    # to a product they can already read.
    product = db.get(Product, product_id)
    if product is None or product.workspace_id != auth.workspace_id:
        raise HTTPException(status_code=404, detail="商品不存在")
    return [run for run in runs if run.workspace_id == auth.workspace_id]
