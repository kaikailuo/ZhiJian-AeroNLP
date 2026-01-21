from sqlmodel import Session

from app.db.models import AuditLog


def log_action(session: Session, action: str, detail: str, user_id: int | None = None) -> AuditLog:
    log = AuditLog(user_id=user_id, action=action, detail=detail)
    session.add(log)
    session.commit()
    session.refresh(log)
    return log
