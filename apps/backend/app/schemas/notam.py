from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel


class NotamParseRequest(BaseModel):
    raw_text: str


class NotamParseResponse(BaseModel):
    record_id: int
    parse_fields: Dict[str, Any]


class NotamRecordOut(BaseModel):
    id: int
    raw_text: str
    parsed_json: Dict[str, Any]
    created_at: datetime


class NotamHistoryResponse(BaseModel):
    items: List[NotamRecordOut]
