from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import AuthContext, get_auth_context
from app.crud import comparison as crud
from app.db.session import get_db
from app.schemas.comparison import (
    CompetitorCreate,
    CompetitorOut,
    CompetitorUpdate,
)

router = APIRouter()


@router.get("", response_model=list[CompetitorOut])
def list_competitors(db: Session = Depends(get_db), auth: AuthContext = Depends(get_auth_context)) -> list[CompetitorOut]:
    return crud.list_competitors(db, auth.workspace_id)


@router.post("", response_model=CompetitorOut, status_code=201)
def create_competitor(payload: CompetitorCreate, db: Session = Depends(get_db), auth: AuthContext = Depends(get_auth_context)) -> CompetitorOut:
    return crud.create_competitor(db, payload, auth.workspace_id)


@router.patch("/{competitor_id}", response_model=CompetitorOut)
def update_competitor(
    competitor_id: UUID, payload: CompetitorUpdate, db: Session = Depends(get_db), auth: AuthContext = Depends(get_auth_context)
) -> CompetitorOut:
    competitor = crud.get_competitor(db, competitor_id, auth.workspace_id)
    if competitor is None:
        raise HTTPException(status_code=404, detail="竞品不存在")
    return crud.update_competitor(db, competitor, payload)


@router.delete("/{competitor_id}", status_code=204)
def delete_competitor(competitor_id: UUID, db: Session = Depends(get_db), auth: AuthContext = Depends(get_auth_context)) -> None:
    competitor = crud.get_competitor(db, competitor_id, auth.workspace_id)
    if competitor is None:
        raise HTTPException(status_code=404, detail="竞品不存在")
    crud.delete_competitor(db, competitor)
