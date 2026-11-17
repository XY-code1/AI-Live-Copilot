from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str:
    payload = jwt.decode(
        token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
    )
    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        raise ValueError("token missing subject")
    return subject


def new_workspace_bundle(db, user_id: str, email: str):
    """Create a user with its own workspace + owner membership."""
    from app.models.workspace import Workspace, WorkspaceMembership

    workspace = Workspace(name=f"{email} 的工作区", owner_user_id=user_id)
    db.add(workspace)
    db.flush()
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=user_id, role="owner"
    )
    db.add(membership)
    return workspace
