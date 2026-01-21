from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.api.deps import require_permission
from app.db.models import BackgroundTask, User
from app.db.session import get_session
from app.schemas.tasks import TaskItem, TaskListResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=TaskListResponse)
def list_tasks(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("tasks")),
) -> TaskListResponse:
    tasks = session.exec(select(BackgroundTask).order_by(BackgroundTask.id.desc())).all()
    items = [
        TaskItem(
            id=task.id,
            task_type=task.task_type,
            status=task.status,
            detail=task.detail,
            created_at=task.created_at,
        )
        for task in tasks
    ]
    return TaskListResponse(items=items)
