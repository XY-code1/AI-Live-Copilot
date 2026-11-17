import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import AuthContext, get_auth_context
from app.db.session import get_db
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMembership
from app.schemas.user import AuthResponse, UserCreate, UserLogin, UserOut
from app.services.auth import (
    create_access_token,
    hash_password,
    verify_password,
)

router = APIRouter()


def _to_response(user: User) -> AuthResponse:
    return AuthResponse(
        token=create_access_token(str(user.id)),
        user=UserOut.model_validate(user),
    )


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> AuthResponse:
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing is not None:
        raise HTTPException(status_code=409, detail="该邮箱已注册")
    workspace = Workspace(name=f"{payload.email} 的工作区", owner_user_id="pending")
    db.add(workspace)
    db.flush()
    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        name=payload.name or payload.email.split("@")[0],
        workspace_id=workspace.id,
    )
    db.add(user)
    db.flush()
    workspace.owner_user_id = str(user.id)
    db.add(
        WorkspaceMembership(
            workspace_id=workspace.id, user_id=str(user.id), role="owner"
        )
    )
    db.commit()
    db.refresh(user)
    return _to_response(user)


@router.post("/login", response_model=AuthResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> AuthResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    return _to_response(user)


@router.get("/me", response_model=UserOut)
def me(db: Session = Depends(get_db), auth: AuthContext = Depends(get_auth_context)) -> UserOut:
    user = db.get(User, uuid.UUID(auth.user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    return UserOut.model_validate(user)
