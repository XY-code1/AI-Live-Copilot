from fastapi import APIRouter, Depends

from app.core.auth import AuthContext, get_auth_context

router = APIRouter()


@router.get("/me")
def me(auth: AuthContext = Depends(get_auth_context)) -> dict[str, str]:
    return {"user_id": auth.user_id, "workspace_id": str(auth.workspace_id)}

