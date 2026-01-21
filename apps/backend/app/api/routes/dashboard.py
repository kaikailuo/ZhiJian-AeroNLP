from datetime import datetime

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.api.deps import require_permission
from app.db.models import BackgroundTask, NotamRecord, User
from app.db.session import get_session
from app.schemas.dashboard import AlertItem, DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def summary(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("dashboard")),
) -> DashboardSummary:
    notam_count = session.exec(select(NotamRecord)).all()
    task_count = session.exec(select(BackgroundTask)).all()
    alerts = [
        AlertItem(
            id=1,
            level="warning",
            message="Runway closure keyword detected in last hour",
            created_at=datetime.utcnow().isoformat() + "Z",
        )
    ]
    return DashboardSummary(
        recent_notam_count=len(notam_count),
        active_alerts=len(alerts),
        pending_tasks=len([t for t in task_count if t.status == "pending"]),
        parse_success_rate=0.92,
        system_status={"db": "ok", "parser": "ok", "queue": "pending"},
        alerts=alerts,
    )
