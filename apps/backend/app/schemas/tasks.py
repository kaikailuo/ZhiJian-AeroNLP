from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel


class TaskItem(BaseModel):
    id: int
    task_type: str
    status: str
    detail: str
    created_at: datetime


class TaskListResponse(BaseModel):
    items: List[TaskItem]
