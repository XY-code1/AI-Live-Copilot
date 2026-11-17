import hashlib
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.auth import AuthContext, get_auth_context
from app.core.config import settings
from app.core.parsing import parser_version
from app.core.storage import save_snapshot, save_upload
from app.crud import ingestion as ingestion_crud
from app.crud import product as product_crud
from app.db.session import get_db
from app.models.product import ProductSource, ProductSourceStatus, ProductSourceType
from app.models.segment import SourceSegment
from app.schemas.product import ProductSourceOut
from app.schemas.segment import SegmentOut
from app.schemas.source import SourceTextOut, UrlSourceCreate, UrlSourcePreview
from app.services.ocr import extract_image_text
from app.services.pdf import extract_pdf_text
from app.services.segments import image_segments, pdf_segments, url_segments
from app.services.sufficiency import assess as assess_sufficiency
from app.services.url import (
    fetch_url_page,
    fetch_url_text,
    infer_product_fields,
    normalize_shared_url,
)

router = APIRouter()


@router.post("/sources/url/preview", response_model=UrlSourcePreview)
def preview_url_source(
    payload: UrlSourceCreate,
    auth: AuthContext = Depends(get_auth_context),
) -> UrlSourcePreview:
    del auth
    try:
        url = normalize_shared_url(payload.url)
        title, _ = fetch_url_text(url)
        fields = infer_product_fields(payload.url, title)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return UrlSourcePreview(url=url, **fields)


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
    is_snapshot = suffix in {".html", ".htm", ".txt"}
    kind = "pdf" if (data.startswith(b"%PDF-") and suffix == ".pdf") else "image"
    parser = "snapshot" if is_snapshot else parser_version(kind)
    run = ingestion_crud.start_run(
        db,
        product_id=product.id,
        type=kind,
        workspace_id=auth.workspace_id,
        parser=parser,
    )
    try:
        if is_snapshot:
            text = data.decode("utf-8", errors="replace")
            page_count = None
            source_type = ProductSourceType.url
            storage_path = save_upload(data, filename)
        elif kind == "pdf":
            text, page_count = extract_pdf_text(data)
            source_type = ProductSourceType.pdf
            storage_path = save_upload(data, filename)
        elif suffix in {".png", ".jpg", ".jpeg", ".webp"}:
            text, page_count = extract_image_text(data), 1
            source_type = ProductSourceType.image
            storage_path = save_upload(data, filename)
        else:
            raise ValueError("文件内容与支持的 PDF/图片/HTML/TXT 格式不匹配")
    except (ValueError, RuntimeError) as exc:
        ingestion_crud.fail_run(db, run, str(exc))
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    assessment = assess_sufficiency(text, is_url=source_type == ProductSourceType.url)

    source = ProductSource(
        product_id=product.id,
        type=source_type,
        name=filename,
        reference=reference,
        storage_path=storage_path,
        status=ProductSourceStatus.ready,
        content_text=text,
        page_count=page_count,
        content_hash=hashlib.sha256(data).hexdigest(),
        parser=run.parser,
        sufficiency=assessment.sufficiency,
    )
    db.add(source)
    db.flush()
    if source_type == ProductSourceType.pdf:
        segments = pdf_segments(data)
    elif is_snapshot:
        segments = url_segments(text) if suffix in {".html", ".htm"} else [
            __import__("app.services.segments", fromlist=["SegmentDraft"]).SegmentDraft(
                kind="page", position=0, content=text
            )
        ]
    else:
        segments = image_segments(text)
    for draft in segments:
        db.add(
            SourceSegment(
                source_id=source.id,
                kind=draft.kind,
                page_no=draft.page_no,
                position=draft.position,
                content=draft.content,
                structured=draft.structured,
            )
        )
    ingestion_crud.finish_run(
        db,
        run,
        source_id=source.id,
        content_hash=source.content_hash,
        snapshot_path=storage_path,
    )
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
        run=source.run,
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

    run = ingestion_crud.start_run(
        db,
        product_id=product.id,
        type="url",
        workspace_id=auth.workspace_id,
        parser=parser_version("url"),
    )
    try:
        url = normalize_shared_url(payload.url)
        title, text, final_url, redirects, html = fetch_url_page(url)
        if payload.url.strip() != url:
            text = f"分享文案：\n{payload.url.strip()}\n\n网页内容：\n{text}"
        snapshot_path = save_snapshot(html.encode("utf-8", errors="replace"), ".html")
    except ValueError as exc:
        ingestion_crud.fail_run(db, run, str(exc))
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    digest = hashlib.sha256(html.encode("utf-8", errors="replace")).hexdigest()
    url_assessment = assess_sufficiency(text, is_url=True)
    source = ProductSource(
        product_id=product.id,
        type=ProductSourceType.url,
        name=title,
        reference=url,
        storage_path=url,
        status=ProductSourceStatus.ready,
        content_text=text,
        page_count=None,
        content_hash=digest,
        parser=run.parser,
        sufficiency=url_assessment.sufficiency,
    )
    db.add(source)
    db.flush()
    for draft in url_segments(html):
        db.add(
            SourceSegment(
                source_id=source.id,
                kind=draft.kind,
                page_no=draft.page_no,
                position=draft.position,
                content=draft.content,
                structured=draft.structured,
            )
        )
    ingestion_crud.finish_run(
        db,
        run,
        source_id=source.id,
        content_hash=digest,
        snapshot_path=snapshot_path,
        final_url=final_url,
        redirect_chain=redirects,
    )
    db.commit()
    db.refresh(source)
    return source


@router.get("/sources/{source_id}/segments", response_model=list[SegmentOut])
def list_segments(
    source_id: UUID, db: Session = Depends(get_db), auth: AuthContext = Depends(get_auth_context)
) -> list[SegmentOut]:
    source = db.get(ProductSource, source_id)
    if source is None or source.product.workspace_id != auth.workspace_id:
        raise HTTPException(status_code=404, detail="资料不存在")
    return sorted(source.segments, key=lambda segment: segment.position)
