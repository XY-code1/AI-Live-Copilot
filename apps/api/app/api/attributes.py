from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import AuthContext, get_auth_context
from app.crud import product as product_crud
from app.db.session import get_db
from app.models.product import ProductAttribute
from app.schemas.product import AttributeCreate, ProductAttributeOut

router = APIRouter()


@router.post(
    "/products/{product_id}/attributes",
    response_model=ProductAttributeOut,
    status_code=201,
)
def add_attribute(
    product_id: UUID,
    payload: AttributeCreate,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(get_auth_context),
) -> ProductAttributeOut:
    product = product_crud.get_product(db, product_id, auth.workspace_id)
    if product is None:
        raise HTTPException(status_code=404, detail="商品不存在")

    attribute = ProductAttribute(
        product_id=product.id,
        label=payload.label,
        value=payload.value,
        status=payload.status,
        origin="manual",
    )
    db.add(attribute)
    db.commit()
    db.refresh(attribute)
    return attribute


@router.delete("/attributes/{attribute_id}", status_code=204)
def delete_attribute(attribute_id: UUID, db: Session = Depends(get_db), auth: AuthContext = Depends(get_auth_context)) -> None:
    attribute = db.get(ProductAttribute, attribute_id)
    if attribute is None or attribute.product.workspace_id != auth.workspace_id:
        raise HTTPException(status_code=404, detail="属性不存在")
    db.delete(attribute)
    db.commit()
