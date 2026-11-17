from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.auth import AuthContext, get_auth_context
from app.crud import comparison as comparison_crud
from app.crud import product as crud
from app.db.session import get_db
from app.schemas.comparison import ComparisonOut
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate

router = APIRouter()


@router.get("", response_model=list[ProductOut])
def list_products(
    q: str | None = Query(default=None, description="按名称、分类或简介搜索"),
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(get_auth_context),
) -> list[ProductOut]:
    return crud.list_products(db, auth.workspace_id, q)


@router.post("", response_model=ProductOut, status_code=201)
def create_product(payload: ProductCreate, db: Session = Depends(get_db), auth: AuthContext = Depends(get_auth_context)) -> ProductOut:
    return crud.create_product(db, payload, auth.workspace_id)


@router.get("/{product_id}/comparisons", response_model=list[ComparisonOut])
def list_comparisons(product_id: UUID, db: Session = Depends(get_db), auth: AuthContext = Depends(get_auth_context)) -> list[ComparisonOut]:
    return comparison_crud.list_comparisons(db, product_id, auth.workspace_id)


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: UUID, db: Session = Depends(get_db), auth: AuthContext = Depends(get_auth_context)) -> ProductOut:
    product = crud.get_product(db, product_id, auth.workspace_id)
    if product is None:
        raise HTTPException(status_code=404, detail="商品不存在")
    return product


@router.patch("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: UUID, payload: ProductUpdate, db: Session = Depends(get_db), auth: AuthContext = Depends(get_auth_context)
) -> ProductOut:
    product = crud.get_product(db, product_id, auth.workspace_id)
    if product is None:
        raise HTTPException(status_code=404, detail="商品不存在")
    return crud.update_product(db, product, payload)


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: UUID, db: Session = Depends(get_db), auth: AuthContext = Depends(get_auth_context)) -> None:
    product = crud.get_product(db, product_id, auth.workspace_id)
    if product is None:
        raise HTTPException(status_code=404, detail="商品不存在")
    crud.delete_product(db, product)
