from fastapi import APIRouter, Depends

from app.api.deps import require_permission
from app.db.models import User

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.get("", response_model=dict)
def list_keys(current_user: User = Depends(require_permission("api-keys"))):
    return {"items": [], "message": "api keys placeholder"}
