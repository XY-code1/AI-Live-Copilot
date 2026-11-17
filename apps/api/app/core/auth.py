import uuid
from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.workspace import Workspace, WorkspaceMembership
from app.services.auth import decode_access_token


@dataclass(frozen=True, slots=True)
class AuthContext:
    user_id: str
    workspace_id: uuid.UUID


def _token_from_request(request: Request) -> str:
    authorization = request.headers.get("authorization", "")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请先登录")
    return authorization.removeprefix("Bearer ").strip()


def _password_user_id(request: Request) -> str:
    token = _token_from_request(request)
    try:
        return decode_access_token(token)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录凭证无效") from exc


def get_auth_context(
    request: Request,
    db: Session = Depends(get_db),
    x_dev_user: str | None = Header(default=None),
    x_workspace_id: uuid.UUID | None = Header(default=None),
) -> AuthContext:
    if settings.auth_mode == "dev":
        user_id = x_dev_user or "dev-user"
    else:
        user_id = _password_user_id(request)

    statement = select(WorkspaceMembership).where(WorkspaceMembership.user_id == user_id)
    if x_workspace_id is not None:
        statement = statement.where(WorkspaceMembership.workspace_id == x_workspace_id)
    membership = db.scalar(statement.order_by(WorkspaceMembership.created_at.asc()))
    if membership is None:
        if x_workspace_id is not None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问该工作区")
        if settings.auth_mode == "dev":
            workspace = Workspace(name="开发工作区", owner_user_id=user_id)
            db.add(workspace)
            db.flush()
            membership = WorkspaceMembership(
                workspace_id=workspace.id, user_id=user_id, role="owner"
            )
            db.add(membership)
            db.commit()
            db.refresh(membership)
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="用户尚未加入工作区")
    return AuthContext(user_id=user_id, workspace_id=membership.workspace_id)
