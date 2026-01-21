from __future__ import annotations

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from app.core.rbac import has_permission
from app.core.security import decode_token
from app.db.models import User
from app.db.session import get_session


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(session: Session = Depends(get_session), token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = decode_token(token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="invalid token") from exc

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="invalid token")

    user = session.exec(select(User).where(User.id == int(user_id))).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="user not found")
    return user


def require_permission(resource: str):
    def checker(user: User = Depends(get_current_user)) -> User:
        if not has_permission(user.role, resource):
            raise HTTPException(status_code=403, detail="insufficient permissions")
        return user

    return checker
