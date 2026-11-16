from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import comparison as crud
from app.db.session import get_db
from app.schemas.comparison import (
    ComparisonCreate,
    ComparisonOut,
    DifferenceCreate,
    DifferenceOut,
)

router = APIRouter()


@router.get("", response_model=list[ComparisonOut])
def list_all_comparisons(db: Session = Depends(get_db)) -> list[ComparisonOut]:
    return crud.list_all_comparisons(db)


@router.post("", response_model=ComparisonOut, status_code=201)
def create_comparison(payload: ComparisonCreate, db: Session = Depends(get_db)) -> ComparisonOut:
    return crud.create_comparison(db, payload)


@router.get("/{comparison_id}", response_model=ComparisonOut)
def get_comparison(comparison_id: UUID, db: Session = Depends(get_db)) -> ComparisonOut:
    comparison = crud.get_comparison(db, comparison_id)
    if comparison is None:
        raise HTTPException(status_code=404, detail="对比不存在")
    return comparison


@router.delete("/{comparison_id}", status_code=204)
def delete_comparison(comparison_id: UUID, db: Session = Depends(get_db)) -> None:
    comparison = crud.get_comparison(db, comparison_id)
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
) -> DifferenceOut:
    comparison = crud.get_comparison(db, comparison_id)
    if comparison is None:
        raise HTTPException(status_code=404, detail="对比不存在")
    return crud.add_difference(db, comparison, payload)


@router.delete("/differences/{difference_id}", status_code=204)
def delete_difference(difference_id: UUID, db: Session = Depends(get_db)) -> None:
    difference = crud.get_difference(db, difference_id)
    if difference is None:
        raise HTTPException(status_code=404, detail="差异项不存在")
    crud.delete_difference(db, difference)
