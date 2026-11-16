from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import product as product_crud
from app.db.session import get_db
from app.schemas.product import ProductOut
from app.services.extraction import extract_product_attributes

router = APIRouter()


@router.post("/products/{product_id}/extract", response_model=ProductOut)
def extract_product(product_id: UUID, db: Session = Depends(get_db)) -> ProductOut:
    product = product_crud.get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="商品不存在")
    try:
        extract_product_attributes(db, product)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    db.refresh(product)
    return product
