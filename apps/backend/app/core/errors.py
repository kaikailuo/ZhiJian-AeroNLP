from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from app.core.logging import get_request_id


def build_error_response(code: str, message: str) -> JSONResponse:
    trace_id = get_request_id() or "-"
    return JSONResponse(
        status_code=400 if code == "bad_request" else 500,
        content={"code": code, "message": message, "trace_id": trace_id},
    )


def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    trace_id = get_request_id() or "-"
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": "http_error", "message": exc.detail, "trace_id": trace_id},
    )


def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    trace_id = get_request_id() or "-"
    return JSONResponse(
        status_code=500,
        content={"code": "internal_error", "message": str(exc), "trace_id": trace_id},
    )
