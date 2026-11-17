import uuid
from dataclasses import dataclass

import jwt
from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.workspace import Workspace, WorkspaceMembership


@dataclass(frozen=True, slots=True)
class AuthContext:
    user_id: str
    workspace_id: uuid.UUID


def _clerk_user_id(request: Request) -> str:
    authorization = request.headers.get("authorization", "")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请先登录")
    token = authorization.removeprefix("Bearer ").strip()
    try:
        if settings.clerk_jwt_key:
            payload = jwt.decode(
                token,
                settings.clerk_jwt_key.replace("\\n", "\n"),
                algorithms=["RS256"],
                issuer=settings.clerk_issuer or None,
                audience=settings.clerk_audience or None,
                options={"verify_aud": bool(settings.clerk_audience)},
            )
        elif settings.clerk_jwks_url:
            signing_key = jwt.PyJWKClient(settings.clerk_jwks_url).get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                issuer=settings.clerk_issuer or None,
                audience=settings.clerk_audience or None,
                options={"verify_aud": bool(settings.clerk_audience)},
            )
        else:
            raise RuntimeError("Clerk JWT verification is not configured")
    except (jwt.PyJWTError, RuntimeError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录凭证无效") from exc
    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录凭证缺少用户标识")
    return subject


def get_auth_context(
    request: Request,
    db: Session = Depends(get_db),
    x_dev_user: str | None = Header(default=None),
    x_workspace_id: uuid.UUID | None = Header(default=None),
) -> AuthContext:
    if settings.auth_mode == "dev":
        user_id = x_dev_user or "dev-user"
    else:
        user_id = _clerk_user_id(request)

    statement = select(WorkspaceMembership).where(WorkspaceMembership.user_id == user_id)
    if x_workspace_id is not None:
        statement = statement.where(WorkspaceMembership.workspace_id == x_workspace_id)
    membership = db.scalar(statement.order_by(WorkspaceMembership.created_at.asc()))
    if membership is None:
        if x_workspace_id is not None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问该工作区")
        workspace = Workspace(
            name="开发工作区" if settings.auth_mode == "dev" else "我的工作区",
            owner_user_id=user_id,
        )
        db.add(workspace)
        db.flush()
        membership = WorkspaceMembership(workspace_id=workspace.id, user_id=user_id, role="owner")
        db.add(membership)
        db.commit()
        db.refresh(membership)
    return AuthContext(user_id=user_id, workspace_id=membership.workspace_id)

