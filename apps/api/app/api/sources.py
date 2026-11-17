from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.auth import AuthContext, get_auth_context
from app.core.config import settings
from app.core.storage import save_upload
from app.crud import product as product_crud
from app.db.session import get_db
from app.models.product import ProductSource, ProductSourceStatus, ProductSourceType
from app.schemas.product import ProductSourceOut
from app.schemas.source import SourceTextOut, UrlSourceCreate
from app.services.ocr import extract_image_text
from app.services.pdf import extract_pdf_text
from app.services.url import fetch_url_text

router = APIRouter()


@router.post("/products/{product_id}/sources", response_model=ProductSourceOut, status_code=201)
def upload_source(
    product_id: UUID,
    file: UploadFile = File(...),
    reference: str | None = Form(default=None),
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(get_auth_context),
) -> ProductSourceOut:
    product = product_crud.get_product(db, product_id, auth.workspace_id)
    if product is None:
        raise HTTPException(status_code=404, detail="商品不存在")

    data = file.file.read(settings.max_upload_bytes + 1)
    if not data:
        raise HTTPException(status_code=400, detail="文件为空")
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="文件超过大小限制")

    filename = Path(file.filename or "upload.bin").name
    suffix = Path(filename).suffix.lower()
    try:
        if data.startswith(b"%PDF-") and suffix == ".pdf":
            text, page_count = extract_pdf_text(data)
            source_type = ProductSourceType.pdf
        elif suffix in {".png", ".jpg", ".jpeg", ".webp"}:
            text, page_count = extract_image_text(data), 1
            source_type = ProductSourceType.image
        else:
            raise ValueError("文件内容与支持的 PDF/图片格式不匹配")
        storage_path = save_upload(data, filename)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    source = ProductSource(
        product_id=product.id,
        type=source_type,
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
def read_source_text(source_id: UUID, db: Session = Depends(get_db), auth: AuthContext = Depends(get_auth_context)) -> SourceTextOut:
    source = db.get(ProductSource, source_id)
    if source is None or source.product.workspace_id != auth.workspace_id:
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
    auth: AuthContext = Depends(get_auth_context),
) -> ProductSourceOut:
    product = product_crud.get_product(db, product_id, auth.workspace_id)
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
