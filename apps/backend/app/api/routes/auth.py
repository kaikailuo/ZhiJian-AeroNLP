from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    is_refresh_token,
    verify_password,
)
from app.db.models import RefreshToken, User
from app.db.session import get_session
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, UserOut
from app.services.audit import log_action

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
def register(payload: RegisterRequest, session: Session = Depends(get_session)) -> UserOut:
    existing = session.exec(select(User).where(User.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="email already registered")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    log_action(session, "register", f"User {user.email} registered", user.id)
    return UserOut(id=user.id, email=user.email, role=user.role, created_at=user.created_at)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, session: Session = Depends(get_session)) -> TokenResponse:
    user = session.exec(select(User).where(User.email == payload.email)).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="invalid credentials")

    access_token = create_access_token(str(user.id), user.role)
    refresh_token = create_refresh_token(str(user.id))
    expires_at = datetime.utcnow() + timedelta(days=settings.refresh_token_days)

    token_record = RefreshToken(user_id=user.id, token=refresh_token, expires_at=expires_at)
    session.add(token_record)
    session.commit()

    log_action(session, "login", f"User {user.email} logged in", user.id)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_minutes * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, session: Session = Depends(get_session)) -> TokenResponse:
    record = session.exec(select(RefreshToken).where(RefreshToken.token == payload.refresh_token)).first()
    if not record or record.revoked:
        raise HTTPException(status_code=401, detail="invalid refresh token")
    try:
        decoded = decode_token(payload.refresh_token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="invalid refresh token") from exc

    if not is_refresh_token(decoded):
        raise HTTPException(status_code=401, detail="invalid refresh token")

    user = session.exec(select(User).where(User.id == record.user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="user not found")

    record.revoked = True
    session.add(record)
    session.commit()

    access_token = create_access_token(str(user.id), user.role)
    refresh_token = create_refresh_token(str(user.id))
    expires_at = datetime.utcnow() + timedelta(days=settings.refresh_token_days)

    new_record = RefreshToken(user_id=user.id, token=refresh_token, expires_at=expires_at)
    session.add(new_record)
    session.commit()

    log_action(session, "refresh", f"Token refreshed for {user.email}", user.id)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_minutes * 60,
    )


@router.post("/logout")
def logout(
    payload: RefreshRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    record = session.exec(select(RefreshToken).where(RefreshToken.token == payload.refresh_token)).first()
    if record:
        record.revoked = True
        session.add(record)
        session.commit()
    log_action(session, "logout", f"User {current_user.email} logged out", current_user.id)
    return {"message": "logged out"}
