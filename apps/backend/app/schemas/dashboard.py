from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel


class AlertItem(BaseModel):
    id: int
    level: str
    message: str
    created_at: str


class DashboardSummary(BaseModel):
    recent_notam_count: int
    active_alerts: int
    pending_tasks: int
    parse_success_rate: float
    system_status: Dict[str, str]
    alerts: List[AlertItem]
