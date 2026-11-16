from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.storage import save_upload
from app.crud import product as product_crud
from app.db.session import get_db
from app.models.product import ProductSource, ProductSourceStatus, ProductSourceType
from app.schemas.product import ProductSourceOut
from app.schemas.source import SourceTextOut, UrlSourceCreate
from app.services.pdf import extract_pdf_text
from app.services.url import fetch_url_text

router = APIRouter()


@router.post("/products/{product_id}/sources", response_model=ProductSourceOut, status_code=201)
def upload_source(
    product_id: UUID,
    file: UploadFile = File(...),
    reference: str | None = Form(default=None),
    db: Session = Depends(get_db),
) -> ProductSourceOut:
    product = product_crud.get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="商品不存在")

    data = file.file.read()
    if not data:
        raise HTTPException(status_code=400, detail="文件为空")

    filename = Path(file.filename or "upload.pdf").name
    storage_path = save_upload(data, filename)
    text, page_count = extract_pdf_text(data)

    source = ProductSource(
        product_id=product.id,
        type=ProductSourceType.pdf,
        name=filename,
        reference=reference,
        storage_path=storage_path,
        status=ProductSourceStatus.ready,
        content_text=text,
        page_count=page_count,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@router.get("/sources/{source_id}", response_model=SourceTextOut)
def read_source_text(source_id: UUID, db: Session = Depends(get_db)) -> SourceTextOut:
    source = db.get(ProductSource, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="资料不存在")
    return SourceTextOut(
        id=source.id,
        product_id=source.product_id,
        name=source.name,
        reference=source.reference,
        page_count=source.page_count,
        text=source.content_text or "",
    )


@router.post("/products/{product_id}/sources/url", response_model=ProductSourceOut, status_code=201)
def create_url_source(
    product_id: UUID,
    payload: UrlSourceCreate,
    db: Session = Depends(get_db),
) -> ProductSourceOut:
    product = product_crud.get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="商品不存在")

    try:
        title, text = fetch_url_text(payload.url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    source = ProductSource(
        product_id=product.id,
        type=ProductSourceType.url,
        name=title,
        reference=payload.url,
        storage_path=payload.url,
        status=ProductSourceStatus.ready,
        content_text=text,
        page_count=None,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source
