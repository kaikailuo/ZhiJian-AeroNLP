import json

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.api.deps import require_permission
from app.core.rate_limit import rate_limit
from app.db.models import NotamRecord, User
from app.db.session import get_session
from app.schemas.notam import NotamHistoryResponse, NotamParseRequest, NotamParseResponse, NotamRecordOut
from app.services.audit import log_action
from app.services.notam_parser import parse_notam_text

router = APIRouter(prefix="/notam", tags=["notam"], dependencies=[Depends(rate_limit)])


@router.post("/parse", response_model=NotamParseResponse)
def parse_notam(
    payload: NotamParseRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("notam")),
) -> NotamParseResponse:
    parsed = parse_notam_text(payload.raw_text)
    record = NotamRecord(
        raw_text=payload.raw_text,
        parsed_json=json.dumps(parsed),
        created_by=current_user.id,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    log_action(session, "parse", f"Parsed NOTAM record {record.id}", current_user.id)
    return NotamParseResponse(record_id=record.id, parse_fields=parsed)


@router.get("/history", response_model=NotamHistoryResponse)
def history(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("notam")),
) -> NotamHistoryResponse:
    records = session.exec(
        select(NotamRecord).where(NotamRecord.created_by == current_user.id).order_by(NotamRecord.id.desc())
    ).all()
    items = [
        NotamRecordOut(
            id=rec.id,
            raw_text=rec.raw_text,
            parsed_json=json.loads(rec.parsed_json),
            created_at=rec.created_at,
        )
        for rec in records
    ]
    return NotamHistoryResponse(items=items)
