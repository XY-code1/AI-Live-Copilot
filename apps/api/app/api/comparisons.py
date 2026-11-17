from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import AuthContext, get_auth_context
from app.crud import comparison as crud
from app.db.session import get_db
from app.models.product import Product
from app.schemas.comparison import (
    ComparisonCreate,
    ComparisonOut,
    DifferenceCreate,
    DifferenceOut,
)
from app.services.comparison_generation import generate_comparison_differences

router = APIRouter()


@router.get("", response_model=list[ComparisonOut])
def list_all_comparisons(db: Session = Depends(get_db), auth: AuthContext = Depends(get_auth_context)) -> list[ComparisonOut]:
    return crud.list_all_comparisons(db, auth.workspace_id)


@router.post("", response_model=ComparisonOut, status_code=201)
def create_comparison(payload: ComparisonCreate, db: Session = Depends(get_db), auth: AuthContext = Depends(get_auth_context)) -> ComparisonOut:
    product = db.get(Product, payload.product_id)
    competitor = crud.get_competitor(db, payload.competitor_id, auth.workspace_id)
    if product is None or product.workspace_id != auth.workspace_id or competitor is None:
        raise HTTPException(status_code=404, detail="商品或竞品不存在")
    return crud.create_comparison(db, payload, auth.workspace_id)


@router.get("/{comparison_id}", response_model=ComparisonOut)
def get_comparison(comparison_id: UUID, db: Session = Depends(get_db), auth: AuthContext = Depends(get_auth_context)) -> ComparisonOut:
    comparison = crud.get_comparison(db, comparison_id, auth.workspace_id)
    if comparison is None:
        raise HTTPException(status_code=404, detail="对比不存在")
    return comparison


@router.delete("/{comparison_id}", status_code=204)
def delete_comparison(comparison_id: UUID, db: Session = Depends(get_db), auth: AuthContext = Depends(get_auth_context)) -> None:
    comparison = crud.get_comparison(db, comparison_id, auth.workspace_id)
    if comparison is None:
        raise HTTPException(status_code=404, detail="对比不存在")
    crud.delete_comparison(db, comparison)


@router.post(
    "/{comparison_id}/differences",
    response_model=DifferenceOut,
    status_code=201,
)
def add_difference(
    comparison_id: UUID,
    payload: DifferenceCreate,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(get_auth_context),
) -> DifferenceOut:
    comparison = crud.get_comparison(db, comparison_id, auth.workspace_id)
    if comparison is None:
        raise HTTPException(status_code=404, detail="对比不存在")
    return crud.add_difference(db, comparison, payload)


@router.delete("/differences/{difference_id}", status_code=204)
def delete_difference(difference_id: UUID, db: Session = Depends(get_db), auth: AuthContext = Depends(get_auth_context)) -> None:
    difference = crud.get_difference(db, difference_id)
    if difference is None or difference.comparison.workspace_id != auth.workspace_id:
        raise HTTPException(status_code=404, detail="差异项不存在")
    crud.delete_difference(db, difference)


@router.post("/{comparison_id}/generate", response_model=ComparisonOut)
def generate_comparison(comparison_id: UUID, db: Session = Depends(get_db), auth: AuthContext = Depends(get_auth_context)) -> ComparisonOut:
    comparison = crud.get_comparison(db, comparison_id, auth.workspace_id)
    if comparison is None:
        raise HTTPException(status_code=404, detail="对比不存在")
    try:
        generate_comparison_differences(db, comparison)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    db.refresh(comparison)
    return comparison
