from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.crud import product as crud
from app.db.session import get_db
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate

router = APIRouter()


@router.get("", response_model=list[ProductOut])
def list_products(
    q: str | None = Query(default=None, description="按名称、分类或简介搜索"),
    db: Session = Depends(get_db),
) -> list[ProductOut]:
    return crud.list_products(db, q)


@router.post("", response_model=ProductOut, status_code=201)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)) -> ProductOut:
    return crud.create_product(db, payload)


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: UUID, db: Session = Depends(get_db)) -> ProductOut:
    product = crud.get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="商品不存在")
    return product


@router.patch("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: UUID, payload: ProductUpdate, db: Session = Depends(get_db)
) -> ProductOut:
    product = crud.get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="商品不存在")
    return crud.update_product(db, product, payload)


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: UUID, db: Session = Depends(get_db)) -> None:
    product = crud.get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="商品不存在")
    crud.delete_product(db, product)
