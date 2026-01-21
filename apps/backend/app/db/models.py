from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    role: str = Field(default="user")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RefreshToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    token: str
    revoked: bool = Field(default=False)
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, index=True)
    action: str
    detail: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class NotamRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    raw_text: str
    parsed_json: str
    created_by: Optional[int] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BackgroundTask(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_type: str
    status: str = Field(default="pending")
    detail: str = Field(default="")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ApiKey(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int
    name: str
    key_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
