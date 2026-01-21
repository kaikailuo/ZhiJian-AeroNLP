from sqlmodel import SQLModel, create_engine, Session

from app.core.config import settings


def create_db_engine():
    connect_args = {}
    if settings.database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    return create_engine(settings.database_url, echo=False, connect_args=connect_args)


engine = create_db_engine()


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
