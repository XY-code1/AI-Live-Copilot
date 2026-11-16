from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


def list_products(db: Session, q: str | None = None) -> list[Product]:
    statement = select(Product).order_by(Product.created_at.desc())
    if q:
        pattern = f"%{q}%"
        statement = statement.where(
            Product.name.ilike(pattern)
            | Product.category.ilike(pattern)
            | Product.summary.ilike(pattern)
        )
    return list(db.scalars(statement).all())


def get_product(db: Session, product_id: UUID) -> Product | None:
    return db.get(Product, product_id)


def create_product(db: Session, payload: ProductCreate) -> Product:
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product: Product, payload: ProductUpdate) -> Product:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: Product) -> None:
    db.delete(product)
    db.commit()
