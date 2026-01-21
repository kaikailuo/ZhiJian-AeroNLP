import uuid
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api import router as api_router
from app.api.routes import health
from app.core.config import settings
from app.core.errors import http_exception_handler, unhandled_exception_handler
from app.core.logging import set_request_id, setup_logging
from app.db.session import init_db


def create_app() -> FastAPI:
    setup_logging(settings.log_level)
    app = FastAPI(title=settings.app_name, openapi_url=f"{settings.api_prefix}/openapi.json")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"] ,
        allow_headers=["*"] ,
    )

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request_id = request.headers.get(settings.request_id_header, str(uuid.uuid4()))
        set_request_id(request_id)
        response = await call_next(request)
        response.headers[settings.request_id_header] = request_id
        return response

    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    @app.on_event("startup")
    def on_startup():
        init_db()

    app.include_router(health.router)
    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()
