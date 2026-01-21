from __future__ import annotations

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    code: str
    message: str
    trace_id: str


class MessageResponse(BaseModel):
    message: str
