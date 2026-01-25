from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import require_permission
from app.db.models import User
from app.services.training_service import MockTrainingService

router = APIRouter(prefix="/training", tags=["training"])

class TrainingSubmission(BaseModel):
    exercise_id: str
    user_answer: Any

class TrainingResponse(BaseModel):
    status: str
    message: str
    data: Any = None

@router.post("/submit", response_model=TrainingResponse)
def submit_exercise(
    submission: TrainingSubmission,
    current_user: User = Depends(require_permission("notam")), # Re-using permissions for simplicity
) -> TrainingResponse:
    """
    Placeholder endpoint for submitting training exercises.
    """
    service = MockTrainingService()
    result = service.evaluate(submission.exercise_id, submission.user_answer)
    
    return TrainingResponse(
        status="success",
        message="已收到请求，当前为占位回应",
        data={
            "submission_received": submission.user_answer,
            "backend_note": result
        }
    )
