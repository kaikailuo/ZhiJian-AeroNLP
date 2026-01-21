import time
from typing import Dict, List

from fastapi import HTTPException, Request

from app.core.config import settings


class MemoryRateLimiter:
    def __init__(self) -> None:
        self._hits: Dict[str, List[float]] = {}

    def check(self, key: str, limit: int, window_seconds: int) -> None:
        now = time.time()
        window_start = now - window_seconds
        timestamps = [ts for ts in self._hits.get(key, []) if ts >= window_start]
        if len(timestamps) >= limit:
            raise HTTPException(status_code=429, detail="rate limit exceeded")
        timestamps.append(now)
        self._hits[key] = timestamps


limiter = MemoryRateLimiter()


def rate_limit(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    limiter.check(client_ip, settings.rate_limit_requests, settings.rate_limit_window_seconds)
