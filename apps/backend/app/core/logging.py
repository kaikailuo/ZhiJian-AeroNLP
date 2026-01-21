import logging
import sys
from contextvars import ContextVar
from typing import Optional

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


def set_request_id(request_id: Optional[str]) -> None:
    request_id_var.set(request_id)


def get_request_id() -> Optional[str]:
    return request_id_var.get()


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id() or "-"
        return True


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(request_id)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    logging.getLogger().addFilter(RequestIdFilter())
