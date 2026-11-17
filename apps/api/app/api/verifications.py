from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import AuthContext, get_auth_context
from app.crud import script as script_crud
from app.db.session import get_db
from app.models.verification import ScriptVerification
from app.schemas.verification import ScriptVerificationOut
from app.services.verification import verify_script

router = APIRouter()


@router.post("/scripts/{script_id}/verify", response_model=ScriptVerificationOut, status_code=201)
def verify(script_id: UUID, db: Session = Depends(get_db), auth: AuthContext = Depends(get_auth_context)) -> ScriptVerificationOut:
    script = script_crud.get_script(db, script_id, auth.workspace_id)
    if script is None:
        raise HTTPException(status_code=404, detail="话术不存在")
    try:
        return verify_script(db, script)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get(
    "/scripts/{script_id}/verifications", response_model=list[ScriptVerificationOut]
)
def list_verifications(
    script_id: UUID, db: Session = Depends(get_db), auth: AuthContext = Depends(get_auth_context)
) -> list[ScriptVerificationOut]:
    script = script_crud.get_script(db, script_id, auth.workspace_id)
    if script is None:
        raise HTTPException(status_code=404, detail="话术不存在")
    statement = (
        select(ScriptVerification)
        .where(ScriptVerification.script_id == script_id)
        .order_by(ScriptVerification.created_at.desc())
    )
    return list(db.scalars(statement).all())
