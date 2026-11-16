from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import comparison as comparison_crud
from app.crud import product as product_crud
from app.crud import script as script_crud
from app.db.session import get_db
from app.models.script import ScriptSection
from app.schemas.script import (
    ScriptGenerateRequest,
    ScriptOut,
    ScriptVersionCreate,
    SectionRewriteOutput,
    SectionRewriteRequest,
)
from app.services.script_generation import generate_script
from app.services.script_rewrite import rewrite_section

router = APIRouter()


@router.post(
    "/products/{product_id}/scripts/generate",
    response_model=ScriptOut,
    status_code=201,
)
def generate(
    product_id: UUID,
    payload: ScriptGenerateRequest,
    db: Session = Depends(get_db),
) -> ScriptOut:
    product = product_crud.get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="商品不存在")

    comparison = None
    if payload.comparison_id is not None:
        comparison = comparison_crud.get_comparison(db, payload.comparison_id)
        if comparison is None or comparison.product_id != product.id:
            raise HTTPException(status_code=400, detail="对比不属于该商品")

    try:
        return generate_script(db, product, payload, comparison)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/scripts", response_model=list[ScriptOut])
def list_scripts(product_id: UUID | None = None, db: Session = Depends(get_db)) -> list[ScriptOut]:
    return script_crud.list_scripts(db, product_id)


@router.get("/scripts/{script_id}", response_model=ScriptOut)
def get_script(script_id: UUID, db: Session = Depends(get_db)) -> ScriptOut:
    script = script_crud.get_script(db, script_id)
    if script is None:
        raise HTTPException(status_code=404, detail="话术不存在")
    return script


@router.get("/scripts/{script_id}/versions", response_model=list[ScriptOut])
def list_versions(script_id: UUID, db: Session = Depends(get_db)) -> list[ScriptOut]:
    script = script_crud.get_script(db, script_id)
    if script is None:
        raise HTTPException(status_code=404, detail="话术不存在")
    return script_crud.list_versions(db, script.series_id)


@router.post("/scripts/{script_id}/versions", response_model=ScriptOut, status_code=201)
def save_version(
    script_id: UUID,
    payload: ScriptVersionCreate,
    db: Session = Depends(get_db),
) -> ScriptOut:
    script = script_crud.get_script(db, script_id)
    if script is None:
        raise HTTPException(status_code=404, detail="话术不存在")
    return script_crud.save_version(db, script, payload)


@router.delete("/scripts/{script_id}", status_code=204)
def delete_script(script_id: UUID, db: Session = Depends(get_db)) -> None:
    script = script_crud.get_script(db, script_id)
    if script is None:
        raise HTTPException(status_code=404, detail="话术不存在")
    script_crud.delete_script_series(db, script)


@router.post(
    "/scripts/{script_id}/sections/{section_id}/rewrite",
    response_model=SectionRewriteOutput,
)
def rewrite_section_endpoint(
    script_id: UUID,
    section_id: UUID,
    payload: SectionRewriteRequest,
    db: Session = Depends(get_db),
) -> SectionRewriteOutput:
    script = script_crud.get_script(db, script_id)
    if script is None:
        raise HTTPException(status_code=404, detail="话术不存在")
    section = db.get(ScriptSection, section_id)
    if section is None or section.script_id != script.id:
        raise HTTPException(status_code=404, detail="段落不存在")
    product = product_crud.get_product(db, script.product_id)
    try:
        content = rewrite_section(db, script, section, payload.instruction, product)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return SectionRewriteOutput(content=content)
