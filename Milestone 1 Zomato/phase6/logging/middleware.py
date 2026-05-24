"""FastAPI middleware for request/response logging and latency tracking."""

from __future__ import annotations

import time
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("zomato.api")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every API request with method, path, status code, and latency."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "%s %s → %s (%.1f ms)",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )

        # Add latency header for observability
        response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.1f}"
        return response
